"""
Flask Web 服务 - 提供小说转剧本的交互界面
"""

import io
from pathlib import Path

import chardet
import docx
import yaml
from flask import Flask, render_template, request, jsonify

from .novel_parser import parse_novel_to_script, check_chapters

app = Flask(__name__)


def extract_text_from_file(file_storage):
    """
    从上传的文件中提取纯文本，支持 .txt, .md, .docx
    """
    filename = file_storage.filename
    ext = Path(filename).suffix.lower()
    content = file_storage.read()

    # 处理 TXT 和 MD 文件
    if ext in ('.txt', '.md'):
        # 智能检测编码，避免乱码
        detected = chardet.detect(content)
        encoding = detected.get('encoding', 'utf-8')
        if encoding.lower() in ('gb2312', 'gbk'):
            encoding = 'gbk'
        return content.decode(encoding, errors='replace')

    # 处理 DOCX 文件
    if ext == '.docx':
        doc = docx.Document(io.BytesIO(content))
        full_text = []
        # 段落
        for para in doc.paragraphs:
            if para.text.strip():
                full_text.append(para.text)
        # 表格
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    cell_text = cell.text.strip()
                    if cell_text:
                        full_text.append(cell_text)
        return '\n'.join(full_text)

    raise ValueError(f"不支持的文件格式: {ext}，请上传 .txt, .md 或 .docx 文件")


@app.route('/')
def index():
    """显示上传页面"""
    return render_template('index.html')


@app.route('/convert', methods=['POST'])
def convert():
    """处理小说文本，返回转换后的 YAML 字符串（JSON）"""
    novel_text = request.form.get('novel_text', '').strip()
    uploaded_file = request.files.get('novel_file')
    force_convert = request.form.get('force_convert') == 'true'

    if uploaded_file and uploaded_file.filename != '':
        try:
            novel_text = extract_text_from_file(uploaded_file)
        except Exception as e:
            return jsonify({'error': f'文件解析失败: {str(e)}'}), 400

    if not novel_text:
        return jsonify({'error': '请输入小说内容或上传文件'}), 400

    if len(novel_text) > 80000:
        return jsonify({'error': f'小说文本过长，当前 {len(novel_text)} 字符，最大支持 80000 字符'}), 400

    if not force_convert:
        chapter_check = check_chapters(novel_text, min_chapters=3)
        if not chapter_check['valid']:
            return jsonify({
                'error': chapter_check['message'],
                'error_type': 'insufficient_chapters',
                'chapters_count': chapter_check['chapters_count']
            }), 400

    result = parse_novel_to_script(novel_text)
    if not result['success']:
        return jsonify({'error': result['error']}), 400

    yaml_str = yaml.dump(result['data'], allow_unicode=True, sort_keys=False)
    return jsonify({'yaml': yaml_str})


@app.route('/parse_docx', methods=['POST'])
def parse_docx():
    """接收 docx 文件，返回提取的纯文本"""
    if 'file' not in request.files:
        return jsonify({'error': '没有文件'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '文件名为空'}), 400
    try:
        text = extract_text_from_file(file)
        return jsonify({'text': text})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/batch_convert', methods=['POST'])
def batch_convert():
    """批量处理多个小说文件，返回每个文件的转换结果"""
    files = request.files.getlist('novel_files')
    if not files:
        return jsonify({'error': '请至少上传一个文件'}), 400
    
    results = []
    for idx, file in enumerate(files):
        if file.filename == '':
            continue
        try:
            # 使用已有的文件解析函数
            novel_text = extract_text_from_file(file)
        except Exception as e:
            results.append({
                'filename': file.filename,
                'success': False,
                'error': f'文件解析失败: {str(e)}'
            })
            continue
        
        # 检查字符数限制
        if len(novel_text) > 80000:
            results.append({
                'filename': file.filename,
                'success': False,
                'error': f'文本过长（{len(novel_text)}字符），最大支持80000字符'
            })
            continue
        
        # 注意：批量转换默认不强制转换章节数不足的文件（根据需求可改为弹窗，但批量无弹窗，直接失败或强制？建议失败提示）
        # 我们遵循：若章节不足且不是强制，则返回错误（用户可以单个转换时强制）
        from .novel_parser import check_chapters
        chapter_check = check_chapters(novel_text, min_chapters=3)
        if not chapter_check['valid']:
            results.append({
                'filename': file.filename,
                'success': False,
                'error': chapter_check['message']
            })
            continue
        
        # 调用核心转换
        result = parse_novel_to_script(novel_text)
        if result['success']:
            yaml_str = yaml.dump(result['data'], allow_unicode=True, sort_keys=False)
            results.append({
                'filename': file.filename,
                'success': True,
                'yaml': yaml_str
            })
        else:
            results.append({
                'filename': file.filename,
                'success': False,
                'error': result['error']
            })
    
    return jsonify({'results': results})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)