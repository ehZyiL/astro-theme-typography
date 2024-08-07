import os
import re


def is_markdown_file(file_path):
    # 检查文件扩展名是否为 .md 或 .markdown
    return file_path.lower().endswith(('.md', '.markdown'))


def insert_yaml_header(file_path):
    if not is_markdown_file(file_path):
        print(f"跳过非 Markdown 文件: {file_path}")
        return

    # 从文件路径中提取文件名（不包括扩展名）
    file_name = os.path.splitext(os.path.basename(file_path))[0]
   # 读取文件内容
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # 创建 YAML 头
    yaml_header = f"""---
title: {file_name}
pubDate: 2024-01-01
categories: ['Java']
description: {file_name}
---

"""

    # 检查文件是否已经有 YAML 头
    if content.startswith('---'):
        # 如果已经有，替换现有的 YAML 头
        content = re.sub(r'^---.*?---\s*\n', yaml_header,
                         content, flags=re.DOTALL)
    else:
        # 如果没有，在文件开头插入 YAML 头
        content = yaml_header + content

    # 将修改后的内容写回文件
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)
    print(f"已成功更新 Markdown 文件: {file_path}")

# 使用示例：处理单个文件
# insert_yaml_header('path/to/your/markdown/file.md')


# 使用示例：处理单个文件
# insert_yaml_header('path/to/your/markdown/file.md')

# 使用示例：处理目录中的所有 Markdown 文件


def process_directory(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            insert_yaml_header(file_path)


# 使用示例
process_directory(r'D:\\archieve\\极客空间MD\\Java 业务开发常见错误 100 例\\')
