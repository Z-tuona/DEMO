"""
向量嵌入模块 — sentence-transformers 封装
模型: paraphrase-multilingual-MiniLM-L12-v2（384维，支持中英文）
首次使用自动下载 ~120MB，之后缓存本地
"""
import os
from config import EMBEDDING_MODEL_NAME, HF_ENDPOINT

# 懒加载单例
_model = None


def _get_model():
    """获取或加载嵌入模型（单例模式）"""
    global _model
    if _model is None:
        # 设置 HuggingFace 镜像（国内用户）
        if HF_ENDPOINT and not os.environ.get('HF_ENDPOINT'):
            os.environ['HF_ENDPOINT'] = HF_ENDPOINT
            print(f"[embedding] 使用 HF 镜像: {HF_ENDPOINT}")

        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            raise ImportError(
                "请安装 sentence-transformers:\n"
                "  pip install sentence-transformers"
            )

        print(f"[embedding] 正在加载模型: {EMBEDDING_MODEL_NAME} ...")
        print("[embedding] 首次运行需下载 ~120MB，请耐心等待...")
        try:
            _model = SentenceTransformer(EMBEDDING_MODEL_NAME)
            print("[embedding] 模型加载完成！")
        except OSError as e:
            raise RuntimeError(
                f"模型下载失败: {e}\n\n"
                "解决方法:\n"
                "1. 检查网络连接\n"
                f"2. 已设置 HF 镜像: {HF_ENDPOINT}\n"
                "3. 如镜像也失败，请在 config.py 中修改 HF_ENDPOINT"
            )

    return _model


def get_embedding(text):
    """
    获取单个文本的向量嵌入

    Args:
        text: 输入文本（超过 1000 字符会自动截断）

    Returns:
        list[float] — 384 维向量
    """
    if not text or not text.strip():
        raise ValueError("输入文本不能为空")
    model = _get_model()
    if len(text) > 1000:
        text = text[:1000]
    return model.encode(text, normalize_embeddings=True).tolist()


def get_embeddings(texts):
    """
    批量获取文本的向量嵌入

    Args:
        texts: 文本列表

    Returns:
        list[list[float]] — 向量列表
    """
    if not texts:
        return []
    model = _get_model()
    texts = [t[:1000] if len(t) > 1000 else t for t in texts]
    return model.encode(texts, normalize_embeddings=True).tolist()


def get_embedding_dimension():
    """返回向量维度"""
    return _get_model().get_sentence_embedding_dimension()
