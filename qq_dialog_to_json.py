from tqdm import tqdm
import re
import json

def extract_dialog(path):
    def flush():
        if content: #不保存空白消息
            dialogs.append({
                'date':date,
                'time':time,
                # 'nickname':nickname.strip('[【】]'),
                'name':name,
                'ID':ID.strip('[()<>]'),
                'content':content
            })

    def update_name_map():
        name_map[ID.strip('[()<>]')]=name #只保存最新名字，可以改成保存多个时间段的名字

    def map_name():
        '''将dialog的name替换成最新名字'''
        for dialog in dialogs:
            dialog['name']=name_map[dialog['ID']] #根据当前ID替换名字

    name_map={} #格式为id:名字，只存最新的
    dialogs=[] #准备存入json格式的
    first_flag=0
    pattern=r"(\d{4}-\d{2}-\d{2}) (\d{1,2}:\d{2}:\d{2}) (【.*】)?(.+)?(\(\d+\)|<.*>)" #分别匹配日期、时间、称号、名字、邮箱或qq号
    compiled=re.compile(pattern=pattern)

    with open(path,mode='r',encoding='utf-8') as f:
        lines=f.readlines()
        lines.append('EOF1145141919810')
        for line in tqdm(lines):
            head_match=compiled.findall(line)
            if head_match:#如果检测到是行头，就把上一次的内容刷新进去
                if first_flag: #第一次不刷新
                    flush()
                    update_name_map()
                first_flag=1
                date,time,nickname,name,ID=head_match[0] 
                content=''
            else: #若不是行头，就是最前面的内容或者用户输入内容
                if first_flag: 
                    if line.strip(): #如果不是空行
                        if line=='EOF1145141919810': #如果到达结尾，因为没有下次行头了，立即刷新
                            flush()
                        else:
                            content+=line.strip()
    map_name() #替换名字，可以去除
    
    js=json.dumps(dialogs,ensure_ascii=0,indent=4)
    try:
        open('extracted_dialog.json','x').write(js) #不存在文件会被自动创建，存在会报错
    except:
        flag=input('该文件已经存在，是否要覆盖？是则输入1,否则输入0')
        if flag:
            open('extracted_dialog.json','w').write(js)
    print(f'成功完成转换！一共{len(dialogs)}条消息')

PATH='你的聊天记录'
extract_dialog(PATH)                
