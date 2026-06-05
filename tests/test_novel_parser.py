import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.novel_parser import parse_novel_to_script
import yaml

def test_with_sample():
    """使用内置示例小说测试转换功能"""
    test_novel = """第一章 相遇
            李明站在雨中，看着远处的红绿灯。他低声说：“今天真是倒霉。”
            第二章 转机
            突然一把伞撑在他头顶。一个女孩笑着说：“需要帮忙吗？”
            第三章 同行
            李明接过伞，点点头：“谢谢你，我叫李明。”
            女孩回答：“我叫王芳，顺路一起走吧。”
            """
    result = parse_novel_to_script(test_novel)
    if result['success']:
        print("✅ 转换成功！YAML如下：")
        print(yaml.dump(result['data'], allow_unicode=True, sort_keys=False))
    else:
        print("❌ 失败:", result['error'])

if __name__ == "__main__":
    test_with_sample()