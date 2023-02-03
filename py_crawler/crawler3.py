# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup as BS
import time
from selenium import webdriver
from pyquery import PyQuery as pq
import pandas as pd
from math import ceil
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
cities = {"bjs": "北京", "ckg": "重庆", "ctu": "成都", "cgq": "长春", "csx": "长沙",
          "dlc": "大连", "can": "广州", "kwe": "贵阳", "kwl": "桂林", "hrb": "哈尔滨",
          "hgh": "杭州", "hfe": "合肥", "het": "呼和浩特", "tna": "济南", "kmg": "昆明",
          "lhw": "兰州", "nkg": "南京", "syx": "三亚", "xmn": "厦门", "sha": "上海",
          "szx": "深圳", "she": "沈阳", "sjw": "石家庄", "tsn": "天津", "wuh": "武汉",
          "sia": "西安"}
route = "-bjs-szx?_=1"
date = "depdate=2023-02-15"
cabin = "cabin=Y_S_C_F"

# 将每次获取到的网页的html保存写入文件
# 使用selenium翻页
browser = webdriver.Chrome()  # 打开浏览器
url = base + route + "&" + date + "&" + cabin
print(url)
browser.get(url)  # 进入相关网站
time.sleep(3)  # 等待3s加载

# 点击提醒窗口
btn = browser.find_element(By.CLASS_NAME, "btn-group")
action = webdriver.ActionChains(browser)
action.click(btn)
action.perform()

time.sleep(3)  # 等待3s加载
# 滚轮滑动，获取剩余航班信息
js = "window.scrollBy(0,500)"  # 向下滑动500个像素
browser.execute_script(js)
time.sleep(1)
browser.execute_script(js)
time.sleep(1)
browser.execute_script(js)
time.sleep(1)
browser.execute_script(js)
time.sleep(1)
browser.execute_script(js)
time.sleep(1)
browser.execute_script(js)
time.sleep(1)
browser.execute_script(js)
time.sleep(1)

res = str(pq(browser.page_source))  # 获取网站源码
time.sleep(3)  # 休眠
with open("3.html", "w", encoding="utf-8") as f:
    f.write(res)

# 使用靓汤对其解析
soupi = BS(res, "html.parser")

# 4.1 获取所有航班信息
flights_info = soupi.find(name="div", attrs={"class": "flight-list root-flights"})
flights_list = flights_info.contents[0].contents

for val in flights_list:
    # 出发信息
    depart_info = val.find(name="div", attrs={"class": "depart-box"})
    depart_site = depart_info.find(name="div", attrs={"class": "airport"}).text
    depart_time = depart_info.find(name="div", attrs={"class": "time"}).text

    # 到达信息
    arrive_info = val.find(name="div", attrs={"class": "arrive-box"})
    arrive_site = arrive_info.find(name="div", attrs={"class": "airport"}).text
    arrive_time = arrive_info.find(name="div", attrs={"class": "time"}).text

    # 航司信息
    airline_info = val.find(name="div", attrs={"class": "flight-airline"})
    air_company = airline_info.find(name="div", attrs={"class": "airline-name"}).text
    plane_info = airline_info.find(name="span", attrs={"class": "plane-No"}).text

    # 价格信息
    air_price = val.find(name="div", attrs={"class": "price"}).text
    air_price_int = int(re.findall(r"\d+\.?\d*", air_price)[0])

commentNum = int(str(price_list[0]).split("(", 1)[1].split(')', 1)[0])
page = ceil(commentNum / 10)
# pageobj = soupi.find_all(name="b", attrs={"class": "numpage"});
print("pageobj")
print(page)

print("page=", page)

# 4.2 根据页数获取评论
comments = [];
for i in range(page):
    res = str(pq(browser.page_source))  # 获取网站源码
    # 使用靓汤对其解析
    soupi = BS(res, "html.parser")
    print("爬取第", (i + 1), "页评论...")
    # 滑倒页面底部，才能显示按钮和评论等
    js = "window.scrollTo(0,100000)"
    browser.execute_script(js)
    commentlinks = soupi.find_all(name="div", attrs={"class": "commentDetail"});
    for link in commentlinks:
        comments.append(link.get_text())
    # print("第",i,"页评论")
    # print(commentlinks)
    # 获取完后点击下一页，继续获取
    # 最后一页不翻页
    if i != (page - 1):
        browser.execute_script(
            "document.getElementsByClassName('ant-pagination-item-comment')[1].firstChild.click()")
        time.sleep(1)
        # browser.execute_script(
        #     "console.log(document.getElementsByClassName('ant-pagination-item-comment')[1].firstChild)")
        # # browser.find_element_by_class_name("ant-btn jumpButton").click();
        # time.sleep(1)
    # 休眠3s后更新html数据

# 5.整合解析的数据
tmp = {};

# 5.8 景点评论
tmp["comment"] = comments;
print(len(tmp["comment"]))
print("打印tmp", tmp["comment"]);
# 把评论写入csv中
df = pd.DataFrame({"评论": tmp["comment"]})
# index=False表示不写入索引
print("写入", placenames[k], ".csv")
df.to_csv(placenames[k] + ".csv", encoding='utf_8_sig', index=False)
