"""
文件解析器 — 支持 .txt / .md / .docx
"""
import os


def parse_file(filepath):
    """
    根据文件扩展名解析文件，返回纯文本字符串。
    支持: .txt, .md, .docx
    """
    ext = os.path.splitext(filepath)[1].lower()
    if ext in ('.txt', '.md'):
        return _parse_text(filepath)
    elif ext == '.docx':
        return _parse_docx(filepath)
    else:
        raise ValueError(f"不支持的文件类型: {ext}，仅支持 txt / md / docx")


def _parse_text(filepath):
    """读取纯文本 / Markdown 文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


def _parse_docx(filepath):
    """读取 .docx 文件，提取所有段落文本"""
    try:
        from docx import Document
    except ImportError:
        raise ImportError("请安装 python-docx: pip install python-docx")

    doc = Document(filepath)
    paragraphs = []
    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            paragraphs.append(text)
    return '\n'.join(paragraphs)


def get_file_info(filepath):
    """获取文件基本信息"""
    ext = os.path.splitext(filepath)[1].lower().lstrip('.')
    size = os.path.getsize(filepath)
    return {
        'file_type': ext if ext in ('txt', 'md', 'docx') else 'unknown',
        'file_size': size,
        'original_filename': os.path.basename(filepath),
    }
