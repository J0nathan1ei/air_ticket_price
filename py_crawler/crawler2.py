# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup as BS
import time
from selenium import webdriver
from pyquery import PyQuery as pq
import pandas as pd
from math import ceil

"""从网上爬取数据"""
# 请求头
headers = {
    "Origin": "https://piao.ctrip.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
}

# places = ["zhuhai27"]
# 地名，用来保存在输出文件的名称
placenames = ["岐澳古道", "五桂山", "唐家湾古镇", "会同村"]
# 携程网的url
base = "https://you.ctrip.com/sight/";
# suffixUrl = "zhongshan233/5631357.html";
# url的后缀，依次保存对应景点的url
suffixUrl = ["zhongshan233/5631357.html", "zhongshan233/23029.html", "zhuhai27/1511281.html", "zhuhai27/122391.html"];

# 将每次获取到的网页的html保存写入文件

# 使用selenium翻页
browser = webdriver.Chrome()  # 打开浏览器
for k in range(len(placenames)):

    browser.get(base + suffixUrl[k])  # 进入相关网站
    print(placenames[k])
    print(base + suffixUrl[k])
    res = str(pq(browser.page_source))  # 获取网站源码
    # print(res)
    time.sleep(3);  # 休眠

    with open("3.html", "w", encoding="utf-8") as f:
        f.write(res)

    # 使用靓汤对其解析
    soupi = BS(res, "html.parser")
    # 1.景点介绍
    # vis = soupi.find_all(name="div", attrs={"class": "text_style"});
    # introduce = []
    # for i in range(len(vis)):
    #     introduce.append(vis[i].get_text())
    # 2.图片的url
    # imgs = [];
    # imglinks = soupi.find_all(name="img", attrs={"width": "350"})
    # print(imglinks)
    # for img in imglinks:
    #     imgs.append(img.attrs["src"])
    # 3.评分
    # score = soupi.find(name="span", attrs={"class": "score"}).b.get_text()
    # scores = [];
    # 3.1 把总体评分加入
    # scores.append(score);
    # 3.2 把分评分加入，景色，趣味，性价比
    # scorelinks = soupi.find(name="dl", attrs={"class": "comment_show"}).find_all(name="dd")
    # for link in scorelinks:
    #     scores.append(link.find(name="span", attrs={"class": "score"}).string)

    '''
    这里使用靓汤依次解析，并保存到评论中
    '''
    # 4.评论

    # 4.1 获取页数
    pagediv = soupi.find(name="div", attrs={"class": "commentModule normalModule"})
    pageobj = pagediv.find_all(name="div", attrs={"class": "moduleTitle"})
    commentNum = int(str(pageobj[0]).split("(", 1)[1].split(')', 1)[0])
    page = ceil(commentNum/10)
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

    # comments = [];
    # commentlinks = soupi.find_all(name="span", attrs={"class": "heightbox"});
    # for link in commentlinks:
    #     comments.append(link.get_text())


    # 5.整合解析的数据
    tmp = {};
    # 5.1 景点id
    # 5.2 景点名字
    # tmp["name"] = soupi.find(name="div", attrs={"class": "f_left"}).find(name="h1").find_all(name="a")[0].string;
    # tmp["name"] = tmp["name"].replace(" ", "").replace("\n", "");
    # tmp["introduce"] = introduce
    # 5.4 景点总体评分
    # tmp["score"] = scores;
    # 5.5 景点位置
    # tmp["position"] = soupi.find_all(name="p", attrs={"class": "s_sight_addr"})[0].string;
    # tmp["position"] = tmp["position"].replace(" ", "").replace("\n", "").split("：", 1)[1];
    # 5.6 景点图片的url
    # tmp["img"] = imgs
    # 5.7 景点等级
    # tmp["grade"] = soupi.find_all(name="span", attrs={"class": "s_sight_con"})[0].get_text()
    # tmp["grade"] = tmp["grade"].replace(" ", "").replace("\n", "")
    # 5.8 景点评论
    tmp["comment"] = comments;
    print(len(tmp["comment"]))
    print("打印tmp", tmp["comment"]);
    # 把评论写入csv中
    df = pd.DataFrame({"评论": tmp["comment"]})
    # index=False表示不写入索引
    print("写入",placenames[k],".csv")
    df.to_csv(placenames[k] + ".csv", encoding='utf_8_sig', index=False)