# -*- coding: utf-8 -*-
import datetime
from bs4 import BeautifulSoup as BS
import time
from selenium import webdriver
from pyquery import PyQuery as pq
import re

from selenium.webdriver.common.by import By

"""从网上爬取数据"""
# 请求头
headers = {
    "Origin": "https://flights.ctrip.com/online/list/oneway-can-bjs?_=1&depdate=2023-02-15&cabin=Y_S_C_F",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/74.0.3729.169 Safari/537.36",
}

# 地名，用来保存在输出文件的名称
# 携程网机票查询的url
base = "https://flights.ctrip.com/online/list/oneway"
# 城市名简称
cities = {"bjs": "北京", "ckg": "重庆", "ctu": "成都", "csx": "长沙", "can": "广州",
          "hrb": "哈尔滨", "hgh": "杭州", "hfe": "合肥", "het": "呼和浩特", "tna": "济南",
          "lhw": "兰州", "nkg": "南京", "syx": "三亚", "xmn": "厦门", "sha": "上海",
          "szx": "深圳", "she": "沈阳", "tsn": "天津", "wuh": "武汉", "sia": "西安"}
cabin = "cabin=Y_S_C_F"
today = datetime.date.today()

# 填充前20城市的路线
city_route = []
for city_1 in cities:
    for city_2 in cities:
        if city_1 == city_2:
            continue
        city_route.append("-" + city_1 + "-" + city_2 + "?_=1")


def craw_page(webdriver):
    # 滚轮滑动，获取剩余航班信息
    js = "window.scrollBy(0,500)"  # 向下滑动500个像素，滚动8次
    for i in range(0, 9):
        webdriver.execute_script(js)
        time.sleep(0.5)

    res = str(pq(webdriver.page_source))  # 获取网站源码
    time.sleep(3)  # 休眠
    with open("3.html", "w", encoding="utf-8") as f:
        f.write(res)

    # 使用靓汤对其解析
    soupi = BS(res, "html.parser")
    # 获取所有航班信息
    flights_info = soupi.find(name="div", attrs={"class": "flight-list root-flights"})
    flights_list = flights_info.contents[0].contents

    for val in flights_list:
        if len(val.contents) == 0:
            continue

        flight_data = dict()
        # 出发信息
        depart_info = val.find(name="div", attrs={"class": "depart-box"})
        flight_data['depart_site'] = depart_info.find(name="div", attrs={"class": "airport"}).text
        flight_data['depart_time'] = depart_info.find(name="div", attrs={"class": "time"}).text

        # 到达信息
        arrive_info = val.find(name="div", attrs={"class": "arrive-box"})
        flight_data['arrive_site'] = arrive_info.find(name="div", attrs={"class": "airport"}).text
        flight_data['arrive_time'] = arrive_info.find(name="div", attrs={"class": "time"}).text

        # 航司信息
        airline_info = val.find(name="div", attrs={"class": "flight-airline"})
        try:
            flight_data['air_company'] = airline_info.find(name="div", attrs={"class": "airline-name"}).text
        except AttributeError:
            flight_data['air_company'] = airline_info.img['alt']
        else:
            flight_data['air_company'] = ""
        # 航班号
        try:
            flight_data['plane_info'] = airline_info.find(name="span", attrs={"class": "plane-No"}).text
        except Exception as e:
            flight_data['plane_info'] = ""

        # 价格信息
        air_price = val.find(name="div", attrs={"class": "price"}).text
        flight_data['air_price_int'] = int(re.findall(r"\d+\.?\d*", air_price)[0])

        # 查询时间为今天
        flight_data['query_date'] = today


# 将每次获取到的网页的html保存写入文件
browser = webdriver.Chrome()  # 打开浏览器
# 获取未来十天的所有数据
for i in range(1, 11):
    day_selected = today + datetime.timedelta(days=+i)
    print(day_selected)
    for route in city_route:
        # 最终查询的url
        url = base + route + "&" + str(day_selected) + "&" + cabin

        # 开始进入网站
        browser.get(url)
        time.sleep(2)  # 等待2s加载

        # 点击提醒窗口
        try:
            btn = browser.find_element(By.CLASS_NAME, "btn-group")
            action = webdriver.ActionChains(browser)
            action.click(btn)
            action.perform()
        except Exception as e:
            print("no need to click, continue to get content")
        time.sleep(2)  # 等待2s加载

        craw_page(browser)
