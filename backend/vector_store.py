"""
向量存储模块 — ChromaDB 操作封装
每个知识库对应一个 ChromaDB collection: kb_1, kb_2, ..., kb_5
数据持久化在 vector_db/ 目录
"""
import os
from config import VECTOR_DB_PATH, TOP_K_RESULTS

_client = None
_collections = {}


def _get_client():
    """获取 ChromaDB PersistentClient（单例）"""
    global _client
    if _client is None:
        try:
            import chromadb
            from chromadb.config import Settings
        except ImportError:
            raise ImportError("请安装 chromadb: pip install chromadb")

        os.makedirs(VECTOR_DB_PATH, exist_ok=True)
        _client = chromadb.PersistentClient(
            path=VECTOR_DB_PATH,
            settings=Settings(anonymized_telemetry=False)
        )
        print(f"[vector_store] ChromaDB 已初始化: {VECTOR_DB_PATH}")
    return _client


def _collection_name(kb_id):
    return f"kb_{kb_id}"


def _get_collection(kb_id):
    name = _collection_name(kb_id)
    if name not in _collections:
        client = _get_client()
        _collections[name] = client.get_or_create_collection(name=name)
    return _collections[name]


def add_chunks(kb_id, doc_id, chunks, embeddings, metadata_list=None):
    """
    将一个文档的所有文本块存入向量库

    Args:
        kb_id: 知识库 ID
        doc_id: 文档 ID
        chunks: 文本块列表
        embeddings: 对应的向量列表（与 chunks 等长）
        metadata_list: 可选的额外元数据
    """
    if not chunks:
        return

    collection = _get_collection(kb_id)
    n = len(chunks)

    ids = [f"doc{doc_id}_chunk{i}" for i in range(n)]
    metadatas = []
    for i in range(n):
        meta = {"doc_id": str(doc_id), "chunk_index": i}
        if metadata_list and i < len(metadata_list):
            meta.update(metadata_list[i])
        metadatas.append(meta)

    collection.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas,
    )


def query(kb_id, query_embedding, top_k=None):
    """
    在知识库中检索最相关的文本块

    Args:
        kb_id: 知识库 ID
        query_embedding: 查询问题的向量
        top_k: 返回结果数

    Returns:
        list[dict]: [{doc_id, chunk_index, text, distance}, ...]
    """
    if top_k is None:
        top_k = TOP_K_RESULTS

    collection = _get_collection(kb_id)

    if collection.count() == 0:
        return []

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, collection.count()),
        include=['documents', 'metadatas', 'distances'],
    )

    out = []
    if results['ids'] and results['ids'][0]:
        for i in range(len(results['ids'][0])):
            meta = results['metadatas'][0][i] if results['metadatas'] else {}
            out.append({
                'doc_id': int(meta.get('doc_id', 0)),
                'chunk_index': meta.get('chunk_index', 0),
                'text': results['documents'][0][i] if results['documents'] else '',
                'distance': results['distances'][0][i] if results['distances'] else 0,
            })
    return out


def delete_document_chunks(kb_id, doc_id):
    """删除一个文档的所有向量块"""
    collection = _get_collection(kb_id)
    try:
        collection.delete(where={"doc_id": str(doc_id)})
    except Exception as e:
        print(f"[vector_store] 删除文档块失败: {e}")


def delete_kb_collection(kb_id):
    """删除整个知识库的 collection"""
    name = _collection_name(kb_id)
    client = _get_client()
    try:
        client.delete_collection(name)
    except Exception:
        pass
    _collections.pop(name, None)


def get_kb_chunk_count(kb_id):
    """获取知识库中的总块数"""
    return _get_collection(kb_id).count()
