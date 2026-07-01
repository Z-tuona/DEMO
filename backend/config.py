"""
RAG 知识库系统 — 全局配置
"""
import os

# ========== 路径 ==========
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)
UPLOAD_FOLDER = os.path.join(PROJECT_DIR, 'uploads')
VECTOR_DB_PATH = os.path.join(PROJECT_DIR, 'vector_db')
SQLITE_DB_PATH = os.path.join(PROJECT_DIR, 'knowledge.db')

# ========== 向量模型 ==========
# 使用多语言模型，支持中英文混合检索
EMBEDDING_MODEL_NAME = 'paraphrase-multilingual-MiniLM-L12-v2'

# HuggingFace 镜像（国内用户）
HF_ENDPOINT = 'https://hf-mirror.com'

# ========== 切块参数 ==========
CHUNK_SIZE = 500        # 每块最大字符数
CHUNK_OVERLAP = 50      # 块间重叠字符数

# ========== 检索参数 ==========
TOP_K_RESULTS = 4       # 每个知识库检索返回的块数

# ========== 系统限制 ==========
MAX_KBS = 5             # 最多知识库数量
MAX_FILE_SIZE = 16 * 1024 * 1024  # 单文件最大 16MB
ALLOWED_EXTENSIONS = {'txt', 'md', 'docx'}

# ========== 外部 API ==========
DEEPSEEK_API_URL = 'https://api.deepseek.com/chat/completions'
DEEPSEEK_MODEL = 'deepseek-chat'
