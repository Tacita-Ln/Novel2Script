"""
Flask Web 服务 - 提供小说转剧本的交互界面
"""

import os
from flask import Flask, render_template, request, send_file, jsonify
from io import BytesIO
import yaml
from .novel_parser import parse_novel_to_script, check_chapters

app = Flask(__name__)

@app.route('/')
def index():
    """显示上传页面"""
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    """处理小说文本，返回转换后的 YAML 字符串（JSON）"""
    novel_text = request.form.get('novel_text', '').strip()
    uploaded_file = request.files.get('novel_file')
    force_convert = request.form.get('force_convert') == 'true'  # 是否强制转换（跳过章节检查）
    
    if uploaded_file and uploaded_file.filename != '':
        novel_text = uploaded_file.read().decode('utf-8')
    
    if not novel_text:
        return jsonify({'error': '请输入小说内容或上传文件'}), 400
    
    # 字符数限制：最大 80000 字符
    if len(novel_text) > 80000:
        return jsonify({'error': f'小说文本过长，当前 {len(novel_text)} 字符，最大支持 80000 字符'}), 400
    
    # 章节数预检查（非强制转换时）
    if not force_convert:
        from .novel_parser import check_chapters
        chapter_check = check_chapters(novel_text, min_chapters=3)
        if not chapter_check['valid']:
            # 返回特定错误码，供前端判断弹窗
            return jsonify({
                'error': chapter_check['message'],
                'error_type': 'insufficient_chapters',
                'chapters_count': chapter_check['chapters_count']
            }), 400
    
    result = parse_novel_to_script(novel_text, skip_chapter_check=force_convert)
    
    if not result['success']:
        return jsonify({'error': result['error']}), 400
    
    yaml_str = yaml.dump(result['data'], allow_unicode=True, sort_keys=False)
    return jsonify({'yaml': yaml_str})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)