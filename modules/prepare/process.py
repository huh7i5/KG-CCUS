import os
from data.schema import schema_ccus
from paddlenlp import Taskflow
import paddle

# 全局变量缓存UIE模型，避免重复加载
_uie_model = None

def get_uie_model():
    global _uie_model
    if _uie_model is None:
        print("初始化UIE模型...")
        paddle.set_device('gpu:0')
        _uie_model = Taskflow("information_extraction", schema=schema_ccus.schema, batch_size=4)
        print("UIE模型加载完成！")
    return _uie_model

# 定义一个函数，用于关系抽取
def paddle_relation_ie(content):
    model = get_uie_model()
    return model(content)

# 关系抽取并修改json文件
def rel_json(content):
    return paddle_relation_ie(content)


# 执行函数
def uie_execute(texts):
    sent_id = 0
    all_items = []
    for line in texts:
        line = line.strip()
        all_relations = rel_json(line)

        item = {}
        item["id"] = sent_id
        item["sentText"] = line
        item["relationMentions"] = all_relations

        sent_id += 1
        if sent_id % 10 == 0 and sent_id != 0:
            print("Done {} lines".format(sent_id))

        all_items.append(item)

    return all_items
