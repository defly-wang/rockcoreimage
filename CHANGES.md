# RockCoreImage 更新日志

## 近期更新 (2025-04-19 ~ 2025-04-20)

### 项目架构重构
- **80710c7** 拆分process_handler.py为多个模块：
  - process_base_handler.py - 基础功能
  - data_process_handler.py - 数据处理
  - lithology_handler.py - 岩性分类
  - alteration_handler.py - 蚀变分析
- **63813a8** 拆分data_processor.py为多个模块：
  - excel_processor.py - Excel读取和处理
  - html_processor.py - HTML文件处理
  - lithology_classifier.py - 岩性分类
  - alteration_analyzer.py - 蚀变分析

### 数据处理优化
- **a9a959f** Excel模式从岩性描述表直接读取生成lithology_descriptions.json
- **3a0642f** 统一Excel和HTML模式：使用lithology_description_id关联岩性描述
- **819c3e4** 完善统计表格：使用lithology_description_id关联岩性描述数据
- **b5d458c** 关联lithology_descriptions.json显示岩性描述和深度信息
- **25db007** 为image_descriptions.json添加lithology_description_id字段
- **51ea388** HTML模式直接从综合柱状图.html生成lithology_descriptions.json
- **9fdc364** 优化数据处理：岩性描述单独存储
- **5f9ee02** 分类时将岩性描述单独存储到descriptions文件

### AI功能增强
- **78f5089** AI接口改为批量处理模式，使用DeepSeek-V3.2模型
- **c9e20d3** AI调用日志输出输入数据和返回JSON
- **ccc190c** AI接口添加system消息指定JSON输出角色
- **1105ec1** AI接口改为硅基流动API，支持JSON模式输出
- **0e30312** 岩性分析模块AI分析功能增加API调用状态输出

### 岩性分析功能
- **75a97b1** 重写深入分析功能，按明确深度范围和岩性关键词分段
- **d6bff32** 添加岩性统计功能，显示在岩性分析界面
- **784f32c** 添加岩性起始编号功能

### Bug修复
- **83558b1** 修复语法错误
- **8e19311** 统计表格显示岩性描述列，按自然顺序
- **0b776b0** 保持岩性数据原始顺序显示
- **d1d3ce1** 修复Excel处理逻辑及统计表格功能
- **f7df236** 修复数据处理模块的多个bug

### 文档更新
- **51cb8a8** 重写README：完整项目架构说明
- **af41fda** 更新README：添加模块架构说明

## 架构变化

### 重构后的模块结构

**数据处理模块 (app/modules/)**
- `data_processor.py` - 主处理器，整合Excel和HTML模式
- `excel_processor.py` - Excel文件读取，岩性匹配
- `html_processor.py` - HTML文件解析，深度匹配
- `lithology_classifier.py` - 岩性标准化分类
- `alteration_analyzer.py` - 蚀变类型检测

**UI处理器模块 (app/ui/)**
- `process_handler.py` - 主处理器（多继承）
- `process_base_handler.py` - 目录选择、统计、导出
- `data_process_handler.py` - 数据处理进度管理
- `lithology_handler.py` - 岩性分类操作
- `alteration_handler.py` - 蚀变分析操作

### 数据流优化

1. **统一数据关联** - 使用 `lithology_description_id` 关联岩性描述
2. **两种处理模式** - Excel和HTML模式统一接口
3. **分离描述文件** - 岩性描述独立存储为 `lithology_descriptions.json`

### 新特性

1. **批量AI分析** - 支持大文件AI分析
2. **JSON模式输出** - AI接口标准化输出格式
3. **完善的岩性统计** - 展示岩性分布
4. **增强的错误处理** - 改进用户体验