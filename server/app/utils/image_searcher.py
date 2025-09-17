
class ImageSearcher:

    def __init__(self):
        self.image_pair = {
            # 原有数据
            "江南大学": "https://xerrors.oss-cn-shanghai.aliyuncs.com/imgs/20230411102806.png",
            "军舰": "https://xerrors.oss-cn-shanghai.aliyuncs.com/imgs/20230411102751.png",
            "消防手套": "https://xerrors.oss-cn-shanghai.aliyuncs.com/imgs/20230411101854.png",
            "灭火剂": "https://xerrors.oss-cn-shanghai.aliyuncs.com/imgs/20230411104044.png",
            "灭火": "https://xerrors.oss-cn-shanghai.aliyuncs.com/imgs/20230411102650.png",
            "潜水装具": "https://xerrors.oss-cn-shanghai.aliyuncs.com/imgs/20230411102343.png",
            "消防水枪": "https://xerrors.oss-cn-shanghai.aliyuncs.com/imgs/20230411102528.png",
            "潜水": "https://xerrors.oss-cn-shanghai.aliyuncs.com/imgs/20230411104255.png",
            "消防呼吸器": "https://xerrors.oss-cn-shanghai.aliyuncs.com/imgs/20230411103758.png",
            "损管尺": "https://xerrors.oss-cn-shanghai.aliyuncs.com/imgs/20230411104425.png",
            "喷射泵": "https://xerrors.oss-cn-shanghai.aliyuncs.com/imgs/20230411104459.png",
            "空气泡沫喷漆": "https://xerrors.oss-cn-shanghai.aliyuncs.com/imgs/20230411104707.png",
            "火灾": "https://xerrors.oss-cn-shanghai.aliyuncs.com/imgs/20230411214012.png",
            "潜水员": "https://xerrors.oss-cn-shanghai.aliyuncs.com/imgs/20230411214038.png",
            "测深仪": "https://xerrors.oss-cn-shanghai.aliyuncs.com/imgs/20230411214124.png",
            "舰艇声呐": "https://xerrors.oss-cn-shanghai.aliyuncs.com/imgs/20230411214203.png",
            "潜水呼吸装置": "https://xerrors.oss-cn-shanghai.aliyuncs.com/imgs/20230411214221.png",
            "舰艇发动机": "https://xerrors.oss-cn-shanghai.aliyuncs.com/imgs/20230411214326.png",
            "鲨鱼": "https://xerrors.oss-cn-shanghai.aliyuncs.com/imgs/20230411214352.png",

            # 扩展消防安全相关图片
            "灭火器": "https://images.unsplash.com/photo-1618477461853-cf6ed80faba5?w=400",
            "消防栓": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400",
            "消防车": "https://images.unsplash.com/photo-1527427337751-fdca57f6a828?w=400",
            "消防员": "https://images.unsplash.com/photo-1526367790999-0150786686a2?w=400",
            "消防梯": "https://images.unsplash.com/photo-1613909207039-6b173b755cc1?w=400",
            "烟雾报警器": "https://images.unsplash.com/photo-1558618047-3c8c76c2d0b6?w=400",
            "安全出口": "https://images.unsplash.com/photo-1516684732162-798a0062be99?w=400",
            "防火门": "https://images.unsplash.com/photo-1504307651254-35680f356dfd?w=400",
            "火警": "https://images.unsplash.com/photo-1528158222524-d4d912d2e208?w=400",
            "急救包": "https://images.unsplash.com/photo-1603398938425-f0d1f3e0dc24?w=400",

            # 海洋军事相关图片
            "潜艇": "https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=400",
            "舰船": "https://images.unsplash.com/photo-1436491865332-7a61a109cc05?w=400",
            "航母": "https://images.unsplash.com/photo-1606664515524-ed2f786a0bd6?w=400",
            "雷达": "https://images.unsplash.com/photo-1566837945700-30057527ade0?w=400",
            "声呐": "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400",
            "海军": "https://images.unsplash.com/photo-1436491865332-7a61a109cc05?w=400",
            "军港": "https://images.unsplash.com/photo-1606577924006-27d39b132ae2?w=400",
            "护卫舰": "https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=400",

            # 通用图片
            "建筑": "https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=400",
            "学校": "https://images.unsplash.com/photo-1523050854058-8df90110c9f1?w=400",
            "大学": "https://images.unsplash.com/photo-1498243691581-b145c3f54a5a?w=400",
            "设备": "https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=400",
            "工具": "https://images.unsplash.com/photo-1504328345606-18bbc8c9d7d1?w=400",
        }

    def search(self, query):
        for key, value in self.image_pair.items():
            if key in query:
                return value

        return None
