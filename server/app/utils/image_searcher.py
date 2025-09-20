
class ImageSearcher:
    """CCUS领域图片搜索器"""

    def __init__(self):
        self.image_pair = {
            # CCUS技术相关图片
            "CCUS": "https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=400",
            "CCS": "https://images.unsplash.com/photo-1473341304170-971dccb5ac1e?w=400",
            "CCU": "https://images.unsplash.com/photo-1580541832626-2a7131ee809f?w=400",
            "碳捕集": "https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=400",
            "碳储存": "https://images.unsplash.com/photo-1473341304170-971dccb5ac1e?w=400",
            "碳利用": "https://images.unsplash.com/photo-1580541832626-2a7131ee809f?w=400",
            "二氧化碳": "https://images.unsplash.com/photo-1569163139394-de44cb2e4de3?w=400",
            "CO2": "https://images.unsplash.com/photo-1569163139394-de44cb2e4de3?w=400",

            # 工业设施
            "燃煤电厂": "https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=400",
            "火力发电": "https://images.unsplash.com/photo-1580541832626-2a7131ee809f?w=400",
            "钢铁厂": "https://images.unsplash.com/photo-1581094794329-c8112a89af12?w=400",
            "水泥厂": "https://images.unsplash.com/photo-1606664515524-ed2f786a0bd6?w=400",
            "石油化工": "https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=400",
            "工业烟囱": "https://images.unsplash.com/photo-1569163139394-de44cb2e4de3?w=400",

            # 设备和技术
            "吸收塔": "https://images.unsplash.com/photo-1581094794329-c8112a89af12?w=400",
            "压缩机": "https://images.unsplash.com/photo-1504328345606-18bbc8c9d7d1?w=400",
            "管道": "https://images.unsplash.com/photo-1566837945700-30057527ade0?w=400",
            "反应器": "https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=400",
            "分离器": "https://images.unsplash.com/photo-1606664515524-ed2f786a0bd6?w=400",
            "热交换器": "https://images.unsplash.com/photo-1581094794329-c8112a89af12?w=400",

            # 储存设施
            "地质储存": "https://images.unsplash.com/photo-1473341304170-971dccb5ac1e?w=400",
            "深部咸水层": "https://images.unsplash.com/photo-1473341304170-971dccb5ac1e?w=400",
            "油气藏": "https://images.unsplash.com/photo-1566837945700-30057527ade0?w=400",
            "盐穴": "https://images.unsplash.com/photo-1473341304170-971dccb5ac1e?w=400",

            # 环境和气候
            "气候变化": "https://images.unsplash.com/photo-1569163139394-de44cb2e4de3?w=400",
            "全球变暖": "https://images.unsplash.com/photo-1569163139394-de44cb2e4de3?w=400",
            "温室气体": "https://images.unsplash.com/photo-1569163139394-de44cb2e4de3?w=400",
            "碳排放": "https://images.unsplash.com/photo-1569163139394-de44cb2e4de3?w=400",
            "碳中和": "https://images.unsplash.com/photo-1473341304170-971dccb5ac1e?w=400",
            "清洁能源": "https://images.unsplash.com/photo-1580541832626-2a7131ee809f?w=400",

            # 能源相关
            "风力发电": "https://images.unsplash.com/photo-1466611653911-95081537e5b7?w=400",
            "太阳能": "https://images.unsplash.com/photo-1509391366360-2e959784a276?w=400",
            "可再生能源": "https://images.unsplash.com/photo-1580541832626-2a7131ee809f?w=400",
            "新能源": "https://images.unsplash.com/photo-1580541832626-2a7131ee809f?w=400",

            # 保留原有的一些图片（兼容性）
            "江南大学": "https://xerrors.oss-cn-shanghai.aliyuncs.com/imgs/20230411102806.png",
            "建筑": "https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=400",
            "学校": "https://images.unsplash.com/photo-1523050854058-8df90110c9f1?w=400",
            "大学": "https://images.unsplash.com/photo-1498243691581-b145c3f54a5a?w=400",
            "设备": "https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=400",
            "工厂": "https://images.unsplash.com/photo-1581094794329-c8112a89af12?w=400",
        }

        # CCUS关键词映射
        self.ccus_mappings = {
            'ccus': 'CCUS',
            'ccs': 'CCS',
            'ccu': 'CCU',
            '碳捕集利用与储存': 'CCUS',
            '碳捕集与储存': 'CCS',
            '碳捕集与利用': 'CCU',
            'co2': 'CO2',
            '二氧化碳': '二氧化碳',
            '燃煤电厂': '燃煤电厂',
            '火力发电厂': '火力发电',
            '钢铁工厂': '钢铁厂',
            '水泥工厂': '水泥厂',
        }

    def search(self, query):
        """搜索CCUS相关图片"""
        if not query:
            return None

        query_lower = query.lower()
        print(f"🖼️ Image search for: {query}")

        # 1. 直接匹配
        for key, value in self.image_pair.items():
            if key in query or key.lower() in query_lower:
                print(f"✅ Found image for: {key}")
                return value

        # 2. 通过映射匹配
        for keyword, mapped_key in self.ccus_mappings.items():
            if keyword in query_lower and mapped_key in self.image_pair:
                print(f"✅ Found image via mapping: {keyword} -> {mapped_key}")
                return self.image_pair[mapped_key]

        # 3. CCUS相关关键词匹配
        ccus_keywords = ['碳', '捕集', '储存', '利用', '排放', '工厂', '电厂']
        for keyword in ccus_keywords:
            if keyword in query:
                if keyword in ['碳', '排放']:
                    return self.image_pair.get('二氧化碳')
                elif keyword in ['捕集']:
                    return self.image_pair.get('碳捕集')
                elif keyword in ['储存']:
                    return self.image_pair.get('地质储存')
                elif keyword in ['利用']:
                    return self.image_pair.get('碳利用')
                elif keyword in ['工厂', '电厂']:
                    return self.image_pair.get('燃煤电厂')

        print(f"❌ No image found for: {query}")
        return None
