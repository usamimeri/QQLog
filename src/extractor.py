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
                    # 'nickname':nickname.strip('【】'),
                    'name':name,
                    'ID':ID.strip('()<>'),
                    'content':content
                })

        def update_name_map():
            self.name_map[ID.strip('()<>')]=name #只保存最新名字，可以改成保存多个时间段的名字

        def map_name():
            '''将dialog的name替换成最新名字'''
            for dialog in self.dialogs:
                dialog['name']=self.name_map[dialog['ID']] #根据当前ID替换名字
        
        first_flag=0
        pattern=r"(\d{4}-\d{2}-\d{2} \d{1,2}:\d{2}:\d{2}) (?:【(.*)】)?(.+)?(\(\d+\)|<.*>)"
        #分别匹配日期、时间、称号、名字、邮箱或qq号
        compiled=re.compile(pattern=pattern)

        with open(self.path,mode='r',encoding='utf-8') as f: #打开聊天记录txt
            lines=f.readlines() #读取为列表
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
                    if first_flag:  #不保存最前面的无关内容
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