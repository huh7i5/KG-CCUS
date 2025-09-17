import os
# 暂时禁用PaddleNLP依赖
# from data.schema import schema_v4
# from paddle import inference as paddle_infer
# from paddlenlp import Taskflow

# 定义一个函数，用于关系抽取
def paddle_relation_ie(content):
    print("Warning: UIE model disabled due to PaddleNLP dependency issues")
    # relation_ie = Taskflow("information_extraction", schema=schema_v4.schema, batch_size=2)
    # return relation_ie(content)
    return []


# 关系抽取并修改json文件
def rel_json(content):
    print("Warning: Relation extraction disabled")
    return []  # 暂时返回空列表


# 执行函数
#
def uie_execute(texts):
    print("Warning: UIE execution disabled due to PaddleNLP issues")
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
