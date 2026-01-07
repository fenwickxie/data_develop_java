import os
import can
import cantools
from typing import List, Dict, Any, Optional, Tuple, TypeAlias, Union
from cantools.database import Database
from tqdm import tqdm
from multiprocessing import Pool, cpu_count
import numpy as np
from collections import defaultdict
import yaml
from pathlib import Path
import yaml
from pathlib import Path
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
# 尝试导入numba用于JIT加速
try:
    from numba import jit

    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False

    # 如果numba不可用，使用空装饰器
    def jit(*args, **kwargs):
        def decorator(func):
            return func

        return decorator if args and callable(args[0]) else decorator


StringPathLike: TypeAlias = Union[str, os.PathLike]

# if platform.system() == "Windows":
#     ENCODING = "gbk"
# else:
ENCODING = "utf-8"

# 大文件阈值（单位：字节）
LARGE_FILE_THRESHOLD = 500 * 1024 * 1024  # 500MB
VERY_LARGE_FILE_THRESHOLD = 1024 * 1024 * 1024  # 1GB


def load_config_from_yaml(yaml_path: StringPathLike) -> Dict[str, Any]:
    """
    从YAML文件加载配置

    Args:
        yaml_path: YAML配置文件路径

    Returns:
        配置字典
    """
    yaml_path = Path(yaml_path)
    if not yaml_path.exists():
        raise FileNotFoundError(f"配置文件不存在: {yaml_path}")

    with open(yaml_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # 验证必需的配置项
    required_keys = ["dbc_path", "can_data_path"]
    missing_keys = [key for key in required_keys if key not in config]
    if missing_keys:
        raise ValueError(f"配置文件缺少必需项: {', '.join(missing_keys)}")

    # 设置默认值
    defaults = {
        "output_dir": "./decoded",
        "step": 0.02,
        "save_formats": [".parquet", ".csv"],
        "num_processes": None,
        "batch_size": 1000,
        "use_numba": True,
        "signal_names": None,
        "signal_mapping": None,
        "time_from_zero": False,  # True: 从0开始索引；False: 使用原始时间戳
    }

    # 合并默认值
    for key, default_value in defaults.items():
        if key not in config or config[key] is None:
            config[key] = default_value

    # 处理signal_names（如果是空列表，设为None表示解析所有信号）
    if isinstance(config["signal_names"], list) and len(config["signal_names"]) == 0:
        config["signal_names"] = None

    # 转换save_formats为元组
    if isinstance(config["save_formats"], list):
        config["save_formats"] = tuple(config["save_formats"])

    return config


@jit(nopython=False, cache=True, parallel=False)
def _fast_array_conversion(timestamps_list, values_list):
    """使用Numba加速数组转换（如果可用）"""
    timestamps = np.array(timestamps_list, dtype=np.float64)
    values = np.array(values_list, dtype=np.float64)
    return timestamps, values


def _build_decoder_map(dbc_data: Database) -> Dict[int, Any]:
    """预编译消息ID到解码函数的映射，避免运行时查找。"""
    decoder_map: Dict[int, Any] = {}
    for __msg in getattr(dbc_data, "messages", []):
        decoder_map[__msg.frame_id] = __msg.decode
    return decoder_map


def _process_single_file_wrapper(args):
    """
    多进程wrapper函数，用于处理单个CAN文件。
    必须在模块级别定义以支持multiprocessing序列化。
    优化：批量处理、预分配内存、减少列表追加开销、大文件优化
    """
    import traceback

    (
        dbc_url,
        log_file_path,
        file_type,
        signal_names,
        signal_corr,
        step,
        time_from_zero,
        save_dir,
        save_formats,
    ) = args

    # 检查文件大小
    try:
        file_size = os.path.getsize(log_file_path)
        is_large_file = file_size > LARGE_FILE_THRESHOLD
        is_very_large_file = file_size > VERY_LARGE_FILE_THRESHOLD

        if is_very_large_file:
            print(
                f"\n⚠ 超大文件: {os.path.basename(log_file_path)} ({file_size/1024/1024:.0f}MB)"
            )
            print(f"  使用优化模式处理，请耐心等待...")
    except:
        file_size = 0
        is_large_file = False
        is_very_large_file = False

    # 在子进程中加载DBC文件并预编译解码函数
    with open(dbc_url, "r", encoding=ENCODING) as f:
        dbc_data = cantools.db.load(f, database_format="dbc", strict=False)
    decoder_map = _build_decoder_map(dbc_data)

    # 处理CAN文件
    try:
        # 根据文件类型加载日志数据
        if file_type == "blf":
            log_data = can.BLFReader(log_file_path)
        elif file_type == "asc":
            log_data = can.ASCReader(log_file_path)
        else:
            return None

        # 解码信号 - 使用优化的数据结构与预编译解码函数
        from asammdf import Signal

        decoded: Dict[str, Dict[str, list]] = {}
        signal_names_set = set(signal_names) if signal_names else None

        # 统计信息
        total_msgs = 0
        decoded_msgs = 0
        error_count = 0
        error_types = {}  # 错误类型统计

        # 根据文件大小动态调整批处理大小
        if is_very_large_file:
            batch_size = 500  # 超大文件使用小批次
        elif is_large_file:
            batch_size = 800
        else:
            batch_size = 1000

        # 批量收集消息数据（减少频繁的字典操作）
        temp_data = defaultdict(lambda: {"timestamps": [], "values": []})

        def flush_batch():
            """将累积的列表转为NumPy数组并合并到主存储。"""
            if not temp_data:
                return
            for sig_name, data in temp_data.items():
                if not data["timestamps"]:
                    continue
                t_arr = np.asarray(data["timestamps"], dtype=np.float64)
                v_arr = np.asarray(data["values"], dtype=np.float64)
                bucket = decoded.setdefault(sig_name, {"timestamps": [], "values": []})
                bucket["timestamps"].append(t_arr)
                bucket["values"].append(v_arr)
            temp_data.clear()

        # 批量处理消息
        for __msg in log_data:
            total_msgs += 1
            decoder = decoder_map.get(__msg.arbitration_id)
            if decoder is None:
                error_count += 1
                error_types["UnknownMessage"] = error_types.get("UnknownMessage", 0) + 1
                continue

            try:
                __dec = decoder(__msg.data)
                if not __dec:
                    error_count += 1
                    continue

                decoded_msgs += 1
                for __k, __v in __dec.items():
                    if signal_names_set is None or __k in signal_names_set:
                        value = getattr(__v, "value", __v)
                        entry = temp_data[__k]
                        entry["timestamps"].append(__msg.timestamp)
                        entry["values"].append(value)

                # 每处理batch_size条消息，转换为numpy数组并合并
                if total_msgs % batch_size == 0:
                    flush_batch()

                    # 大文件显示进度
                    if is_very_large_file and total_msgs % 50000 == 0:
                        decode_rate = (
                            decoded_msgs / total_msgs * 100 if total_msgs > 0 else 0
                        )
                        print(
                            f"  已处理 {total_msgs} 条消息 (解码成功率: {decode_rate:.1f}%)..."
                        )

            except Exception as e:
                # 捕获所有解码错误但不中断处理
                error_count += 1
                error_type = type(e).__name__
                error_types[error_type] = error_types.get(error_type, 0) + 1
                continue

        # 处理剩余的批次数据
        flush_batch()

        # 构建Signal对象 - 优化：分批转为数组后再合并，减少中间对象
        sigs = []
        total_data_points = 0

        for __k, __v in decoded.items():
            if len(__v["timestamps"]) > 0:  # 只处理有数据的信号
                timestamps = np.concatenate(__v["timestamps"]) if len(__v["timestamps"]) > 1 else __v["timestamps"][0]
                values = np.concatenate(__v["values"]) if len(__v["values"]) > 1 else __v["values"][0]
                signal_name = signal_corr.get(__k, __k) if signal_corr else __k
                sigs.append(
                    Signal(values, timestamps, name=str(signal_name), encoding="utf-8")
                )
                total_data_points += len(timestamps)

        # 估算内存使用（每个数据点约16字节：8字节timestamp + 8字节value）
        estimated_memory_mb = (total_data_points * 16) / 1024 / 1024

        if is_very_large_file and sigs:
            print(f"  信号数量: {len(sigs)}")
            print(f"  数据点总数: {total_data_points}")
            print(f"  估算内存: {estimated_memory_mb:.1f} MB")

            if estimated_memory_mb > 2000:  # 超过2GB
                print(f"  ⚠ 警告: 估算内存超过 2GB，建议增大step值")

        # 保存结果
        if sigs:
            from asammdf import MDF
            import scipy.io as sio

            try:
                if is_very_large_file:
                    print(f"  正在生成MDF对象...")

                mdf = MDF()
                mdf.append(sigs)

                if is_very_large_file:
                    print(f"  正在转换为DataFrame（这可能需要几分钟）...")
                    # 计算预期的DataFrame大小 - 使用信号的时间跨度
                    try:
                        # 从已解码的信号中获取最大时间戳
                        max_timestamp = max(
                            sig.timestamps[-1]
                            for sig in sigs
                            if len(sig.timestamps) > 0
                        )
                        min_timestamp = min(
                            sig.timestamps[0] for sig in sigs if len(sig.timestamps) > 0
                        )
                        time_span = max_timestamp - min_timestamp
                        expected_rows = (
                            int(time_span / step) if step > 0 else total_data_points
                        )
                        expected_memory_mb = (
                            (expected_rows * len(sigs) * 8) / 1024 / 1024
                        )
                        print(f"  时间跨度: {time_span:.1f}秒")
                        print(f"  预期行数: ~{expected_rows:,}")
                        print(f"  预期内存: ~{expected_memory_mb:.0f} MB")
                    except (ValueError, IndexError):
                        # 如果无法计算时间跨度，跳过这些信息
                        pass

                # 对于超大文件，使用更大的raster步长减少数据点
                if is_very_large_file and step < 0.01:
                    print(f"  ⚠ 超大文件检测，建议使用更大的step值 (>=0.05)")

                df = mdf.to_dataframe(raster=step, time_from_zero=time_from_zero)

                if is_very_large_file:
                    print(f"  DataFrame大小: {len(df)} 行, {len(df.columns)} 列")
                    print(
                        f"  内存占用: {df.memory_usage(deep=True).sum() / 1024 / 1024:.1f} MB"
                    )

            except MemoryError as e:
                return {
                    "file": os.path.basename(log_file_path),
                    "total_msgs": total_msgs,
                    "decoded_msgs": decoded_msgs,
                    "signals": len(sigs),
                    "data_points": total_data_points,
                    "estimated_memory_mb": estimated_memory_mb,
                    "success": False,
                    "error": f"内存不足: 转换DataFrame时内存耗尽 (估算需要 {estimated_memory_mb:.0f}MB). 建议: 1)增大step值至{step*5:.3f}或更大 2)使用signal_names过滤信号 3)减少进程数至1",
                }
            except Exception as e:
                return {
                    "file": os.path.basename(log_file_path),
                    "total_msgs": total_msgs,
                    "success": False,
                    "error": f"DataFrame转换失败: {str(e)}",
                }

            base_filename = os.path.splitext(os.path.basename(log_file_path))[0]

            # 优化：使用更高效的保存参数
            save_methods = {
                ".mat": lambda file_url: sio.savemat(
                    file_url, df.to_dict(orient="list"), do_compression=True  # 启用压缩
                ),
                ".csv": lambda file_url: df.to_csv(
                    file_url,
                    index=True,
                    chunksize=(
                        10000 if not is_very_large_file else 5000
                    ),  # 大文件使用更小块
                ),
                ".parquet": lambda file_url: df.to_parquet(
                    file_url,
                    compression="snappy",
                    index=True,
                    engine="pyarrow",  # 使用pyarrow引擎更快
                ),
            }

            save_errors = []
            for save_format in save_formats:
                __file_url = os.path.join(save_dir, f"{base_filename}{save_format}")
                save_method = save_methods.get(save_format)
                if save_method:
                    try:
                        if is_very_large_file:
                            print(f"  正在保存 {save_format} 格式...")
                        save_method(__file_url)
                    except Exception as e:
                        # 记录错误但继续尝试其他格式
                        error_msg = f"{save_format}: {str(e)}"
                        save_errors.append(error_msg)
                        # 尝试降级方案
                        try:
                            if save_format == ".csv":
                                df.to_csv(__file_url, index=False)
                            elif save_format == ".parquet":
                                df.to_parquet(
                                    __file_url, compression="snappy", index=False
                                )
                        except Exception as e2:
                            save_errors.append(f"{save_format} fallback: {str(e2)}")

            # 返回统计信息
            result = {
                "file": os.path.basename(log_file_path),
                "total_msgs": total_msgs,
                "decoded_msgs": decoded_msgs,
                "error_count": error_count,
                "error_types": error_types,  # 添加错误类型统计
                "signals": len(sigs),
                "success": True,
            }

            if save_errors:
                result["save_warnings"] = save_errors

            if is_very_large_file:
                print(f"  ✓ 完成处理: {os.path.basename(log_file_path)}")

            return result
        else:
            # 没有成功解码任何信号
            return {
                "file": os.path.basename(log_file_path),
                "total_msgs": total_msgs,
                "decoded_msgs": decoded_msgs,
                "error_count": error_count,
                "error_types": error_types,  # 添加错误类型统计
                "signals": 0,
                "success": False,
                "error": "No valid signals decoded",
            }
    except MemoryError as e:
        # 内存不足错误
        return {
            "file": os.path.basename(log_file_path),
            "success": False,
            "error": f"内存不足: {str(e)}. 建议: 1)增大step值 2)过滤信号 3)减少进程数",
        }
    except KeyboardInterrupt:
        # 用户中断
        return {
            "file": os.path.basename(log_file_path),
            "success": False,
            "error": "用户中断",
        }
    except Exception as e:
        # 捕获所有其他异常，记录详细信息
        error_detail = traceback.format_exc()
        return {
            "file": os.path.basename(log_file_path),
            "success": False,
            "error": f"{type(e).__name__}: {str(e)}",
            "traceback": error_detail[-500:],  # 只保留最后500字符
        }


class CanDecoder:
    def __init__(
        self,
        dbc_url: StringPathLike,
        can_url: StringPathLike,
        use_numba: bool = True,  # 是否使用Numba加速
        batch_size: int = 1000,  # 批处理大小
    ):  # 构造函数，初始化对象
        self.dbc_url = dbc_url  # 将传入的dbc_url参数赋值给对象的dbc_url属性
        self.can_url = can_url  # 将传入的can_url参数赋值给对象的can_url属性
        self.use_numba = use_numba and NUMBA_AVAILABLE  # 只有在可用时才启用
        self.batch_size = batch_size  # 批处理大小

        # 性能统计
        self.performance_mode = True  # 启用性能优化模式

        self.dbcs = self.__load_dbc_multi(
            dbc_url
        )  # 调用私有方法__load_dbc_multi加载dbc文件，并将结果赋值给对象的dbcs属性
        self.blf_urls, self.asc_urls = self.__load_can_multi(
            can_url
        )  # 调用私有方法__load_can_multi加载can文件，并将结果分别赋值给对象的blf_urls和asc_urls属性

        # 打印性能配置信息
        if self.use_numba:
            print("✓ Numba JIT加速已启用")
        else:
            print("⚠ Numba不可用，使用标准模式")
        print(f"✓ 批处理大小: {self.batch_size}")

    @classmethod
    def from_config(cls, config_path: StringPathLike) -> "CanDecoder":
        """
        从YAML配置文件创建CanDecoder实例

        Args:
            config_path: YAML配置文件路径

        Returns:
            CanDecoder实例

        Example:
            >>> decoder = CanDecoder.from_config('config.yaml')
            >>> decoder.read_can_files_multi()
        """
        config = load_config_from_yaml(config_path)

        print(f"\n{'='*60}")
        print(f"从配置文件加载: {config_path}")
        print(f"{'='*60}")
        print(f"DBC文件: {config['dbc_path']}")
        print(f"数据路径: {config['can_data_path']}")
        print(f"输出目录: {config['output_dir']}")
        print(f"Step值: {config['step']}")

        if config["signal_names"]:
            print(f"信号过滤: 启用 ({len(config['signal_names'])} 个信号)")
        else:
            print(f"信号过滤: 禁用 (解析所有信号)")

        print(f"{'='*60}\n")

        # 创建实例
        instance = cls(
            dbc_url=config["dbc_path"],
            can_url=config["can_data_path"],
            use_numba=config["use_numba"],
            batch_size=config["batch_size"],
        )

        # 保存配置供后续使用
        instance._config = config

        return instance

    def run_from_config(self) -> None:
        """
        使用加载的配置运行CAN文件处理

        该方法仅在通过from_config()创建实例后可用
        """
        if not hasattr(self, "_config"):
            raise RuntimeError(
                "此方法仅在通过from_config()创建实例后可用。"
                "请使用 CanDecoder.from_config('config.yaml') 创建实例。"
            )

        config = self._config

        self.read_can_files_multi(
            signal_names=config["signal_names"],
            signal_corr=config["signal_mapping"],
            step=config["step"],
            save_dir=config["output_dir"],
            save_formats=config["save_formats"],
            num_processes=config["num_processes"],
            time_from_zero=config["time_from_zero"],
        )

    def __load_dbc_single(self, dbc_url: StringPathLike) -> Tuple[str, Any]:
        """
        Load a DBC file and return the database object.
        """
        # 打开指定路径的DBC文件，以只读模式("r")和指定的编码格式(ENCODING)读取文件内容
        with open(dbc_url, "r", encoding=ENCODING) as f:
            # 使用cantools库的db模块加载DBC文件内容，指定文件格式为"dbc"，并设置严格模式为False
            dbc_content = cantools.db.load(f, database_format="dbc", strict=False)
        # 返回DBC文件的路径和加载的数据库对象，确保dbc_url是字符串
        return str(dbc_url), dbc_content

    def __load_dbc_multi(
        self,
        dbc_url: Union[StringPathLike, List[StringPathLike]],
    ) -> List[Tuple[str, Any]]:

        # 初始化一个空列表用于存储加载的数据库
        dbcs = []
        # 检查dbc_url的类型，如果是字符串路径
        if isinstance(dbc_url, StringPathLike):
            # 检查该路径是否是一个目录
            if os.path.isdir(dbc_url):
                # 获取目录下所有以.dbc结尾的文件路径
                dbc_urls = [
                    os.path.join(dbc_url, file)
                    for file in os.listdir(dbc_url)
                    if file.endswith(".dbc")
                ]
                # 使用map函数并行加载这些.dbc文件
                dbcs.extend(map(self.__load_dbc_single, dbc_urls))

            # 如果是一个文件
            elif os.path.isfile(dbc_url):
                # 将该文件路径添加到列表中
                dbc_urls = [dbc_url]
                # 注释掉的代码：原本是直接调用__load_dbc_single函数加载单个文件
                # dbcs.append(__load_dbc_single(dbc_url))
            else:
                # 如果既不是目录也不是文件，抛出异常
                raise ValueError(f"Invalid DBC file path: {dbc_url}")
        # 如果dbc_url是列表
        elif isinstance(dbc_url, list):
            # 过滤出所有以.dbc结尾的文件路径，并转换为字符串
            dbc_urls = [str(url) for url in dbc_url if str(url).endswith(".dbc")]
            # 注释掉的代码：原本是直接调用__load_dbc_single函数加载列表中的文件
            # dbcs.extend(map(__load_dbc_single, dbc_url))
        else:
            # 如果dbc_url既不是字符串也不是列表，抛出异常
            raise ValueError(f"Invalid DBC file path: {dbc_url}")
        # 导入ThreadPoolExecutor用于并行处理
        from concurrent.futures import ThreadPoolExecutor

        # 使用ThreadPoolExecutor并行加载所有.dbc文件
        with ThreadPoolExecutor() as executor:
            dbcs = list(executor.map(self.__load_dbc_single, dbc_urls))
        # 返回加载的数据库列表
        return dbcs

    def __load_can_multi(
        self,
        can_url: Union[StringPathLike, List[StringPathLike]],
    ) -> Tuple[List[StringPathLike], List[StringPathLike]]:
        """
        加载多个 CAN 文件路径，并根据文件类型（.blf 或 .asc）分类。

        Args:
            can_url (Union[StringPathLike, List[StringPathLike]]): CAN 文件路径或目录路径，或包含多个路径的列表。

        Returns:
            Tuple[List[StringPathLike], List[StringPathLike]]: 包含 .blf 文件路径列表和 .asc 文件路径列表的元组。
        """
        blf_urls = []  # 存储所有 .blf 文件路径的列表
        asc_urls = []  # 存储所有 .asc 文件路径的列表

        def __process_path(path: StringPathLike):
            """处理单个路径，分类为 .blf 或 .asc 文件"""
            if os.path.isdir(path):
                # 如果路径是目录，列出目录中的所有文件
                files = os.listdir(path)
                # 使用列表推导式和过滤器一次性处理文件
                files = os.listdir(path)
                blf_urls.extend(
                    os.path.join(path, file) for file in files if file.endswith(".blf")
                )
                asc_urls.extend(
                    os.path.join(path, file) for file in files if file.endswith(".asc")
                )
            elif os.path.isfile(path):
                # 使用字典映射减少 if-else 判断
                extension_map = {".blf": blf_urls, ".asc": asc_urls}
                ext = os.path.splitext(path)[1].lower()
                if ext in extension_map:
                    extension_map[ext].append(path)
            return blf_urls, asc_urls

        # 单个路径
        if isinstance(can_url, (str, os.PathLike)):
            __process_path(can_url)
        # 列表使用多线程并行处理
        elif isinstance(can_url, list):
            from concurrent.futures import ThreadPoolExecutor

            with ThreadPoolExecutor() as executor:
                executor.map(__process_path, can_url)
        else:
            raise ValueError(
                "can_url must be a string, PathLike, or a list of such objects."
            )

        return blf_urls, asc_urls

    def __decode_can(
        self,
        dbc_data,
        can_data,
        signal_names: Optional[List[str]] = None,
        signal_corr: Optional[Dict[str, str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Decode CAN data using the provided DBC data.
        优化：批量处理、减少内存分配、使用numpy加速
        """
        from asammdf import Signal  # 从 asammdf 库导入 Signal 类

        decoder_map = _build_decoder_map(dbc_data)

        decoded = defaultdict(lambda: {"timestamps": [], "values": []})
        signal_names_set = set(signal_names) if signal_names else None

        batch_limit = self.batch_size if self.batch_size > 0 else 1000

        def flush_batch(temp_storage: Dict[str, Dict[str, list]]):
            if not temp_storage:
                return
            for sig_name, data in temp_storage.items():
                if not data["timestamps"]:
                    continue
                t_arr = np.asarray(data["timestamps"], dtype=np.float64)
                v_arr = np.asarray(data["values"], dtype=np.float64)
                bucket = decoded[sig_name]
                bucket["timestamps"].append(t_arr)
                bucket["values"].append(v_arr)
            temp_storage.clear()

        temp_data: Dict[str, Dict[str, list]] = defaultdict(lambda: {"timestamps": [], "values": []})
        batch_count = 0
        for __msg in can_data:
            decoder = decoder_map.get(__msg.arbitration_id)
            if decoder is None:
                continue
            try:
                __dec = decoder(__msg.data)
                if not __dec:
                    continue

                for __k, __v in __dec.items():
                    if signal_names_set is None or __k in signal_names_set:
                        value = getattr(__v, "value", __v)
                        entry = temp_data[__k]
                        entry["timestamps"].append(__msg.timestamp)
                        entry["values"].append(value)

                batch_count += 1
                if self.performance_mode and batch_count % batch_limit == 0:
                    flush_batch(temp_data)

            except (KeyError, ValueError, Exception):
                continue

        flush_batch(temp_data)

        sigs = []
        for __k, __v in decoded.items():
            if __v["timestamps"]:
                if self.use_numba:
                    try:
                        timestamps, values = _fast_array_conversion(
                            np.concatenate(__v["timestamps"]) if len(__v["timestamps"]) > 1 else __v["timestamps"][0],
                            np.concatenate(__v["values"]) if len(__v["values"]) > 1 else __v["values"][0],
                        )
                    except Exception:
                        timestamps = np.concatenate(__v["timestamps"]) if len(__v["timestamps"]) > 1 else __v["timestamps"][0]
                        values = np.concatenate(__v["values"]) if len(__v["values"]) > 1 else __v["values"][0]
                else:
                    timestamps = np.concatenate(__v["timestamps"]) if len(__v["timestamps"]) > 1 else __v["timestamps"][0]
                    values = np.concatenate(__v["values"]) if len(__v["values"]) > 1 else __v["values"][0]

                signal_name = signal_corr.get(__k, __k) if signal_corr else __k
                sigs.append(
                    Signal(values, timestamps, name=str(signal_name), encoding="utf-8")
                )

        return sigs

    def __save_to(
        self,
        dbc_file_url,
        can_file_url,
        signals,
        step: float = 0.002,
        time_from_zero: bool = True,
        save_dir: StringPathLike = r"./can_decoded",
        save_formats: Tuple[str, ...] = (".csv", ".parquet", ".mat"),
    ):
        """
        Save decoded CAN data to specified formats.

        Args:
            dbc_file_url (str): Path to the DBC file.
            can_file_url (str): Path to the CAN file.
            signals (list): Decoded signals.
            step (float): Raster step size.
            save_dir (str): Directory to save the output files.
            save_formats (tuple): File formats to save (e.g., .csv, .parquet, .mat).
        """
        # 检查保存目录是否存在，如果不存在则创建
        os.makedirs(save_dir, exist_ok=True)

        # 导入asammdf库中的MDF类和scipy库中的io模块
        from asammdf import MDF
        import scipy.io as sio

        # 如果没有信号数据，直接返回
        if not signals:
            return

        # 创建一个MDF对象
        mdf = MDF()
        # 将解码后的信号添加到MDF对象中
        mdf.append(signals)
        # 将MDF对象转换为DataFrame，指定栅格步长
        df = mdf.to_dataframe(raster=step, time_from_zero=time_from_zero)

        # 生成基础文件名，由DBC文件名和CAN文件名组合而成
        base_filename = os.path.splitext(os.path.basename(can_file_url))[0]

        # 定义文件格式与保存方法的映射 - 优化版本
        save_methods = {
            ".mat": lambda file_url: sio.savemat(
                file_url,
                df.to_dict(orient="list"),
                do_compression=True,  # MAT文件启用压缩
            ),
            ".csv": lambda file_url: df.to_csv(
                file_url, index=False, chunksize=10000  # 分块写入大文件
            ),
            ".parquet": lambda file_url: df.to_parquet(
                file_url,
                compression="snappy",
                index=False,
                engine="pyarrow" if self._has_pyarrow() else "fastparquet",
            ),
        }

        # 遍历保存格式并调用对应的保存方法
        for save_format in save_formats:
            # 生成完整的文件路径
            __file_url = os.path.join(save_dir, f"{base_filename}{save_format}")
            # 获取对应的保存方法
            save_method = save_methods.get(save_format)
            if save_method:
                try:
                    # 调用保存方法
                    save_method(__file_url)
                except Exception as e:
                    # 如果优化方法失败，使用基础方法
                    if save_format == ".csv":
                        df.to_csv(__file_url, index=False)
                    elif save_format == ".parquet":
                        df.to_parquet(__file_url, compression="snappy", index=False)
                    elif save_format == ".mat":
                        sio.savemat(__file_url, df.to_dict(orient="list"))
            else:
                # 如果不支持的文件格式，抛出异常
                raise ValueError(f"Unsupported save format: {save_format}")

    def _has_pyarrow(self) -> bool:
        """检查是否安装了pyarrow"""
        try:
            import pyarrow

            return True
        except ImportError:
            return False

    def read_single_can(
        self,
        dbc_url: str,
        dbc_data: Database,
        log_file_path: str,
        file_type: str,
        signal_names: Optional[List[str]] = None,
        signal_corr: Optional[Dict[str, str]] = None,
        step: float = 0.002,
        time_from_zero: bool = True,
        save_dir: str = r"./can_decoded",
        save_formats: Tuple[str, ...] = (".csv", ".parquet", ".mat"),
    ) -> List[Dict[str, Any]] | None:
        """
        Process a single CAN file (BLF or ASC) and save the decoded data.

        Args:
            dbc_url (str): Path to the DBC file.
            dbc_data (Database): DBC database object.
            log_file_path (str): Path to the CAN log file.
            file_type (str): Type of the CAN file ("blf" or "asc").
            signal_names (Optional[List[str]]): List of signal names to decode.
            signal_corr (Optional[Dict[str, str]]): Signal name corrections.
            step (float): Raster step size.
            save_dir (str): Directory to save the output files.
            save_formats (Tuple[str, ...]): File formats to save (e.g., ".csv", ".parquet").
        """
        try:
            # 根据文件类型加载日志数据
            if file_type == "blf":
                log_data = can.BLFReader(log_file_path)
            elif file_type == "asc":
                log_data = can.ASCReader(log_file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")

            # 解码信号
            signals = self.__decode_can(dbc_data, log_data, signal_names, signal_corr)

            # 保存解码结果
            self.__save_to(
                dbc_url,
                log_file_path,
                signals,
                step,
                time_from_zero,
                save_dir,
                save_formats,
            )
            return signals
        except Exception as e:
            print(f"Error processing file {log_file_path}: {e}")

    def read_can_files(
        self,
        signal_names: Optional[List[str]] = None,
        signal_corr: Optional[Dict[str, str]] = None,
        step: float = 0.002,
        time_from_zero: bool = True,
        save_dir: str = r"./can_decoded",
        save_formats: Tuple[str, ...] = (".csv", ".parquet", ".mat"),
    ) -> None:
        """
        Read CAN files and decode them using the provided DBC data (single-threaded).
        """

        # 确保保存目录存在
        os.makedirs(save_dir, exist_ok=True)

        # 遍历每个 DBC 文件
        for __dbc_url, __dbc_data in self.dbcs:
            # 处理 BLF 文件
            for __blf_url in tqdm(
                self.blf_urls,
                desc=f"Processing BLF files for {os.path.basename(__dbc_url)}",
            ):
                self.read_single_can(
                    __dbc_url,
                    __dbc_data,
                    str(__blf_url),  # 转换为字符串
                    "blf",
                    signal_names,
                    signal_corr,
                    step,
                    time_from_zero,
                    save_dir,
                    save_formats,
                )

            # 处理 ASC 文件
            for __asc_url in tqdm(
                self.asc_urls,
                desc=f"Processing ASC files for {os.path.basename(__dbc_url)}",
            ):
                self.read_single_can(
                    __dbc_url,
                    __dbc_data,
                    str(__asc_url),  # 转换为字符串
                    "asc",
                    signal_names,
                    signal_corr,
                    step,
                    time_from_zero,
                    save_dir,
                    save_formats,
                )

    def read_can_files_multi(
        self,
        signal_names: Optional[List[str]] = None,
        signal_corr: Optional[Dict[str, str]] = None,
        step: float = 0.02,
        time_from_zero: bool = True,
        save_dir: str = r"./can_decoded",
        save_formats: Tuple[str, ...] = (".csv", ".parquet", ".mat"),
        num_processes: Optional[int] = None,
    ) -> None:
        """
        Read multiple CAN files and decode them using the provided DBC data (multi-process).

        Args:
            signal_names (Optional[List[str]]): List of signal names to decode.
            signal_corr (Optional[Dict[str, str]]): Signal name corrections.
            step (float): Raster step size.
            save_dir (str): Directory to save the output files.
            save_formats (Tuple[str, ...]): File formats to save (e.g., ".csv", ".parquet", ".mat").
            num_processes (Optional[int]): Number of processes to use. Default is CPU count - 1.
        """

        # 确保保存目录存在
        os.makedirs(save_dir, exist_ok=True)

        # 构建任务列表 - 只传递DBC文件路径而非Database对象（不可序列化）
        tasks = []
        for __dbc_url, _ in self.dbcs:
            for __blf_url in self.blf_urls:
                tasks.append(
                    (
                        __dbc_url,
                        __blf_url,
                        "blf",
                        signal_names,
                        signal_corr,
                        step,
                        time_from_zero,
                        save_dir,
                        save_formats,
                    )
                )
            for __asc_url in self.asc_urls:
                tasks.append(
                    (
                        __dbc_url,
                        __asc_url,
                        "asc",
                        signal_names,
                        signal_corr,
                        step,
                        time_from_zero,
                        save_dir,
                        save_formats,
                    )
                )

        # 设置进程数，默认为CPU核心数-1，至少为1
        if num_processes is None:
            num_processes = max(1, cpu_count() - 1)

        # 使用进程池并行处理
        with Pool(processes=num_processes) as pool:
            results = list(
                tqdm(
                    pool.imap_unordered(
                        _process_single_file_wrapper,
                        tasks,
                    ),
                    total=len(tasks),
                    desc="Processing CAN files",
                )
            )

        # 统计处理结果
        success_count = sum(1 for r in results if r and r.get("success"))
        failed_count = len(results) - success_count

        # 显示汇总信息
        print(f"\n\n{'='*60}")
        print(f"处理完成: {success_count}/{len(results)} 个文件成功")
        print(f"{'='*60}")

        if failed_count > 0:
            print(f"\n⚠ 警告: {failed_count} 个文件处理失败或无有效数据")
            print(f"\n失败文件详情:")
            for r in results:
                if r and not r.get("success"):
                    error_msg = r.get("error", "Unknown error")
                    print(f"\n  ✖ {r.get('file', 'Unknown')}")
                    print(f"    错误: {error_msg}")
                    # 显示堆栈跟踪（如果有）
                    if "traceback" in r:
                        print(f"    详细: {r['traceback']}")

        # 显示保存警告
        save_warnings = [
            r.get("save_warnings", []) for r in results if r and r.get("save_warnings")
        ]
        if save_warnings:
            print(f"\n⚠ 保存警告:")
            for r in results:
                if r and r.get("save_warnings"):
                    print(f"  {r.get('file')}: {', '.join(r['save_warnings'])}")

        # 显示详细统计
        total_msgs = sum(r.get("total_msgs", 0) for r in results if r)
        decoded_msgs = sum(r.get("decoded_msgs", 0) for r in results if r)
        error_msgs = sum(r.get("error_count", 0) for r in results if r)
        total_data_points = sum(r.get("data_points", 0) for r in results if r)

        # 汇总错误类型统计
        all_error_types = {}
        for r in results:
            if r and "error_types" in r:
                for err_type, count in r["error_types"].items():
                    all_error_types[err_type] = all_error_types.get(err_type, 0) + count

        if total_msgs > 0:
            print(f"\n消息统计:")
            print(f"  总消息数: {total_msgs:,}")
            print(f"  成功解码: {decoded_msgs:,} ({decoded_msgs/total_msgs*100:.1f}%)")
            print(f"  解码错误: {error_msgs:,} ({error_msgs/total_msgs*100:.1f}%)")
            if total_data_points > 0:
                print(f"  数据点总数: {total_data_points:,}")

            # 显示错误类型统计
            if all_error_types:
                print(f"\n错误类型统计:")
                for err_type, count in sorted(
                    all_error_types.items(), key=lambda x: x[1], reverse=True
                ):
                    print(f"  {err_type}: {count:,} ({count/error_msgs*100:.1f}%)")

            if error_msgs > 0:
                print(f"\n提示: 解码错误通常由以下原因引起:")
                print(f"  1. DecodeError - DBC文件中的多路复用器ID定义与实际数据不匹配")
                print(f"  2. KeyError - 消息ID不在DBC文件中")
                print(f"  3. ValueError - CAN消息数据格式错误或不完整")
                print(f"  4. struct.error - 数据解包失败")
                print(f"  这些错误已被自动跳过，不影响其他有效消息的处理。")

        # 大文件处理建议
        large_files = [r for r in results if r and r.get("total_msgs", 0) > 100000]
        if large_files:
            print(f"\n💡 大文件处理建议:")
            print(f"  - 检测到大型文件，建议使用 step=0.05 或更大")
            print(f"  - 考虑使用 signal_names 过滤不需要的信号")
            print(f"  - 如遇到内存不足，可减少 num_processes 参数")


def main():
    # 获取配置文件路径
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
    else:
        config_file = "config.yaml"

    config_path = Path(config_file)

    if not config_path.exists():
        print(f"错误: 配置文件不存在: {config_path}")
        print(f"\n请创建配置文件或指定正确的路径。")
        print(f"用法: python run_with_config.py [config_file]")
        return 1

    try:
        # 从配置文件创建解码器实例
        decoder = CanDecoder.from_config(config_path)

        # 运行解析
        decoder.run_from_config()

        print("\n" + "=" * 60)
        print("✓ 处理完成！")
        print("=" * 60)

        return 0

    except FileNotFoundError as e:
        print(f"\n错误: {e}")
        return 1
    except ValueError as e:
        print(f"\n配置错误: {e}")
        return 1
    except KeyboardInterrupt:
        print(f"\n\n用户中断处理")
        return 130
    except Exception as e:
        print(f"\n未预期的错误: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)


def process_candecode_from_config(config_yaml_path: StringPathLike) -> int:
    """
    Convenience function to process CAN data using a config YAML file.
    Returns number of signals decoded successfully.
    
    Args:
        config_yaml_path: Path to the configuration YAML file
        
    Returns:
        Number of signals decoded
    """
    config_path = Path(config_yaml_path)
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    decoder = CanDecoder.from_config(config_path)
    decoder.run_from_config()
    
    # Return count of output files as proxy for signals
    output_dir = Path(decoder.save_dir)
    if output_dir.exists():
        return len(list(output_dir.glob("*.parquet")))
    return 0

