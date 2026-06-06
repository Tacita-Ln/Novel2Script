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
    """构建发送给智谱模型的 prompt - 标准剧本格式"""
    schema_definition = """
            你是一个剧本转换工具。将小说转为严格符合以下 YAML Schema 的剧本。

            ## Schema
            ```yaml
            title: string
            author: string
            logline: string
            characters:
            - name: string
                age: int (可选)
                personality: string
                role_type: "主角"/"配角"/"反派"
            scenes:
            - scene_id: int
                location: string
                time: string
                action: string (可选)
                dialogues:
                - character: string
                    line: string        # 原话内容
            ```

            ## 规则
            对话：提取所有引号内的句子。独立成条，不合并。说话人据上下文推断。
            场景：地点/时间变化时新场景，scene_id 从1递增。

            小说内容
            {novel_text}

            只输出 yaml ... 代码块。
            """
    return f"{schema_definition}\n\n## 小说内容：\n{novel_text}\n\n请输出 YAML 剧本（只输出代码块）："


def parse_novel_to_script(novel_text: str, skip_chapter_check: bool = False) -> dict:
    """
    主函数：调用智谱 API 将小说文本转为剧本字典
    参数:
        novel_text: 小说文本
        skip_chapter_check: 是否跳过章节数量检查（用于强制转换）
    """
    if not client:
        return {'success': False, 'data': None, 'error': '智谱 API 客户端未初始化，请检查 ZHIPU_API_KEY 环境变量'}

    # 只有在不跳过时才检查章节数
    if not skip_chapter_check:
        chapter_check = check_chapters(novel_text)
        if not chapter_check['valid']:
            return {'success': False, 'data': None, 'error': chapter_check['message']}

    # 构建 prompt
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