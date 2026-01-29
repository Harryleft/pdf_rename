# PDF 标题修复脚本

该项目用于批量修复中文学术 PDF 的标题，生成规范化文件名并输出到指定目录。

## 快速开始
1. 配置路径（`config.py`）  
   - `SOURCE_PDF_FOLDER`：原始 PDF 目录  
   - `FORMATED_PDF_NAME_FOLDER`：修复后输出目录

2. 配置环境变量  
   - `DEEPSEEK_API_KEY`：DeepSeek API Key（脚本默认使用 `https://api.deepseek.com`）

3. 运行脚本  
```bash
python main.py
```

## CLI 用法
- 指定输入/输出目录：
```bash
python main.py -i "D:\\PDF" -o "D:\\PDF\\修复输出"
```
- 仅指定输入目录，输出目录自动创建为同级 `修复输出`：
```bash
python main.py -i "D:\\PDF"
```
