# RockCoreImage - 岩心图像识别系统

基于 PyQt6 和 PyTorch 开发的岩心图像分类识别桌面应用。

## 功能特性

- **数据管理** - 批量导入图像，支持jpg、png、bmp格式，网格浏览
- **数据清洗** - 自动检测模糊图像、损坏图像、过小图像
- **图像预处理** - 尺寸统一、数据增强（翻转、旋转、颜色抖动）
- **模型训练** - 支持 ResNet18、ResNet50、VGG16、EfficientNet-B0
- **图像识别** - 单图/批量识别，导出CSV/JSON结果
- **数据处理** - 从Excel/HTML目录批量处理数据
- **岩性分类** - 根据岩性配置对岩性进行标准化分类
- **蚀变分析** - 基于岩性名称检测蚀变类型
- **岩性描述管理** - 生成lithology_descriptions.json关联数据

## 项目架构

```
rockcoreimage/
├── app/
│   ├── ui/                    # UI模块
│   │   ├── home_page.py       # 首页
│   │   ├── data_page.py    # 数据管理页
│   │   ├── process_page.py # 数据处理页
│   │   ├── analysis_page.py # 分析页
│   │   ├── training_page.py # 训练页
│   │   ├── preprocess_page.py # 预处理页
│   │   ├── recognition_page.py # 识别页
│   │   ├── main_window.py # 主窗口
│   │   ├── sidebar.py  # 侧边栏
│   │   ├── widgets.py # 自定义组件
│   │   │
│   │   ├── process_handler.py      # 处理器主模块(多继承)
│   │   ├── process_base_handler.py # 基础功能
│   │   ├── data_process_handler.py # 数据处理
│   │   ├── lithology_handler.py # 岩性分类
│   │   └── alteration_handler.py # 蚀变分析
│   │
│   └── modules/             # 核心模块
│       ├── data_processor.py     # 数据处理主模块
│       ├── excel_processor.py # Excel处理
│       ├── html_processor.py # HTML处理
│       ├── lithology_classifier.py # 岩性分类
│       ├── alteration_analyzer.py # 蚀变分析
│       ├── trainer.py     # 模型训练
│       ├── preprocessor.py # 图像预处理
│       ├── recognizer.py # 图像识别
│       └── data_cleaner.py # 数据清洗
│
├── config/                 # 配置文件
│   ├── rock_types_flat.json
│   ├── alteration_types.json
│   └── ...
│
├── main.py               # 入口
└── README.md
```

## 模块说明

### 数据处理模块 (app/modules/)

| 模块 | 说明 |
|------|------|
| `excel_processor.py` | 读取xlsx文件的岩性描述和图像数据 |
| `html_processor.py` | 解析HTML文件的综合柱状图和白光平扫相册 |
| `lithology_classifier.py` | 岩性标准化分类 |
| `alteration_analyzer.py` | 蚀变类型检测 |
| `data_processor.py` | 主处理器，整合各模块 |

### UI处理器模块 (app/ui/)

| 模块 | 说明 |
|------|------|
| `process_base_handler.py` | 目录选择、统计显示、Excel导出 |
| `data_process_handler.py` | 数据处理进度和结果展示 |
| `lithology_handler.py` | 岩性分类操作 |
| `alteration_handler.py` | 蚀变分析操作 |
| `process_handler.py` | 多重继承整合 |

## 数据处理流程

### Excel模式
1. 读取项目目录下的xlsx文件
2. 读取"岩性描述"表获取岩性名称和描述
3. 读取"岩心影像"表获取图像文件名和深度
4. 匹配深度获取岩性
5. 复制图像到输出目录
6. 生成 `image_descriptions.json` 和 `lithology_descriptions.json`

### HTML模式
1. 读取项目目录下的 `离线成果展示/综合柱状图.html`
2. 解析 `SysHistogramInfo.js` 获取岩性描述
3. 读取 `白光平扫相册.html` 获取图像
4. 匹配深度获取岩性
5. 复制图像到输出目录
6. 生成文件

## 输出文件

- `image_descriptions.json` - 图像描述数据（含lithology_description_id）
- `lithology_descriptions.json` - 岩性描述数据
- `images/` - 复制的图像文件

## 环境要求

- Python 3.8+
- PyQt6
- PyTorch 2.0+
- openpyxl

## 安装

```bash
pip install -r requirements.txt
```

## 运行

```bash
python main.py
```

## License

MIT License