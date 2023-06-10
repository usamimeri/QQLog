import pandas as pd
   
class Analysis:
    def __init__(self,data) -> None:
        self.data=data

    def key_word_frequency(self,key_words):
        '''词频统计,data应该是dataframe,key_words需要是列表等可迭代对象'''
        name_dict={name:0 for name in self.data['name'].unique()}
        for name,content in zip(self.data['name'],self.data['content']):
            if any([key_word in content for key_word in key_words]):
                name_dict[name]+=1
        result=dict(sorted(name_dict.items(),key=lambda x:x[1],reverse=True))
        df=pd.DataFrame(list(result.items()), columns=['名称', '次数']).set_index('名称')
        return df

    def content_frequency(self):
        '''发言次数统计,返回名称，次数的dataframe'''
        frequency=self.data['name'].value_counts()
        df=frequency.to_frame('次数') #转为dataframe
        df.index.name='名称'
        return df

    def hour_frequency(self):
        '''获取群按小时的聊天频率统计，返回小时，次数的df'''
        frequency=self.data['datetime'].map(lambda x:x.hour).value_counts()
        df=frequency.to_frame('发言频数') #转为dataframe
        df.index.name='小时'
        df.sort_index(inplace=True)
        return df

    def hour_most_user(self):
        '''获取每个小时发言最多的用户及其发言数,最终返回dataframe
        列是 时间 人 次数'''
        self.data['datetime']=self.data['datetime'].map(lambda x:x.hour) #映射为hour
        frequency=self.data.groupby('datetime')[['name']].value_counts() #注意这里可能有小时是没有人发言的
        most_freq = {
            '时间': list(range(24)),
            '名称': [],
            '频数': [],
        }
        for hour in range(24):
            try:
                name=frequency[hour].index[0]
                freq=frequency[hour][0]
            except:
                most_freq['名称'].append('无人发言')
                most_freq['频数'].append(0)
            else:
                most_freq['名称'].append(name)
                most_freq['频数'].append(freq)
        
        df=pd.DataFrame(most_freq,columns=['时间','名称','频数']).set_index('时间')
        return df

    def image_frequency(self):
        '''获取每个人的发图次数，发图占发言占比，表情次数，表情占比，表情和图片的占比'''
        image=self.key_word_frequency(self.data,['[图片]'])
        emoji=self.key_word_frequency(self.data,['[表情]'])
        freq=self.data['name'].value_counts().to_frame() #发言频数
        temp=pd.concat([image,emoji,freq],axis=1)
        temp.columns=['发图次数','发表情次数','总发言次数']
        temp['发表情和图片次数']=temp['发图次数']+temp['发表情次数']
        temp['发图占比']=temp['发图次数']/temp['总发言次数']
        temp['发表情占比']=temp['发表情次数']/temp['总发言次数']
        temp['发表情和图片占比']=temp['发表情占比']+temp['发图占比']
        temp=temp[['发图次数','发表情次数','发表情和图片次数','总发言次数','发图占比','发表情占比','发表情和图片占比']]
        return temp.round(2)
    def word_count(self,stopwords_path:list=[],user_dict_path:list=[],n:int=None,is_chinese=True):
        '''进行分词和统计词频，允许设置多停用词和多自定义词典,可以设置n代表可设置只记录出现n次以上的词，
        以及是否要只输出中文'''
        import jieba
        import re
        from collections import Counter
        def load_stopwords():
            stopwords=[]
            if stopwords_path:
                for txt in stopwords_path:
                    stopwords += [line.strip() for line in open(txt,encoding='utf-8').readlines()]
            return stopwords
        def load_user_dict():
            for txt in user_dict_path:
                with open(txt,encoding='utf-8') as f:
                    jieba.load_userdict(f)
        def is_chinese(word):
            if is_chinese:
                if re.search(r'[\u4e00-\u9fa5]+',word):
                    return True
                else:
                    return False
            else:
                return True #没有设置要求中文就恒返回True
        
        if user_dict_path:
            load_user_dict()
        stopwords=load_stopwords()
        #可以选择停用词
        word_list = [word for content in self.data.content
                            for word in jieba.cut(content) 
                            if word not in stopwords and len(word.strip())>1 and is_chinese(word)] #不统计停用词和字数为0和1的
        count=Counter(word_list) #将列表输入Counter计算词频，返回字典
        word_count=dict(sorted(dict(count).items(),key=lambda x:x[1],reverse=True))
        if n:
            word_count={k: v for k, v in word_count.items() if v >= n}  #如果设置大于n就进行筛选
            
        return word_count