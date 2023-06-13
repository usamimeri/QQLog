# 项目目标
1. 对QQ群聊天记录进行读取，存入多种格式中（目前支持json）
2. 对QQ群聊天记录进行分析，提取有价值的信息
3. 对QQ群聊天记录进行可视化

# 使用案例
```
extractor=DialogExtractor('D:\pywork\数据库\聊天记录\厦大选课交流群（思明）.txt')
extractor.extract_dialog()
extractor.save_json() #存为json格式数据
data=extractor.load_json_dataframe() #读取为dataframe
analysis=Analysis(data) #初始化分析器
analysis.key_word_frequency(['避雷','给分']) #用户关键词统计
analysis.time_frequency(time='weekday') #群按时间的聊天频数统计
analysis.image_frequency() #发图和表情包统计
analysis.user_content_frequency() #发言次数统计
analysis.time_most_user(time='hour') #每个时间点发言最多的群友
word_freq=analysis.word_count(stopwords_path=[],user_dict_path=[],n=30,is_chinese=True) #词频统计，可设置停用词和自定义词，可设置读取多少词频以上的词以及是否只读取中文
visual=Visualize()
visual.word_cloud(word_freq) #生成词云图
visual.simple_visual() #传入之前analysis得到的结果,还有期望的x,y轴的列
```
# 工作流
1. 初始化提取器，传入聊天记录txt文件进行读取，可获取dataframe格式数据以备分析
2. 初始化分析器，对之前读取的聊天记录进行分析，统一获取dataframe结果
3. 初始化可视化器，进行可视化
# 目前功能
## 读取工具
1. 对txt导出聊天记录进行提取并输出json文件
2. 将提取内容转为pandas的dataframe进行分析
## 分析工具
1. 指定关键词获取群友的使用这些词的次数
2. 群友发言总次数统计
3. 群按时间序列的聊天频率统计
4. 时间序列的发言最多的用户及其次数
5. 获取每个人的发图次数，发图占发言占比，表情次数，表情占比，表情和图片的占比
6. 添加全部聊天记录的词频分析，找到群里最常用的词和热门话题
7. 情感分析，即情绪变化和话题情感倾向、并获取按时、天、月、年的统计
## 可视化工具
1. plotly简单可视化
2. 提供词云可视化，使用pyecharts

# 目前目标
1. 获取每个人的活跃时间，即一日有发言一定次数被视为活跃，可以扩展到一小时即活跃小时数
3. （较难）分析小团体的形成如@和回复和一个时间段上的互动，并用networkx库等可视化

# 示例图片
![sentiment](https://github.com/usamimeri/QQLog/blob/main/images/junpei.png)
