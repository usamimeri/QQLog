class Visualize:
    def __init__(self) -> None:
        pass

    def simple_visual(self, data, x, y, text):
        '''简单可视化,适用x为频数等，y为人名或时间等定性'''
        import plotly.express as px
        fig = px.bar(data_frame=data, x=x, y=y, text=text, orientation='h',
                     color=x, color_continuous_scale='matter', height=800)
        fig.update_traces(textposition='inside')
        fig.update_layout(
            yaxis=dict(
                tickmode='linear',
                tick0=0,
                dtick=1
            )
        )
        fig.update_layout(font=dict(family='{@Malgun Gothic}',
                                    size=18,))
        return fig

    def word_cloud(self, word_freq, mask=None):
        '''生成词云图,注意需要输入[[词，词频]]或[()]格式，总之内部是这种可迭代的格式
        允许设置图形蒙版'''
        from pyecharts import options as opts
        from pyecharts.charts import WordCloud
        from pyecharts.globals import SymbolType
        from PIL import Image

        wordcloud = WordCloud()
        wordcloud.add(series_name=None,
                      data_pair=word_freq,
                      shape=SymbolType.DIAMOND,
                      word_gap=10,  # 词之间的间隙
                      rotate_step=0,  # 设置词的旋转
                      mask_image=mask,  # 图形蒙版


                      )
        wordcloud.set_global_opts(
            title_opts=opts.TitleOpts(title="词云统计",
                                      title_textstyle_opts=opts.TextStyleOpts(
                                          font_size=30, font_family='{@Malgun Gothic}'))
        )

        wordcloud.render('词云.html')
