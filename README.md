# RockCoreImage - 岩心图像识别系统

基于 PyQt6 和 PyTorch 开发的岩心图像分类识别桌面应用。

## 功能特性

- **数据管理** - 批量导入图像，支持jpg、png、bmp格式，网格浏览
- **数据清洗** - 自动检测模糊图像、损坏图像、过小图像
- **图像预处理** - 尺寸统一、数据增强（翻转、旋转、颜色抖动）
- **模型训练** - 支持 ResNet18、ResNet50、VGG16、EfficientNet-B0
- **图像识别** - 单图/批量识别，导出CSV/JSON结果
- **数据处理** - 从图像目录批量处理数据，生成岩性分析JSON
- **岩性分类** - 根据岩性配置对岩性进行标准化分类
- **蚀变分析** - 基于岩性名称检测蚀变类型（绢云母化、绿泥石化、硅化等）

## 环境要求

- Python 3.8+
- PyQt6
- PyTorch 2.0+
- torchvision
- OpenCV
- Pillow
- matplotlib
- pandas
- scikit-image

## 安装

```bash
pip install -r requirements.txt
```

## 使用方法

```bash
python main.py
```

### 数据集格式

训练数据需按类别目录组织：

```
dataset/
├── 类别A/
│   ├── image1.jpg
│   ├── image2.jpg
│   └── ...
├── 类别B/
│   ├── image1.jpg
│   └── ...
└── ...
```

## 界面预览

- **首页** - 软件概览和快速入口
- **数据管理** - 导入和管理岩心图像
- **图像预处理** - 设置增强参数并预览
- **模型训练** - 配置训练参数，实时查看损失曲线
- **图像识别** - 加载模型进行预测

## 技术栈

- PyQt6 - GUI框架
- PyTorch - 深度学习框架
- torchvision - 预训练模型
- OpenCV - 图像处理
- PIL - 图像处理
- matplotlib - 数据可视化
- pandas - 数据导出

## License

MIT License
