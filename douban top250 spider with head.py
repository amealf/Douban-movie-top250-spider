#  原帖 https://zhuanlan.zhihu.com/p/36202008
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

# 设定5个存放数据的列表：电影排名、电影名称、电影评分、评论人数、短评
total_rank_list = []
total_movie_name = []
total_movie_score = []
total_comment_num = []
total_quote_list = []

for page in range(0, 250, 25):
    url = 'https://movie.douban.com/top250?start={}'.format(page)
    # 构造合理的HTTP请求头， 伪装成浏览器， 绕过反爬虫机制，否则会被反爬虫机制拒绝（418）。 https://www.kesci.com/home/project/5dd6003700b0b900365feaeb
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.44 Safari/537.36"
    # 请求网页
    res = requests.get(url=url, headers={'User-Agent': user_agent})
    res.raise_for_status()  # 检查连接状态
    # res.encoding = 'utf-8'  # 编码转换

    '''
    用BeautifulSoup读html 
    关于BS：https://morvanzhou.github.io/tutorials/data-manipulation/scraping/2-01-beautifulsoup-basic/
    '''
    soup = BeautifulSoup(res.text, "html.parser")

    rank_list = []
    movie_score = []
    movie_name = []
    comment_num = []
    quote_list = []

    '''
    所有电影信息在一个ol标签之内，该标签的 class属性值为grid_view
    find等价于limit=1的find_all
    https://www.crummy.com/software/BeautifulSoup/bs4/doc.zh/#find
    soup.find_all('ol', attrs={'class': 'grid_view'}, limit=1)
    '''
    movie_list = soup.find('ol', attrs={'class': 'grid_view'})
    #  print(movie_list)


    '''
    每个电影在一个li标签里面；
    每个电影的电影名称在：第一个 class属性值为hd 的div标签 下的 第一个 class属性值为title 的span标签里；
    每个电影的评分在对应li标签里的（唯一）一个 class属性值为rating_num 的span标签里；
    每个电影的评价人数在 对应li标签 里的一个 class属性值为star 的div标签中 的最后一个数字；
    每个电影的短评在 对应li标签 里的一个 class属性值为inq 的span标签里。
    '''
    for movie in movie_list.find_all('li'):

        rank = movie.find('em', attrs={'class': ''}).getText()  # 排名
        rank_list.append(rank)
        # print(rank)

        score = movie.find('span', attrs={'class': 'rating_num'}).getText()  # 分数
        movie_score.append(score)
        # print(score)

        name = movie.find('span', attrs={'class': 'title'}).getText()  # 电影名
        movie_name.append(name)

        comment_info = movie.find('div', attrs={'class': 'star'})  # 评论人数
        # print(comment_info)

        '''
        findall返回一个列表，列表里是comment_info里的所有数字
        [-1]是选择此列表中最后一个数字，即评价人数。
        '''
        num = re.findall(r'\d+', str(comment_info))[-1]

        comment_num.append(num)

        quote = movie.find('span', attrs={'class': 'inq'})  # 短评
        if quote is not None:
            quote_list.append(quote.getText())
        else:
            quote_list.append('无')

    # 将每次循环得到的列表加到总列表里
    total_rank_list.extend(rank_list)
    total_movie_name.extend(movie_name)
    total_movie_score.extend(movie_score)
    total_comment_num.extend(comment_num)
    total_quote_list.extend(quote_list)

# 用pandas输出为csv格式的文件
data = {'电影排名': total_rank_list, '电影名称': total_movie_name,
        '电影评分': total_movie_score, '评论人数': total_comment_num,
        '短评': total_quote_list}

df = pd.DataFrame(data)
print(df)
df.to_csv('douban_movie.csv', index=False)
