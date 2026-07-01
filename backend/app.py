"""
Flask 主服务 — RAG 知识库系统后端
启动: cd backend && python app.py
"""
import os, json, uuid, requests
from flask import Flask, request, jsonify, Response, send_file
from flask_cors import CORS

from config import (
    PROJECT_DIR, UPLOAD_FOLDER, ALLOWED_EXTENSIONS,
    MAX_KBS, MAX_FILE_SIZE, CHUNK_SIZE, CHUNK_OVERLAP,
    TOP_K_RESULTS, DEEPSEEK_API_URL, DEEPSEEK_MODEL,
)
from database import (
    create_kb, get_kb, list_kbs, update_kb, delete_kb, get_kb_count,
    add_document, list_documents, get_document, delete_document,
)
from parser import parse_file, get_file_info
from chunker import chunk_text
from embedding import get_embedding, get_embeddings
from vector_store import (
    add_chunks, query, delete_document_chunks, delete_kb_collection,
    get_kb_chunk_count,
)

app = Flask(__name__, static_folder=PROJECT_DIR, static_url_path='')
CORS(app)

# ========== 首页 ==========
@app.route('/')
def index():
    return send_file(os.path.join(PROJECT_DIR, 'index.html'))

# ========== 知识库 CRUD ==========
@app.route('/api/kbs', methods=['GET', 'POST'])
def handle_kbs():
    if request.method == 'GET':
        return jsonify(list_kbs())

    if request.method == 'POST':
        data = request.get_json(silent=True) or {}
        name = data.get('name', '').strip()
        if not name:
            return jsonify({'error': '知识库名称不能为空'}), 400
        if get_kb_count() >= MAX_KBS:
            return jsonify({'error': f'知识库数量已达上限（{MAX_KBS}个）'}), 400
        kb = create_kb(name, data.get('description', ''))
        return jsonify(kb), 201

@app.route('/api/kbs/<int:kb_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_kb(kb_id):
    kb = get_kb(kb_id)
    if kb is None:
        return jsonify({'error': '知识库不存在'}), 404

    if request.method == 'GET':
        kb['documents'] = list_documents(kb_id)
        kb['chunk_count'] = get_kb_chunk_count(kb_id)
        return jsonify(kb)

    if request.method == 'PUT':
        data = request.get_json(silent=True) or {}
        updated = update_kb(kb_id, data.get('name'), data.get('description'))
        return jsonify(updated)

    if request.method == 'DELETE':
        docs = list_documents(kb_id)
        for doc in docs:
            doc_path = os.path.join(UPLOAD_FOLDER, doc['filename'])
            if os.path.exists(doc_path):
                os.remove(doc_path)
        delete_kb_collection(kb_id)
        delete_kb(kb_id)
        return jsonify({'success': True})

# ========== 文档管理 ==========
@app.route('/api/kbs/<int:kb_id>/docs', methods=['GET', 'POST'])
def handle_docs(kb_id):
    kb = get_kb(kb_id)
    if kb is None:
        return jsonify({'error': '知识库不存在'}), 404

    if request.method == 'GET':
        return jsonify(list_documents(kb_id))

    if request.method == 'POST':
        if 'files' not in request.files:
            return jsonify({'error': '请上传文件（字段名: files）'}), 400

        files = request.files.getlist('files')
        if not files or all(f.filename == '' for f in files):
            return jsonify({'error': '未选择文件'}), 400

        results = []
        for file in files:
            if file.filename == '':
                continue

            ext = os.path.splitext(file.filename)[1].lower().lstrip('.')
            if ext not in ALLOWED_EXTENSIONS:
                results.append({
                    'filename': file.filename,
                    'error': f'不支持的文件类型: .{ext}（支持: {", ".join(sorted(ALLOWED_EXTENSIONS))}）'
                })
                continue

            kb_folder = os.path.join(UPLOAD_FOLDER, str(kb_id))
            os.makedirs(kb_folder, exist_ok=True)
            safe_name = f"{uuid.uuid4().hex}_{file.filename}"
            filepath = os.path.join(kb_folder, safe_name)

            file.seek(0, 2)
            file_size = file.tell()
            file.seek(0)
            if file_size > MAX_FILE_SIZE:
                results.append({
                    'filename': file.filename,
                    'error': f'文件过大（{file_size/1024/1024:.1f}MB），上限 {MAX_FILE_SIZE/1024/1024:.0f}MB'
                })
                continue

            file.save(filepath)

            try:
                text = parse_file(filepath)
                chunks = chunk_text(text, CHUNK_SIZE, CHUNK_OVERLAP)
                if not chunks:
                    os.remove(filepath)
                    results.append({'filename': file.filename, 'error': '文件内容为空'})
                    continue

                embeddings = get_embeddings(chunks)
                info = get_file_info(filepath)
                doc_id = add_document(
                    kb_id, os.path.join(str(kb_id), safe_name),
                    info['original_filename'], info['file_type'],
                    info['file_size'], len(chunks)
                )
                add_chunks(kb_id, doc_id, chunks, embeddings)
                results.append({
                    'id': doc_id,
                    'filename': file.filename,
                    'chunk_count': len(chunks),
                })
            except Exception as e:
                if os.path.exists(filepath):
                    os.remove(filepath)
                results.append({'filename': file.filename, 'error': f'处理失败: {str(e)}'})

        return jsonify(results), 201 if any('id' in r for r in results) else 400

@app.route('/api/kbs/<int:kb_id>/docs/<int:doc_id>', methods=['DELETE'])
def handle_doc(kb_id, doc_id):
    doc = get_document(doc_id)
    if doc is None or doc['kb_id'] != kb_id:
        return jsonify({'error': '文档不存在'}), 404

    doc_path = os.path.join(UPLOAD_FOLDER, doc['filename'])
    if os.path.exists(doc_path):
        os.remove(doc_path)
    delete_document_chunks(kb_id, doc_id)
    delete_document(doc_id)
    return jsonify({'success': True})

# ========== 查看文档内容 ==========
@app.route('/api/kbs/<int:kb_id>/docs/<int:doc_id>/content', methods=['GET'])
def view_doc_content(kb_id, doc_id):
    """查看文档的完整内容和切块详情"""
    doc = get_document(doc_id)
    if doc is None or doc['kb_id'] != kb_id:
        return jsonify({'error': '文档不存在'}), 404

    # 读取原始文件
    doc_path = os.path.join(UPLOAD_FOLDER, doc['filename'])
    if not os.path.exists(doc_path):
        return jsonify({'error': '原始文件已被删除'}), 404

    try:
        full_text = parse_file(doc_path)
        chunks = chunk_text(full_text, CHUNK_SIZE, CHUNK_OVERLAP)
    except Exception as e:
        return jsonify({'error': f'文件解析失败: {str(e)}'}), 500

    return jsonify({
        'doc_id': doc_id,
        'filename': doc['original_filename'],
        'file_type': doc['file_type'],
        'file_size': doc['file_size'],
        'chunk_count': len(chunks),
        'full_text': full_text,
        'chunks': [
            {'index': i, 'text': c, 'char_count': len(c)}
            for i, c in enumerate(chunks)
        ],
    })


# ========== 相关性计算工具 ==========
def calc_relevance(distance):
    """将 ChromaDB 的余弦距离转为 0-100 的相关性百分比"""
    # cosine distance: 0=完全匹配, 2=完全相反
    # 转换为: 100=完全匹配, 0=完全不相关
    score = max(0, min(100, (1 - distance / 2) * 100))
    return round(score, 1)


def search_and_rank(question, kb_ids):
    """检索知识库并计算相关性排名"""
    try:
        question_embedding = get_embedding(question)
    except Exception as e:
        return None, str(e)

    all_chunks = []
    for kb_id in kb_ids:
        results = query(kb_id, question_embedding, TOP_K_RESULTS)
        kb = get_kb(kb_id)
        for r in results:
            r['kb_name'] = kb['name'] if kb else f'知识库{kb_id}'
            r['relevance'] = calc_relevance(r.get('distance', 1))
        all_chunks.extend(results)

    # 按相关性降序
    all_chunks.sort(key=lambda x: x.get('relevance', 0), reverse=True)

    # 相关性等级
    for chunk in all_chunks:
        r = chunk['relevance']
        if r >= 70:
            chunk['level'] = '高'
        elif r >= 40:
            chunk['level'] = '中'
        else:
            chunk['level'] = '低'

    return all_chunks, None


# ========== 相关性检查接口（不调用 AI） ==========
@app.route('/api/check-relevance', methods=['POST'])
def check_relevance():
    """
    检查用户问题与知识库内容的相关性（仅检索，不生成回答）
    用于验证知识库内容是否与问题匹配
    """
    data = request.get_json(silent=True) or {}
    question = data.get('question', '').strip()
    kb_ids = data.get('kb_ids', [])

    if not question:
        return jsonify({'error': '问题不能为空'}), 400
    if not kb_ids:
        return jsonify({'error': '请选择至少一个知识库'}), 400

    all_chunks, error = search_and_rank(question, kb_ids)
    if error:
        return jsonify({'error': f'检索失败: {error}'}), 500

    # 计算整体相关性（取前3个的平均值）
    top_scores = [c['relevance'] for c in all_chunks[:3]]
    overall = round(sum(top_scores) / len(top_scores), 1) if top_scores else 0

    return jsonify({
        'question': question,
        'overall_relevance': overall,       # 整体相关性 0-100
        'overall_level': '高' if overall >= 70 else ('中' if overall >= 40 else '低'),
        'matched_chunks': [{
            'kb_name': c.get('kb_name', '?'),
            'doc_id': c['doc_id'],
            'text_preview': c['text'][:150] + ('...' if len(c['text']) > 150 else ''),
            'relevance': c['relevance'],
            'level': c['level'],
        } for c in all_chunks],
    })


# ========== RAG 聊天 ==========
@app.route('/api/chat/rag', methods=['POST'])
def chat_rag():
    data = request.get_json(silent=True) or {}
    question = data.get('question', '').strip()
    kb_ids = data.get('kb_ids', [])
    history = data.get('history', [])
    api_key = data.get('api_key', '').strip()

    if not question:
        return jsonify({'error': '问题不能为空'}), 400
    if not kb_ids:
        return jsonify({'error': '请选择至少一个知识库'}), 400
    if not api_key:
        return jsonify({'error': '请提供 DeepSeek API Key'}), 400

    # 检索 + 相关性计算
    all_chunks, error = search_and_rank(question, kb_ids)
    if error:
        return jsonify({'error': f'检索失败: {error}'}), 500

    # 整体相关性
    top_scores = [c['relevance'] for c in all_chunks[:3]]
    overall_relevance = round(sum(top_scores) / len(top_scores), 1) if top_scores else 0

    # 构建上下文（含相关性标注）
    context_parts = []
    for chunk in all_chunks:
        doc = get_document(chunk['doc_id'])
        doc_name = doc['original_filename'] if doc else '未知文档'
        context_parts.append(
            f"[相关性:{chunk['relevance']}% | KB:{chunk.get('kb_name','?')} | 文档:{doc_name}]\n{chunk['text']}"
        )
    context_str = '\n\n---\n\n'.join(context_parts)

    # 构建增强提示词
    system_prompt = (
        "你是一个知识库问答助手。请使用以下从用户知识库中检索到的信息来回答问题。\n\n"
        "每条信息前面标注了「相关性」百分比——越高表示与该信息与用户问题越匹配。\n"
        "请优先参考高相关性的内容回答。\n\n"
        "规则：\n"
        "1. 回答开头先给出【整体相关性评估: X%】，然后基于检索内容回答\n"
        "2. 优先使用高相关性的信息，保持准确和客观\n"
        "3. 如果检索信息与问题相关，请引用知识库名称和文档\n"
        "4. 如果所有信息相关性都很低（<40%），请在开头说明「知识库中未找到高度相关信息」，然后使用常识回答\n"
        "5. 回答要简洁、清晰、有条理\n\n"
        f"=== 检索到的知识库信息 ===\n{context_str}\n=== 检索信息结束 ==="
    )

    messages = [{"role": "system", "content": system_prompt}]
    for msg in history:
        messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})
    messages.append({
        "role": "user",
        "content": f"用户问题：{question}\n\n请基于上述检索信息回答。",
    })

    # SSE 流式代理
    def generate():
        # 首先发送相关性元数据
        relevance_meta = json.dumps({
            'type': 'relevance',
            'overall_relevance': overall_relevance,
            'top_matches': [{
                'kb_name': c.get('kb_name', '?'),
                'relevance': c['relevance'],
                'level': c['level'],
                'preview': c['text'][:100] + ('...' if len(c['text']) > 100 else ''),
            } for c in all_chunks[:5]],
        }, ensure_ascii=False)
        yield f'data: {relevance_meta}\n\n'

        try:
            resp = requests.post(
                DEEPSEEK_API_URL,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {api_key}',
                },
                json={
                    'model': DEEPSEEK_MODEL,
                    'messages': messages,
                    'stream': True,
                    'max_tokens': 4096,
                    'temperature': 0.7,
                },
                stream=True,
                timeout=120,
            )

            if resp.status_code != 200:
                err_info = '请求失败'
                try:
                    err = resp.json()
                    err_info = err.get('error', {}).get('message', f'HTTP {resp.status_code}')
                except:
                    err_info = f'HTTP {resp.status_code}'
                yield f'data: {{"error": "{err_info}"}}\n\n'
                yield 'data: [DONE]\n\n'
                return

            for line in resp.iter_lines():
                if line:
                    decoded = line.decode('utf-8') if isinstance(line, bytes) else line
                    yield f'{decoded}\n\n'

        except requests.exceptions.Timeout:
            yield 'data: {"error": "请求超时，请重试"}\n\n'
            yield 'data: [DONE]\n\n'
        except Exception as e:
            yield f'data: {{"error": "请求失败: {str(e)}"}}\n\n'
            yield 'data: [DONE]\n\n'

    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive',
        }
    )

# ========== 配置接口 ==========
@app.route('/api/config')
def get_config():
    return jsonify({
        'max_kbs': MAX_KBS,
        'chunk_size': CHUNK_SIZE,
        'chunk_overlap': CHUNK_OVERLAP,
        'top_k': TOP_K_RESULTS,
        'allowed_extensions': sorted(list(ALLOWED_EXTENSIONS)),
        'max_file_size_mb': MAX_FILE_SIZE / 1024 / 1024,
    })

# ========== 启动 ==========
if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    print("=" * 50)
    print("  RAG 知识库系统后端")
    print("  http://localhost:5000")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=True)
