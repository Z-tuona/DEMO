"""
===========================================================
RAG 知识库系统 — 一键初始化脚本
自动创建 5 个课程测试知识库并上传示例文档
===========================================================

使用方法:
    先启动 Flask:  cd backend && python app.py
    再运行本脚本:  python init_rag_kbs.py
===========================================================
"""
import requests
import os
import sys

BASE = 'http://localhost:5000'

# ====== 5 个知识库定义 ======
KB_DEFINITIONS = [
    {
        'name': 'Python编程',
        'description': 'Python基础语法、Django/Flask框架、pip包管理等',
        'content': (
            'Python是由Guido van Rossum于1991年创建的解释型高级编程语言。\n'
            'Python的设计哲学强调代码可读性，使用缩进来表示代码块。\n'
            'Python 3是最新主要版本，不再支持Python 2。\n\n'
            'Flask是一个轻量级Web框架，适合小型项目和RESTful API开发。\n'
            'Flask使用Jinja2模板引擎和Werkzeug WSGI工具包。\n'
            'Django是全栈Web框架，包含ORM、Admin后台、表单处理等功能。\n'
            'Django遵循MVT（Model-View-Template）架构模式。\n\n'
            'pip是Python的标准包管理工具，用于安装和管理第三方库。\n'
            '虚拟环境（venv）用于隔离项目依赖，避免版本冲突。\n'
            '装饰器（Decorator）是Python的重要高级特性，用于修改函数行为。\n'
            '列表推导式（List Comprehension）是Python简洁创建列表的语法。'
        ),
    },
    {
        'name': '人工智能',
        'description': '机器学习、深度学习、NLP、计算机视觉等AI技术',
        'content': (
            '人工智能（AI）是研究使计算机模拟人类智能的科学。\n'
            '机器学习是AI的核心分支，让计算机从数据中学习规律。\n\n'
            '深度学习使用多层神经网络来学习数据的层次化表示。\n'
            '卷积神经网络（CNN）擅长图像识别，通过卷积核提取空间特征。\n'
            '循环神经网络（RNN）适合处理序列数据，如文本和时间序列。\n'
            '长短时记忆网络（LSTM）解决了RNN的梯度消失问题。\n\n'
            'Transformer架构通过自注意力（Self-Attention）机制革新了NLP领域。\n'
            'GPT（Generative Pre-trained Transformer）擅长文本生成任务。\n'
            'BERT（Bidirectional Encoder Representations from Transformers）擅长文本理解。\n'
            '大语言模型（LLM）通过海量数据预训练展现出强大的涌现能力。\n'
            '自然语言处理（NLP）研究计算机与人类语言的交互。'
        ),
    },
    {
        'name': 'Web前端',
        'description': 'HTML、CSS、JavaScript、Vue、React等前端技术',
        'content': (
            'HTML（HyperText Markup Language）是构建网页的基础标记语言。\n'
            'HTML使用标签来定义页面结构，如标题、段落、图片、链接等。\n'
            'HTML5引入了语义化标签（header、nav、article、footer等）。\n\n'
            'CSS（Cascading Style Sheets）负责网页的视觉样式和布局。\n'
            'CSS3引入了Flexbox和Grid布局，大幅简化了页面排版。\n'
            '响应式设计（Responsive Design）使网站在不同设备上都有良好体验。\n\n'
            'JavaScript是浏览器端运行的脚本语言，赋予网页交互能力。\n'
            'ES6+带来了箭头函数、模板字符串、解构赋值等现代语法。\n'
            'TypeScript是JavaScript的超集，添加了静态类型检查。\n\n'
            'React由Facebook开发，使用虚拟DOM和组件化思想构建UI。\n'
            'Vue是渐进式JavaScript框架，设计简洁，学习曲线平缓。\n'
            'Webpack和Vite是主流的前端构建打包工具。'
        ),
    },
    {
        'name': '数据库技术',
        'description': 'MySQL、PostgreSQL、MongoDB、Redis等数据库系统',
        'content': (
            '数据库（Database）是有组织的数据集合，由数据库管理系统管理。\n'
            '关系型数据库使用表（Table）来组织数据，用SQL语言查询。\n\n'
            'MySQL是最流行的开源关系型数据库，隶属于Oracle公司。\n'
            'MySQL的InnoDB引擎支持事务（ACID）、外键和行级锁。\n'
            'PostgreSQL是功能强大的开源对象关系型数据库。\n'
            'PostgreSQL支持JSON、数组、全文搜索等高级数据类型。\n\n'
            'NoSQL数据库适用于非结构化或半结构化数据。\n'
            'MongoDB是面向文档的NoSQL数据库，使用BSON格式存储。\n'
            'MongoDB天然支持水平扩展和高可用性。\n'
            'Redis是开源的内存键值存储系统，读写速度极快。\n'
            'Redis常用于缓存（Cache）、会话管理（Session）和消息队列。\n\n'
            'ACID：原子性(Atomicity)、一致性(Consistency)、隔离性(Isolation)、持久性(Durability)。\n'
            '索引（Index）是提高数据库查询性能的重要机制。'
        ),
    },
    {
        'name': '数据结构',
        'description': '数组、链表、树、图、排序算法等计算机基础',
        'content': (
            '数据结构是计算机存储和组织数据的方式，直接影响算法效率。\n\n'
            '数组（Array）是在内存中连续存储相同类型数据的结构。\n'
            '数组支持O(1)随机访问，但插入删除需要O(n)时间。\n'
            '链表（Linked List）通过指针连接节点，内存不连续。\n'
            '链表插入删除只需O(1)，但不支持随机访问需O(n)查找。\n'
            '单链表只有一个方向指针，双链表有前后两个方向。\n\n'
            '栈（Stack）是后进先出（LIFO）的数据结构。\n'
            '队列（Queue）是先进先出（FIFO）的数据结构。\n'
            '二叉树（Binary Tree）每个节点最多有两个子节点。\n'
            '二叉搜索树（BST）左子树 < 根 < 右子树，查找效率O(log n)。\n'
            '平衡二叉树（AVL、红黑树）通过旋转保持树的平衡。\n'
            '堆（Heap）是一种特殊的完全二叉树，用于实现优先队列。\n\n'
            '图的遍历：深度优先搜索（DFS）使用栈，广度优先搜索（BFS）使用队列。\n'
            'Dijkstra算法解决带权最短路径问题。\n\n'
            '快速排序（Quick Sort）平均O(n log n)，最坏O(n²)。\n'
            '归并排序（Merge Sort）稳定O(n log n)，需要额外O(n)空间。\n'
            '冒泡排序（Bubble Sort）简单但效率低，O(n²)。'
        ),
    },
]


def main():
    print("=" * 50)
    print("  RAG 知识库一键初始化")
    print("=" * 50)
    print()

    # 1. 检查后端是否启动
    try:
        r = requests.get(f'{BASE}/api/config', timeout=3)
        if r.status_code != 200:
            print("[错误] 后端未正常响应，请确认 Flask 已启动")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("[错误] 无法连接后端 http://localhost:5000")
        print("       请先运行: cd backend && python app.py")
        sys.exit(1)
    print("[1/3] 后端连接正常")

    # 2. 清理旧数据
    r = requests.get(f'{BASE}/api/kbs')
    for kb in r.json():
        requests.delete(f'{BASE}/api/kbs/{kb["id"]}')
    print(f"[2/3] 旧数据已清理")

    # 3. 创建 5 个知识库并上传文档
    print("[3/3] 正在创建知识库和上传文档...")
    for kb_def in KB_DEFINITIONS:
        # 创建知识库
        r = requests.post(f'{BASE}/api/kbs', json={
            'name': kb_def['name'],
            'description': kb_def['description'],
        })
        if r.status_code != 201:
            print(f"  [失败] {kb_def['name']}: {r.json().get('error', '未知错误')}")
            continue
        kb = r.json()
        kb_id = kb['id']

        # 写临时文件并上传
        tmp_path = f'C:/Users/29475/Desktop/ai-chat/_init_tmp_{kb_id}.txt'
        with open(tmp_path, 'w', encoding='utf-8') as f:
            f.write(kb_def['content'])

        with open(tmp_path, 'rb') as f:
            r = requests.post(f'{BASE}/api/kbs/{kb_id}/docs',
                            files={'files': (f'{kb_def["name"]}_知识库文档.txt', f)})
        os.remove(tmp_path)

        result = r.json()
        if result and 'chunk_count' in result[0]:
            print(f"  [OK] [{kb_id}] {kb_def['name']} — {result[0]['chunk_count']} 个文本块")
        else:
            error = result[0].get('error', '未知') if result else '无响应'
            print(f"  [失败] {kb_def['name']}: {error}")

    # 4. 汇总
    print()
    r = requests.get(f'{BASE}/api/kbs')
    kbs = r.json()
    print("=" * 50)
    print(f"  初始化完成！共 {len(kbs)} 个知识库：")
    for kb in kbs:
        r2 = requests.get(f'{BASE}/api/kbs/{kb["id"]}')
        detail = r2.json()
        print(f"  [{kb['id']}] {kb['name']} | {kb['doc_count']} 文档 | {detail.get('chunk_count', 0)} 向量块")
    print("=" * 50)
    print()
    print("现在可以打开 index.html 进行 RAG 对话测试了！")
    print("  - 在侧边栏选择知识库")
    print("  - 开启 RAG 开关")
    print("  - 输入相关问题，AI 将基于知识库回答")


if __name__ == '__main__':
    main()
