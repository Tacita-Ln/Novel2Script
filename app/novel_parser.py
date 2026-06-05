"""
小说转剧本核心模块 - 调用智谱 GLM-4.5-Air 模型
"""

import os
import re
import yaml
from dotenv import load_dotenv
from zhipuai import ZhipuAI

# 加载环境变量
load_dotenv()

ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "glm-4.5-air")

# 初始化客户端
client = ZhipuAI(api_key=ZHIPU_API_KEY) if ZHIPU_API_KEY else None


def check_chapters(text: str, min_chapters: int = 3) -> dict:
    """
    检查输入文本是否包含足够的章节（默认至少3章）
    返回: {'valid': bool, 'message': str, 'chapters_count': int}
    """
    pattern = r'第[一二三四五六七八九十零0-9]+章'
    chapters = re.findall(pattern, text)
    count = len(set(chapters))
    if count >= min_chapters:
        return {'valid': True, 'message': f'检测到 {count} 个章节，符合要求', 'chapters_count': count}
    else:
        return {'valid': False, 'message': f'检测到 {count} 个章节，至少需要 {min_chapters} 章', 'chapters_count': count}


def build_prompt(novel_text: str) -> str:
    """构建发送给智谱模型的 prompt - 强化格式约束并包含小说内容"""
    schema_definition = """
## 必须遵守的 YAML Schema（字段名和类型完全一致，不要使用任何变体）：

```yaml
title: string          # 剧本标题（根据小说内容提取）
author: string         # 原作者，如果未知写"未知"
logline: string        # 一句话故事梗概
characters:            # 必须是列表，不是字典
  - name: string       # 角色名
    age: int           # 年龄（可选，没有则省略此字段）
    personality: string  # 性格描述
    role_type: string  # 必须是 "主角"、"配角" 或 "反派"
scenes:                # 必须是列表，按顺序
  - scene_id: int      # 从1开始递增
    location: string   # 具体地点
    time: string       # 如："日"、"夜"、"晨"、"暮"、"室内"、"室外"
    action: string     # 动作或环境描述（可选，没有则写空字符串）
    dialogues:         # 必须是列表
      - character: string  # 角色名（必须在 characters 中存在）
        line: string       # 台词内容
        emotion: string    # 情绪（可选，没有则写"平静"）
```

## 要求：
1. 只输出 YAML 代码块（```yaml ... ```），不要输出任何解释文字。
2. 严格遵循上面的字段名和结构（不要用 `type` 代替 `role_type`，不要用 `text` 代替 `line`）。
3. 根据下面提供的小说内容合理提取信息。
"""
    return f"{schema_definition}\n\n## 小说内容：\n{novel_text}\n\n请输出转换后的 YAML 剧本："


def parse_novel_to_script(novel_text: str) -> dict:
    """
    主函数：调用智谱 API 将小说文本转为剧本字典（已解析为 Python 对象）
    返回: {'success': bool, 'data': dict or None, 'error': str}
    """
    if not client:
        return {'success': False, 'data': None, 'error': '智谱 API 客户端未初始化，请检查 ZHIPU_API_KEY 环境变量'}

    # 先检查章节数
    chapter_check = check_chapters(novel_text)
    if not chapter_check['valid']:
        return {'success': False, 'data': None, 'error': chapter_check['message']}

    # 构建 prompt（现在包含了小说内容）
    prompt = build_prompt(novel_text)

    try:
        # 调用智谱 GLM-4.5-Air
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "你是一个专业的剧本格式转换助手，只输出 YAML 格式的剧本内容，不要输出额外解释。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,  # 降低随机性，提高格式稳定性
            top_p=0.9,
        )
        raw_output = response.choices[0].message.content
        # 提取 YAML 代码块
        yaml_match = re.search(r'```yaml\n(.*?)\n```', raw_output, re.DOTALL)
        if not yaml_match:
            # 尝试匹配没有语言标识的代码块
            yaml_match = re.search(r'```\n(.*?)\n```', raw_output, re.DOTALL)
        if not yaml_match:
            # 如果都没有，尝试将整个输出当作 YAML
            yaml_str = raw_output.strip()
        else:
            yaml_str = yaml_match.group(1).strip()

        # 解析 YAML 为 Python 字典
        script_data = yaml.safe_load(yaml_str)
        return {'success': True, 'data': script_data, 'error': None}
    except Exception as e:
        return {'success': False, 'data': None, 'error': f'调用模型或解析 YAML 失败: {str(e)}'}