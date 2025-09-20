import wikipediaapi
from opencc import OpenCC

cc = OpenCC('s2t')

class WikiSearcher(object):
    """CCUS领域Wikipedia搜索器"""

    def __init__(self) -> None:
        self.wiki = wikipediaapi.Wikipedia(
            user_agent='CCUS-KnowledgeGraph/1.0 (Educational Purpose)',
            language='zh'
        )
        # CCUS领域相关搜索词扩展
        self.ccus_terms_mapping = {
            'ccus': ['碳捕集利用与储存', '碳捕集', 'CCUS技术'],
            'ccs': ['碳捕集与储存', '碳封存技术'],
            'ccu': ['碳捕集与利用', '碳利用技术'],
            '二氧化碳': ['二氧化碳', 'CO2', '温室气体'],
            '碳捕集': ['碳捕获', '二氧化碳捕集'],
            '碳储存': ['碳封存', '地质储存', 'CO2储存'],
            '碳利用': ['碳转化', 'CO2利用'],
            '气候变化': ['全球变暖', '温室效应'],
            '碳中和': ['净零排放', '碳达峰'],
            '清洁能源': ['可再生能源', '新能源']
        }

    def search(self, query):
        """搜索CCUS相关Wikipedia页面"""
        result = None
        search_terms = [query]

        # 扩展搜索词
        query_lower = query.lower()
        for key, alternatives in self.ccus_terms_mapping.items():
            if key in query_lower:
                search_terms.extend(alternatives)

        print(f"🔍 Wikipedia search for CCUS terms: {search_terms[:3]}")

        # 尝试多个搜索词
        for term in search_terms:
            try:
                # 尝试简体中文
                page = self.wiki.page(term)
                if page.exists():
                    result = page
                    print(f"✅ Found Wikipedia page: {page.title}")
                    break

                # 尝试繁体中文
                traditional_term = cc.convert(term)
                if traditional_term != term:
                    page = self.wiki.page(traditional_term)
                    if page.exists():
                        result = page
                        print(f"✅ Found Wikipedia page (traditional): {page.title}")
                        break

            except Exception as e:
                print(f"⚠️ Wikipedia search error for '{term}': {e}")
                continue

        if not result:
            print(f"❌ No Wikipedia page found for: {query}")

        return result

    def get_summary(self, query, max_length=300):
        """获取摘要信息"""
        page = self.search(query)
        if page and page.exists():
            summary = page.summary
            if len(summary) > max_length:
                summary = summary[:max_length] + "..."
            return {
                "title": page.title,
                "summary": summary,
                "url": page.fullurl
            }
        return None