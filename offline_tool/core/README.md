# Core 核心业务逻辑包

本目录包含项目的核心业务逻辑，可被多个应用复用。

## 📦 目录结构

```
core/
├── __init__.py                 # 包初始化
├── data_processing/            # 数据处理模块
│   ├── __init__.py
│   ├── candata.py             # CAN 数据分析
│   ├── candecode.py           # CAN 解码器
│   └── feature.py             # 特征提取
│
├── visualization/              # 可视化模块
│   ├── __init__.py
│   ├── graph_gen.py           # 图表生成器
│   ├── diagram_gen.py         # 流程图生成器
│   └── table_gen.py           # 表格生成器
│
└── document/                   # 文档生成模块
    ├── __init__.py
    ├── ppt_gen.py             # PPT 生成器
    └── word_gen.py            # Word 生成器
```

## 🎯 设计原则

### 1. 职责分离
- **core**: 纯业务逻辑，不依赖其他应用框架

### 2. 可复用性
core 包可以被以下场景复用：
- CLI 命令行工具
- 桌面GUI应用
- 数据处理脚本
- 单元测试

### 3. 模块化
每个子模块专注于特定功能：
- `data_processing`: 数据解析和分析
- `visualization`: 图表和可视化
- `document`: 报告生成

## 📝 使用方法

### 在其他应用中使用

```python
# backend/files/tasks.py
from core.data_processing.candecode import CanDecoder
from core.data_processing.candata import CanData

# 使用 CAN 解码器
decoder = CanDecoder(file_path, dbc_path)
decoded_data = decoder.decode()

# 使用 CAN 数据分析
can_data = CanData(data_path)
metrics = can_data.calculate_metrics()
```

### 在报告生成中使用

```python
# backend/reports/tasks.py
from core.visualization.graph_gen import GraphGen
from core.document.ppt_gen import PPTGen
from core.document.word_gen import WordGen

# 生成图表
graph_gen = GraphGen(data)
chart = graph_gen.generate_line_chart()

# 生成报告
ppt_gen = PPTGen(data)
ppt_gen.generate_ppt()
```

### 在独立脚本中使用

```python
# scripts/analyze_data.py
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from core.data_processing.candata import CanData

# 直接使用核心功能
data = CanData('path/to/data')
results = data.analyze()
```

## 🔧 开发指南

### 添加新功能

1. **确定功能类别**：数据处理、可视化、还是文档生成？
2. **创建新模块**：在对应子目录下创建 `.py` 文件
3. **更新 __init__.py**：导出公共接口
4. **编写测试**：确保功能正常

### 示例：添加新的数据处理器

```python
# core/data_processing/excel_processor.py
class ExcelProcessor:
    def __init__(self, file_path):
        self.file_path = file_path
    
    def process(self):
        # 处理逻辑
        pass
```

```python
# core/data_processing/__init__.py
from .candata import CanData
from .candecode import CanDecoder
from .excel_processor import ExcelProcessor  # 添加新类

__all__ = ['CanData', 'CanDecoder', 'ExcelProcessor']
```

## 📋 依赖管理

core 包的依赖应该在项目根目录的 `requirements.txt` 中声明：

```txt
pandas>=1.5.0
numpy>=1.23.0
cantools>=36.0.0
python-can>=4.0.0
matplotlib>=3.5.0
python-docx>=0.8.11
python-pptx>=0.6.21
openpyxl>=3.0.10
```


## 🚀 未来计划

- [ ] 添加 `core/utils/` 通用工具模块
- [ ] 完善单元测试覆盖率
- [ ] 添加 API 文档
- [ ] 考虑将 core 发布为独立 Python 包
