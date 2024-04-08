from collections import defaultdict
import requests
from bs4 import BeautifulSoup
import re
import matplotlib.pyplot as plt
import json


class Weather:
    def __init__(self):
        # js文件，访问此文件返回json字符串，通过解析字符串获得城市列表区域代码，可以通过代码值覆盖cityID，访问相应城市天气预报，
        self.__city_url = 'https://j.i8tq.com/weather2020/search/city.js'  # 城市列表
        self.__url1 = 'http://www.weather.com.cn/weather/(cityID).shtml'   # 七天
        self.__url2 = 'http://www.weather.com.cn/weather15d/(cityID).shtml'# 8-14天
        self.__cityID = defaultdict(str)    # 城市区域代码
        self.__date = []                    # 日期
        self.__tem_max = []                 # 最高温度
        self.__tem_min = []                 # 最低温度

    # 获取城市列表
    def get_cityList(self, prov):  # prov为输入框输入值
        self.__cityID.clear()  # 清除
        # print(cityID)
        res = []
        city = requests.get(self.__city_url).text.strip('var city_data = ').replace('\r\n', '').replace(' ', '')
        city = json.loads(city)
        # 通过requests.get发送url get请求，解析成json格式可以直接转换的样式，变成嵌套的字典类型
        # 找prov在哪，把匹配的都返回添加到res，访问字典，城市，区域名，得到城市列表
        if prov in city:
            f = '1'
            s = prov
            for town in city[prov]:
                if town not in s:
                    s += '-' + town
                    f += '2'
                for area in city[prov][town]:
                    if area not in s:
                        s += '-' + area
                        f += '3'
                    res.append(s)
                    self.__cityID[s] = city[prov][town][area]['AREAID']
                    if f[-1] == '3':
                        s = s.replace('-' + area, '')
                        f = f.rstrip('3')
                if f[-1] == '2':
                    s = s.replace('-' + town, '')
                    f = f.rstrip('2')
        elif not res:
            for p in city:
                if prov in city[p]:
                    s = prov
                    f = '1'
                    for area in city[p][prov]:
                        if area not in s:
                            s += '-' + area
                            f += '2'
                        res.append(s)
                        self.__cityID[s] = city[p][prov][area]['AREAID']
                        if f[-1] == '2':
                            s = s.replace('-' + area, '')
                            f = f.rstrip('2')
            if not res:
                for p in city:
                    for t in city[p]:
                        if prov in city[p][t]:
                            res.append(prov)
                            self.__cityID[prov] = city[p][t][prov]['AREAID']
        return res if res else None

    # 获取温度
    def getTem(self, city):
        id = self.__cityID[city]  # 上一步以获取的区域代码
        url1 = self.__url1.replace('(cityID)', id)  # url预处理，cityID替换为区域代码
        url2 = self.__url2.replace('(cityID)', id)
        html1 = requests.get(url1).text  # 发送request请求，返回数据，进行处理
        html2 = requests.get(url2).text
        bs1 = BeautifulSoup(html1, 'html.parser')  # beautifulsoup解析网站，转换成两个对象
        bs2 = BeautifulSoup(html2, 'html.parser')
        temp1 = bs1.find('ul', {'class': 't clearfix'})  # 通过find查找ul标签内容，继续找li，返回列表
        temp1 = temp1.find_all('li')
        # 获取未来七天天气预报，遍历列表，提取日期和最高最低温度
        for i in temp1[1:]:
            self.__date.append(re.search(r'\d+', i.find('h1').get_text()).group() + '日')  # 获取天气日期，添加到data，re.search匹配，抓下来只有数字，其他乱码，所以自己添加‘日’
            t = re.findall(r'\d+', i.find('p', {'class': 'tem'}).get_text())
            # 获取天气温度

            self.__tem_max.append(int(t[0]))
            self.__tem_min.append(int(t[1]))
        temp2 = bs2.find('ul', {'class': 't clearfix'})
        temp2 = temp2.find_all('li')
        # 8到15天的天气数据
        for i in temp2:
            self.__date.append(re.search(r'\d+', i.find('span', {'class': 'time'}).get_text()).group() + '日')
            t = re.findall(r'\d+', i.find('span', {'class': 'tem'}).get_text())
            # 获取天气温度，span中为最高温度，i中为最低温度，当天温度只有一个
            self.__tem_max.append(int(t[0]))
            self.__tem_min.append(int(t[1]))
        self.draw(city)

    # 根据数据绘图
    def draw(self, name):  # name列表框选项，具体地区名
        plt.title(name)    # 图表标题
        plt.rcParams['font.sans-serif'] = 'KaiTI'
        # 运行配置参数中的字体（font）为楷体（KaiTI)
        plt.xlabel('日期', )
        plt.ylabel('温度/℃')
        # 设置x轴y轴的标签为日期，温度，字符型
        plt.plot(self.__date, self.__tem_min, linewidth=1, color='blue', label="最低气温", marker="o", markersize=2)
        plt.plot(self.__date, self.__tem_max, linewidth=1, color='red', label="最高气温", marker="o", markersize=2)
        # 对图形进行一些更改，x轴为日期，y为最低温度/最高温度，颜色为蓝色/红色，标记风格，标记为小圆点，尺寸2
        plt.fill_between(self.__date, self.__tem_max, self.__tem_min, color="lightgreen")
        # 填充两个函数之间的区域，填充颜色为绿色
        for i in range(14):
            plt.text(self.__date[i], self.__tem_max[i], self.__tem_max[i], fontsize=12, color="grey", style="italic",
                     weight="light",
                     verticalalignment='bottom', horizontalalignment='right', rotation=0)
            plt.text(self.__date[i], self.__tem_min[i], self.__tem_min[i], fontsize=12, color="grey", style="italic",
                     weight="light",
                     verticalalignment='top', horizontalalignment='center', rotation=0)
            # 设置线上数据值，在x轴下对某个y点添加数据，字体12，灰色，italic字体，垂直对端对齐，水平右对齐，是和水平坐标轴的夹角为0
        plt.legend(['最高气温', '最低气温'])
        # 图例标题
        plt.savefig("./tem.png", bbox_inches='tight')
        # 保存图片，矢量图
        plt.close()  # 关闭图库
        self.__date.clear()
        self.__tem_max.clear()
        self.__tem_min.clear()
        # 清空
