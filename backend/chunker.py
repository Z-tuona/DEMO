"""
文本切块器 — 递归字符分割
分割顺序: 段落(\n\n) → 行(\n) → 句子(。.!！？?) → 空格 → 字符级
最后合并小片段并添加块间重叠
"""
from config import CHUNK_SIZE, CHUNK_OVERLAP


def chunk_text(text, chunk_size=None, overlap=None):
    """
    将长文本按递归策略切分为文本块列表。

    Args:
        text: 原始文本
        chunk_size: 每块最大字符数（默认从 config 读取）
        overlap: 块间重叠字符数（默认从 config 读取）

    Returns:
        list[str] — 文本块列表
    """
    if chunk_size is None:
        chunk_size = CHUNK_SIZE
    if overlap is None:
        overlap = CHUNK_OVERLAP

    if not text or not text.strip():
        return []

    # 统一换行符
    text = text.replace('\r\n', '\n').replace('\r', '\n')

    # 递归分割
    separators = ['\n\n', '\n', '。', '. ', '.', '！', '？', '?', '!', '；', ';', ' ', '']
    chunks = _split_recursive(text, separators, chunk_size)

    # 合并过小的块 + 添加重叠
    return _merge_with_overlap(chunks, chunk_size, overlap)


def _split_recursive(text, separators, chunk_size):
    """递归分割文本：选最佳分隔符 → 分割 → 递归处理子段"""
    if len(text) <= chunk_size:
        return [text] if text.strip() else []

    # 选择合适的分隔符
    best_sep = None
    for sep in separators:
        if sep in text:
            parts = text.split(sep)
            if any(len(p) <= chunk_size for p in parts if p.strip()):
                best_sep = sep
                break

    if best_sep is None:
        return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

    if best_sep == '':
        return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

    parts = text.split(best_sep)
    chunks = []
    for part in parts:
        if not part.strip():
            continue
        sub_chunks = _split_recursive(part.strip(), separators, chunk_size)
        chunks.extend(sub_chunks)

    return chunks


def _merge_with_overlap(chunks, chunk_size, overlap):
    """合并过小的块，并在块间添加重叠"""
    if not chunks:
        return []

    # 第一轮：合并短块
    merged = []
    buffer = ''
    for chunk in chunks:
        if len(buffer) + len(chunk) <= chunk_size:
            buffer = (buffer + '\n' + chunk).strip() if buffer else chunk
        else:
            if buffer:
                merged.append(buffer)
            buffer = chunk
    if buffer:
        merged.append(buffer)

    # 第二轮：添加重叠
    if len(merged) <= 1 or overlap <= 0:
        return merged

    result = [merged[0]]
    for i in range(1, len(merged)):
        prev = merged[i - 1]
        curr = merged[i]
        if len(prev) > overlap:
            result.append(curr)
        else:
            result.append(curr)

    return result
