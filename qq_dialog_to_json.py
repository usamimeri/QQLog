import re
import json
import pandas as pd
import os
class DialogExtractor:
    def __init__(self,path) -> None:
        self.path=path #聊天记录txt的位置
        self.json_dialog=None#准备存入json格式的
        self.dialogs=[]#格式为id:名字，只存最新的
        self.name_map={}
    def extract_dialog(self):
        '''提取聊天记录'''
        def flush():
            if content and '撤回了一条消息' not in content and name!='系统消息': #不保存空白消息和撤回消息和系统消息
                self.dialogs.append({
                    'datetime':datetime,
                    # 'nickname':nickname.strip('[【】]'),
                    'name':name,
                    'ID':ID.strip('[()<>]'),
                    'content':content
                })

        def update_name_map():
            self.name_map[ID.strip('[()<>]')]=name #只保存最新名字，可以改成保存多个时间段的名字

        def map_name():
            '''将dialog的name替换成最新名字'''
            for dialog in self.dialogs:
                dialog['name']=self.name_map[dialog['ID']] #根据当前ID替换名字
        
        first_flag=0
        pattern=r"(\d{4}-\d{2}-\d{2} \d{1,2}:\d{2}:\d{2}) (?:【(.*)】)?(.+)?(\(\d+\)|<.*>)"
        #分别匹配日期、时间、称号、名字、邮箱或qq号
        compiled=re.compile(pattern=pattern)

        with open(self.path,mode='r',encoding='utf-8') as f:
            lines=f.readlines()
            lines.append('EOF1145141919810') #在结尾添加终止符号，一旦读到这行表明结束
            for line in lines:
                head_match=compiled.findall(line)
                if head_match:#如果检测到是行头，就把上一次的内容刷新进去
                    if first_flag: #第一次不刷新
                        flush()
                        update_name_map()
                    first_flag=1
                    datetime,nickname,name,ID=head_match[0] 
                    content=''
                else: #若不是行头，就是最前面的内容或者用户输入内容
                    if first_flag: 
                        if line.strip(): #如果不是空行
                            if line=='EOF1145141919810': #如果到达结尾，因为没有下次行头了，立即刷新
                                flush()
                            else:
                                content+=line.strip()
    
        map_name() #替换名字，可以去除
        json_dialog=json.dumps(self.dialogs,ensure_ascii=0,indent=4)
        self.json_dialog=json_dialog
        
    
    def save_json(self):
        try:
            newname=os.path.splitext(self.path)[0]+'.json'
            open(newname,'x').write(self.json_dialog) #不存在文件会被自动创建，存在会报错
        except:
            flag=input('该文件已经存在，是否要覆盖？是则输入1,否则输入0')
            if flag:
                open(newname,'w').write(self.json_dialog)
    def load_json(self):
        return self.json_dialog
    def load_json_dataframe(self):
        return pd.read_json(self.json_dialog)
        
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
        '''发言次数统计,返回名称，次数的df'''
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
        '''获取每个小时发言最多的用户发言,最终返回dataframe
        列是 时间点 人 次数'''
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

class Visualize:
    def __init__(self,data) -> None:
        self.data=data
    def simple_visual(self,x,y,text):
        '''简单可视化,适用x为频数等，y为人名或时间等定性'''
        import plotly.express as px
        fig=px.bar(data_frame=self.data,x=x,y=y,text=text,orientation='h',color=x,color_continuous_scale='matter',height=800)
        fig.update_traces(textposition='inside')
        fig.update_layout(
                yaxis = dict(
                    tickmode = 'linear',
                    tick0 = 0,
                    dtick = 1
                )
        )
        fig.update_layout(font=dict(family='{@Malgun Gothic}', 
                                    size=14,))
        return fig
