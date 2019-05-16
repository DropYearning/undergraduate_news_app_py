import jieba.analyse
import datetime
import pymysql
# from snownlp import SnowNLP


# 关键词抽取函数
def keywords_by_jieba_TF(text):
    # 调用结巴分词库封装的TF-IDF算法抽取关键词, 提取效果好, 启动速度满但是分析速度快
    keywords = jieba.analyse.extract_tags(text, topK=3, withWeight=False, allowPOS=('n'))
    keywords_str = ""
    temp = 1
    for word in keywords:
        if temp == 1:
            keywords_str = keywords_str + word
            temp = temp + 1
        else:
            keywords_str = keywords_str + "/" + word
            temp = temp + 1
    # print(keywords_str)
    return keywords_str


def keywords_by_jieba_TR(text):
    # 调用结巴分词库封装的textrank算法抽取关键词, 提取效果好, 启动速度满但是分析速度快
    keywords = jieba.analyse.textrank(text, topK=3, withWeight=False, allowPOS=('n'))
    keywords_str = ""
    temp = 1
    for word in keywords:
        if temp == 1:
            keywords_str = keywords_str + word
            temp = temp + 1
        else:
            keywords_str = keywords_str + "/" + word
            temp = temp + 1
    # print(keywords_str)
    return keywords_str


# def keywords_by_SnowNLP_TR(text):
#     # 调用SnowNLP的封装的textrank算法抽取关键词, 提取效果差, 分析慢
#     s = SnowNLP(text)
#     keywords = s.keywords(3)
#     return keywords



