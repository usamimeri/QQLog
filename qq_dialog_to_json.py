import re
import json
def preprocess(path,newfile):
    '''接受一个txt聊天记录文件地址,处理后生成json文件'''
    dialog=[]
    pattern=r'([-\d]+)\s([:\d]+)\s(【.*】)?(.+)?(\(\d+\)|<.*>)\n?(.*)' #感觉可以了 后面格式化的时候清除一下就好
    regex=re.compile(pattern=pattern)
    with open(path,encoding='utf-8',errors='ignore') as f:
        file=f.read()
        data=re.split(pattern=r'\n{2,3}',string=file)[2:-1]
        #data=str.split(file,'\n\n')[2:-1]#去除前两段无用内容和最后一个空字符
    error=0
    for i in data:
        try:
            date,time,nickname,name,ID,content=regex.findall(i)[0]
        except Exception as e:
            print(i,f'发生错误{e}')
            error+=1
        if not content:
            continue #如果内容为空就跳过这轮循环，不存储空数据
        dialog.append({
            "date":date,
            "time":time,
            # "nickname":nickname.strip('[【】]'), 没有开启绰号，因为太多了耗费token而且没啥意义
            "name":name,
            "ID":ID.strip('[()]'),
            "content":content,
        })
    js=json.dumps(dialog,ensure_ascii=0,indent=4)
    open(newfile,'w').write(js)
    print(f'格式化完成，发生了{error}次错误')
preprocess('幻想韵律-厦大幻想乡.txt','格式化聊天记录.json')
