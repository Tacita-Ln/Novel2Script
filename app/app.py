"""
Flask Web 服务 - 提供小说转剧本的交互界面
"""

import os
from flask import Flask, render_template, request, send_file, jsonify
from io import BytesIO
import yaml
from .novel_parser import parse_novel_to_script

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
    
    if uploaded_file and uploaded_file.filename != '':
        novel_text = uploaded_file.read().decode('utf-8')
    
    if not novel_text:
        return jsonify({'error': '请输入小说内容或上传文件'}), 400
    
    result = parse_novel_to_script(novel_text)
    
    if not result['success']:
        return jsonify({'error': result['error']}), 400
    
    # 将字典转为 YAML 字符串
    yaml_str = yaml.dump(result['data'], allow_unicode=True, sort_keys=False)
    
    return jsonify({'yaml': yaml_str})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)