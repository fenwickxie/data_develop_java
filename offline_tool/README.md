# offline_tool

Python 离线工具，用于 CAN 数据解析（BLF/ASC/CSV）、指标计算、图表生成和报表输出。

## 功能特性

- **下载**：从后端获取签名 URL 并下载原始数据文件
- **计算**：
  - CSV 文件 → CanData 指标提取
  - BLF/ASC 文件 → candecode 完整解码（需 DBC）
- **上传**：将计算的指标上传到后端 API
- **图表生成**：从解码数据生成时序图表（matplotlib）
- **报表生成**：生成包含指标和图表的 Word 分析报告

## 环境要求

- Python 3.10+
- 依赖包：见 `requirements.txt`

## 安装

```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境 (Windows)
.venv\Scripts\activate
# 激活虚拟环境 (Linux/Mac)
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

## 使用方式

### 1. 命令行界面 (CLI)

```bash
# 查看帮助
python cli.py --help

# 下载文件
python cli.py download <file_id> <signed_url>

# 计算指标
python cli.py compute <input_file> --output <output.json> --dbc <dbc_file> --step 0.02

# 上传指标
python cli.py upload <dataset_id> <file_id> <metrics.json>

# 生成图表
python cli.py generate-chart <data_file> --output-dir charts --signal-columns "signal1,signal2"

# 生成报表
python cli.py generate-report <metrics.json> --charts-dir charts --output report/analysis_report.docx
```

### 2. 图形界面 (GUI)

基于 PySide6 的桌面应用，提供友好的可视化界面：

```bash
# 启动 GUI (Windows)
run_gui.bat

# 启动 GUI (Linux/Mac)
chmod +x run_gui.sh
./run_gui.sh

# 或直接运行
python gui.py
```

**GUI 功能标签页：**
- 📥 **下载**：输入文件 ID 和签名 URL，下载到本地
- ⚙️ **计算**：选择数据文件（CSV/BLF/ASC），配置 DBC 和采样步长，计算指标
- 📤 **上传**：配置 API 地址和 token，上传指标到后端
- 📊 **图表**：从解码数据生成时序图表（PNG）
- 📄 **报表**：生成包含指标和图表的 Word 文档

## 配置

复制 `config.example.yaml` 为 `config.yaml`，设置：

```yaml
base_url: http://localhost:8080
auth_token: your-jwt-token-here
```

或使用环境变量：`API_BASE_URL`、`API_AUTH_TOKEN`

## 核心模块

- `core/data_processing/candata.py`：CSV 指标提取
- `core/data_processing/candecode.py`：BLF/ASC 解码（需 DBC）
- `core/data_processing/feature.py`：特征选择器
- `core/visualization/`：图表生成
- `core/document/`：Word/PPT 文档生成

## 开发说明

- CLI 基于 Typer 构建
- GUI 基于 PySide6 (Qt6) 构建
- 解码使用 asammdf + cantools
- 可视化使用 matplotlib/seaborn/plotly

