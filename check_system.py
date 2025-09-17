#!/usr/bin/env python3
"""
ChatKG 系统状态检查脚本
验证所有组件是否正常工作
"""

import os
import sys
import json

def check_files():
    """检查关键文件"""
    print("📁 Checking system files...")

    files_to_check = [
        "data/data.json",
        "server/app/utils/ner.py",
        "server/app/utils/graph_utils.py",
        "server/app/utils/chat_glm.py",
        "server/app/utils/image_searcher.py",
        "server/app/utils/query_wiki.py",
        "chat-kg/src/views/ChatView.vue"
    ]

    all_good = True
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} - MISSING")
            all_good = False

    return all_good

def check_knowledge_graph():
    """检查知识图谱数据"""
    print("\n📊 Checking knowledge graph data...")

    data_path = "data/data.json"
    if not os.path.exists(data_path):
        print("  ❌ data.json not found")
        return False

    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        nodes = len(data.get('nodes', []))
        links = len(data.get('links', []))
        sents = len(data.get('sents', []))
        categories = len(data.get('categories', []))

        print(f"  ✅ Nodes: {nodes}")
        print(f"  ✅ Links: {links}")
        print(f"  ✅ Sentences: {sents}")
        print(f"  ✅ Categories: {categories}")

        return nodes > 0 and links > 0

    except Exception as e:
        print(f"  ❌ Error reading data.json: {e}")
        return False

def test_ner():
    """测试实体识别"""
    print("\n🔍 Testing NER (Named Entity Recognition)...")

    try:
        sys.path.append('server')
        from app.utils.ner import Ner

        ner = Ner()
        test_queries = ["介绍下灭火器", "潜水装备有哪些", "江南大学"]

        for query in test_queries:
            entities = ner.get_entities(query)
            print(f"  Query: '{query}' -> Entities: {entities}")

        return True

    except Exception as e:
        print(f"  ❌ NER test failed: {e}")
        return False

def test_knowledge_graph_search():
    """测试知识图谱搜索"""
    print("\n🔎 Testing knowledge graph search...")

    try:
        sys.path.append('server')
        from app.utils.graph_utils import search_node_item

        test_entities = ["灭火器", "潜水", "消防"]

        for entity in test_entities:
            graph = search_node_item(entity)
            if graph and graph.get('nodes'):
                print(f"  '{entity}': Found {len(graph['nodes'])} nodes, {len(graph['links'])} links")
            else:
                print(f"  '{entity}': No results found")

        return True

    except Exception as e:
        print(f"  ❌ Knowledge graph search test failed: {e}")
        return False

def test_image_search():
    """测试图片搜索"""
    print("\n🖼️  Testing image search...")

    try:
        sys.path.append('server')
        from app.utils.image_searcher import ImageSearcher

        searcher = ImageSearcher()
        test_queries = ["灭火器", "消防车", "潜水装备"]

        found_count = 0
        for query in test_queries:
            image_url = searcher.search(query)
            if image_url:
                print(f"  '{query}': ✅ Found image")
                found_count += 1
            else:
                print(f"  '{query}': ❌ No image found")

        print(f"  Total images found: {found_count}/{len(test_queries)}")
        return True

    except Exception as e:
        print(f"  ❌ Image search test failed: {e}")
        return False

def test_wiki_search():
    """测试Wikipedia搜索"""
    print("\n📖 Testing Wikipedia search...")

    try:
        sys.path.append('server')
        from app.utils.query_wiki import WikiSearcher

        searcher = WikiSearcher()
        test_queries = ["灭火器", "潜水", "江南大学"]

        found_count = 0
        for query in test_queries:
            result = searcher.search(query)
            if result and result.exists():
                print(f"  '{query}': ✅ Found Wikipedia page")
                found_count += 1
            else:
                print(f"  '{query}': ❌ No Wikipedia page found")

        print(f"  Total pages found: {found_count}/{len(test_queries)}")
        return True

    except Exception as e:
        print(f"  ❌ Wikipedia search test failed: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("🔧 ChatKG System Status Check")
    print("=" * 60)

    tests = [
        ("Files", check_files),
        ("Knowledge Graph", check_knowledge_graph),
        ("NER", test_ner),
        ("Knowledge Graph Search", test_knowledge_graph_search),
        ("Image Search", test_image_search),
        ("Wikipedia Search", test_wiki_search)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")

    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All systems operational! ChatKG is ready to use.")
        print("\nTo start the system:")
        print("  python start_system.py")
    else:
        print("⚠️  Some components need attention. Please check the errors above.")

if __name__ == "__main__":
    main()