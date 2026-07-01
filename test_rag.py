"""
RAG 系统端到端测试脚本
"""
import requests, os

BASE = 'http://localhost:5000'

def main():
    # 1. 清理旧数据
    r = requests.get(f'{BASE}/api/kbs')
    for kb in r.json():
        requests.delete(f'{BASE}/api/kbs/{kb["id"]}')
    print('=== 旧数据已清理 ===')

    # 2. 创建5个知识库
    kb_data = [
        ('Python编程', 'Python基础语法、Django、Flask等Web框架'),
        ('人工智能', '机器学习、深度学习、NLP、CV等AI技术'),
        ('Web前端', 'HTML、CSS、JavaScript、Vue、React等技术'),
        ('数据库技术', 'MySQL、PostgreSQL、MongoDB、Redis等'),
        ('数据结构', '数组、链表、树、图、排序算法等'),
    ]
    kb_ids = []
    for name, desc in kb_data:
        r = requests.post(f'{BASE}/api/kbs', json={'name': name, 'description': desc})
        if r.status_code == 201:
            kb_ids.append(r.json()['id'])
            print(f'  [OK] [{kb_ids[-1]}] {name}')
        else:
            print(f'  [FAIL] {name}: {r.json()}')

    print(f'=== 已创建 {len(kb_ids)} 个知识库 ===')

    # 3. 为每个KB上传测试文档
    test_contents = [
        'Python是由Guido van Rossum于1991年创建的解释型高级编程语言。Python设计哲学强调代码可读性。Flask是轻量级Web框架，适合小型项目和API开发。Django是全栈Web框架，包含ORM和Admin后台。Python的pip是标准包管理工具。装饰器是Python的重要高级特性。\nPython 3是最新主要版本，不再支持Python 2。列表推导式是Python的特色语法。',
        '深度学习是机器学习的重要分支，使用多层神经网络来学习数据表示。卷积神经网络（CNN）擅长图像识别任务，通过卷积层提取空间特征。循环神经网络（RNN）适合序列数据处理。\nTransformer架构通过自注意力机制革新了NLP领域，不再依赖循环结构。GPT系列模型基于Transformer解码器架构，擅长文本生成。BERT使用双向编码器进行预训练，适合文本理解。大语言模型通过大规模预训练展现强大的涌现能力。',
        'HTML（超文本标记语言）是构建网页的基础语言，使用标签定义页面结构。CSS（层叠样式表）负责网页的视觉样式和布局设计。JavaScript是浏览器端运行的脚本语言，赋予网页交互能力。\nReact是由Facebook开发的声明式UI框架，使用虚拟DOM提高渲染性能。Vue是渐进式JavaScript框架，设计简洁易于上手。TypeScript是JavaScript的超集，添加了静态类型检查。Webpack和Vite是前端构建工具。',
        'MySQL是最流行的开源关系型数据库管理系统，使用结构化查询语言SQL。InnoDB是MySQL的默认存储引擎，支持事务和外键。PostgreSQL是功能强大的开源对象关系型数据库，支持高级数据类型和全文搜索。\nMongoDB是面向文档的NoSQL数据库，使用BSON格式存储数据，灵活可扩展。Redis是开源的内存键值数据存储系统，常用于缓存、会话管理和消息队列。ACID是数据库事务的四个基本特性：原子性、一致性、隔离性、持久性。',
        '数组（Array）是在内存中连续存储相同类型数据的线性数据结构，支持随机访问。链表（Linked List）通过指针将节点串联起来，插入删除效率高，但不支持随机访问。\n二叉树（Binary Tree）每个节点最多有两个子节点。二叉搜索树左子树值小于根节点，右子树值大于根节点。堆是一种特殊的完全二叉树。图（Graph）由顶点和边组成，遍历算法包括深度优先搜索DFS和广度优先搜索BFS。\n快速排序（Quick Sort）的平均时间复杂度为O(n log n)，是最常用的排序算法。冒泡排序简单但效率低。归并排序是稳定的O(n log n)算法。',
    ]

    for i, (kb_id, content) in enumerate(zip(kb_ids, test_contents)):
        tmp_path = f'C:/Users/29475/Desktop/ai-chat/_tmp_test_{i}.txt'
        with open(tmp_path, 'w', encoding='utf-8') as f:
            f.write(content)

        with open(tmp_path, 'rb') as f:
            r = requests.post(f'{BASE}/api/kbs/{kb_id}/docs', files={'files': ('test_doc.txt', f)})

        os.remove(tmp_path)
        result = r.json()
        for res in result:
            if 'error' in res:
                print(f'  [FAIL] KB {kb_id}: {res["error"]}')
            else:
                print(f'  [OK] KB {kb_id} ({kb_data[i][0]}): upload -> {res["chunk_count"]} chunks')

    # 4. 验证每个KB
    print('=== 知识库状态 ===')
    for kb_id in kb_ids:
        r = requests.get(f'{BASE}/api/kbs/{kb_id}')
        kb = r.json()
        print(f'  [{kb_id}] {kb["name"]}: {kb["doc_count"]} docs, {kb.get("chunk_count", 0)} vectors')

    print()
    print('=== 5个知识库创建和文档上传全部完成! ===')
    print('现在可以打开 index.html 进行 RAG 对话测试')

if __name__ == '__main__':
    main()
