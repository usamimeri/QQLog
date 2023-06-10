import pandas as pd


class Analysis:
    def __init__(self, data) -> None:
        self.data = data
        self.TIME_FREQUENCY_MAP = {
            'month': lambda x: x.month,
            'hour': lambda x: x.hour,
            'weekday': lambda x: x.weekday(),
            'quarter': lambda x: x.quarter
        }
        self.RENAME = {
            'month': {
                1: '一月',
                2: '二月',
                3: '三月',
                4: '四月',
                5: '五月',
                6: '六月',
                7: '七月',
                8: '八月',
                9: '九月',
                10: '十月',
                11: '十一月',
                12: '十二月'
            },
            'quarter': {1: '第一季度', 2: '第二季度', 3: '第三季度', 4: '第四季度'},
            'weekday': {0: '周一', 1: '周二', 2: '周三', 3: '周四', 4: '周五', 5: '周六', 6: '周日'}
        }

    def key_word_frequency(self, key_words):
        '''关键词频统计,data应该是dataframe,key_words需要是列表等可迭代对象'''
        name_dict = {name: 0 for name in self.data['name'].unique()}
        for name, content in zip(self.data['name'], self.data['content']):
            if any([key_word in content for key_word in key_words]):
                name_dict[name] += 1
        result = dict(sorted(name_dict.items(),
                      key=lambda x: x[1], reverse=True))
        df = pd.DataFrame(list(result.items()), columns=[
                          '名称', '次数']).set_index('名称')
        return df

    def user_content_frequency(self):
        '''发言次数统计,返回名称，次数的dataframe'''
        frequency = self.data['name'].value_counts()
        df = frequency.to_frame('次数')  # 转为dataframe
        df.index.name = '名称'
        return df

    def time_frequency(self, time: str = 'hour'):
        '''获取群按时间的的聊天频率统计，返回时间，次数的df
        支持：小时hour，月份month,季度'quarter'，周几'weekday
        '''

        frequency = self.data['datetime'].map(
            self.TIME_FREQUENCY_MAP[time]).value_counts()
        df = frequency.to_frame('发言频数')  # 转为dataframe
        df.index.name = time
        df.sort_index(inplace=True)
        df = df.rename(index=self.RENAME.get(
            time, {114514: 1919810}))  # 没有查找到就啥也不干
        return df

    def time_most_user(self, time: str = 'hour'):
        '''获取每个小时hour,月份，季度，周几,发言最多的用户及其发言数,最终返回dataframe
        列是 时间 人 次数'''
        self.data['datetime'] = self.data['datetime'].map(
            self.TIME_FREQUENCY_MAP[time])
        frequency = self.data.groupby(
            'datetime')[['name']].value_counts()  # 注意这里可能有时间段是没有人发言的

        most_freq = [('114514')]
        for multiindex in frequency.index:
            if multiindex[0] == most_freq[-1][0]:
                continue
            else:
                most_freq.append(
                    (multiindex[0], multiindex[1], frequency[multiindex[0]][0]))
        most_freq.pop(0) #去除最開始的占位符
        df = pd.DataFrame(most_freq, columns=[
            '时间', '名称', '频数']).set_index('时间')
        df = df.rename(index=self.RENAME.get(
            time, {114514: 1919810}))  # 没有查找到就啥也不干
        return df

    def image_frequency(self):
        '''获取每个人的发图次数，发图占发言占比，表情次数，表情占比，表情和图片的占比'''
        image = self.key_word_frequency(self.data, ['[图片]'])
        emoji = self.key_word_frequency(self.data, ['[表情]'])
        freq = self.data['name'].value_counts().to_frame()  # 发言频数
        temp = pd.concat([image, emoji, freq], axis=1)
        temp.columns = ['发图次数', '发表情次数', '总发言次数']
        temp['发表情和图片次数'] = temp['发图次数']+temp['发表情次数']
        temp['发图占比'] = temp['发图次数']/temp['总发言次数']
        temp['发表情占比'] = temp['发表情次数']/temp['总发言次数']
        temp['发表情和图片占比'] = temp['发表情占比']+temp['发图占比']
        temp = temp[['发图次数', '发表情次数', '发表情和图片次数',
                     '总发言次数', '发图占比', '发表情占比', '发表情和图片占比']]
        return temp.round(2)

    def word_count(self, stopwords_path: list = [], user_dict_path: list = [], n: int = None, is_chinese=True):
        '''进行分词和统计词频，允许设置多停用词和多自定义词典,可以设置n代表可设置只记录出现n次以上的词，
        以及是否要只输出中文'''
        import jieba
        import re
        from collections import Counter

        def load_stopwords():
            stopwords = []
            if stopwords_path:
                for txt in stopwords_path:
                    stopwords += [line.strip()
                                  for line in open(txt, encoding='utf-8').readlines()]
            return stopwords

        def load_user_dict():
            for txt in user_dict_path:
                with open(txt, encoding='utf-8') as f:
                    jieba.load_userdict(f)

        def is_chinese(word):
            if is_chinese:
                if re.search(r'[\u4e00-\u9fa5]+', word):
                    return True
                else:
                    return False
            else:
                return True  # 没有设置要求中文就恒返回True

        if user_dict_path:
            load_user_dict()
        stopwords = load_stopwords()
        # 可以选择停用词
        word_list = [word for content in self.data.content
                     for word in jieba.cut(content)
                     if word not in stopwords and len(word.strip()) > 1 and is_chinese(word)]  # 不统计停用词和字数为0和1的
        count = Counter(word_list)  # 将列表输入Counter计算词频，返回字典
        word_count = dict(sorted(dict(count).items(),
                          key=lambda x: x[1], reverse=True))
        if n:
            word_count = {k: v for k, v in word_count.items()
                          if v >= n}  # 如果设置大于n就进行筛选

        return word_count
    def group_sentiment(self,period_start:str=None,period_end:str=None,rule:str='M'):
        '''获取群按时间序列的情感分数波动，支持年A，月M，周W,日D，时H，分T，秒S等
        可以加上数字如15D表示每15天，具体见重采样方法resample,axis=0默认行采样,how默认平均聚合
        目前也支持选择时间跨度
        后续：由于平均会削弱情感，所以应该返回时间段的正面和负面情感数'''
        from snownlp import SnowNLP
        def get_sentiment(sentence):
            from numpy import NAN
            '''认为0.6以上是正面，0.4以下是负面，忽略中性'''
            s=SnowNLP(sentence).sentiments
            if s>=0.6:
                return '正面'
            elif s<=0.4:
                return '负面'
            else:
                return '中性'
        df=self.data.query('content not in ("[图片]","[表情]")').copy()#去除只含图片表情的聊天记录
        df=df.set_index('datetime')
        if period_start and period_end:
            df=df.loc[period_start:period_end]
        elif period_start:
            df=df.loc[period_start:]
        else:
            df=df.loc[:period_end]
        df['情感分类']=df['content'].apply(lambda x:get_sentiment(x)) #获取情感得分
        dummies=pd.get_dummies(df['情感分类'])
        df=df.join(dummies)
        df=df.drop(['情感分类'],axis='columns')
        df=df.resample(rule=rule).sum()
        return df

    
