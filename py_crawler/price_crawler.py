# -*- coding: utf-8 -*-
# python 3.11.0

import json
import time
import random
import datetime
import sqlalchemy
import urllib.request
import pandas as pd
from operator import itemgetter
from dateutil.parser import parse


class FLIGHT(object):
    def __init__(self):
        self.Airline = {}  # 航空公司代码
        self.engine = sqlalchemy.create_engine("mssql+pymssql://kk:kk@HZC/Myspider")
        self.url = ''
        self.headers = {}
        self.city={"bjs":"北京","ckg":"重庆","ctu":"成都","cgq":"长春","csx":"长沙",
        "dlc":"大连","can":"广州","kwe":"贵阳","kwl":"桂林","hrb":"哈尔滨",
        "hgh":"杭州","hfe":"合肥","het":"呼和浩特","tna":"济南","kmg":"昆明",
        "lhw":"兰州","nkg":"南京","syx":"三亚","xmn":"厦门","sha":"上海",
        "szx":"深圳","she":"沈阳","sjw":"石家庄","tsn":"天津","wuh":"武汉",
        "sia":"西安"}
        self.UserAgent = [
            "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.36 Safari/535.7",
            "Mozilla/5.0 (Windows NT 6.2; Win64; x64; rv:16.0) Gecko/16.0 Firefox/16.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/534.55.3 (KHTML, like Gecko) Version/5.1.3 Safari/534.53.10",
            "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
            "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
            "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1500.55 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1309.0 Safari/537.17"
            "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b13pre) Gecko/20110307 Firefox/4.0b13pre",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:16.0) Gecko/20100101 Firefox/16.0",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11"
        ]

    # 遍历两个日期间的所有日期
    def set_url_headers(self, startdate, enddate):
        startDate = datetime.datetime.strptime(startdate, '%Y-%m-%d')
        endDate = datetime.datetime.strptime(enddate, '%Y-%m-%d')
        while startDate <= endDate:
            today = startDate.strftime('%Y-%m-%d')
            for fromcode, fromcity in sorted(self.city.items(), key=itemgetter(0)):
                for tocode, tocity in sorted(self.city.items(), key=itemgetter(0)):
                    if fromcode != tocode:
                        self.url = 'https://flights.ctrip.com/online/list/oneway-%s-%s?_=1&depdate=%s&cabin=Y_S_C_F' % (
                        str.lower(fromcode), str.lower(tocode), today)
                        self.headers = {
                            "Host": "flights.ctrip.com",
                            "User-Agent": random.choice(self.UserAgent),
                            "Referer": "https://flights.ctrip.com/booking/%s-%s-day-1.html?DDate1=%s" % (
                            fromcode, tocode, today),
                            "Connection": "keep-alive",
                        }
                        print("%s : %s(%s) ==> %s(%s) " % (today, fromcity, fromcode, tocity, tocode))
                        self.get_parse_json_data(today)
                time.sleep(10)
            startDate += datetime.timedelta(days=1)

    # 获取一个页面中的数据
    def get_one_page_json_data(self):
        req = urllib.request.Request(self.url, headers=self.headers)
        body = urllib.request.urlopen(req, timeout=30).read().decode('utf-8')
        jsonData = json.loads(body.strip("'<>() ").replace('\'', '\"'))
        return jsonData

    # 获取一个页面中的数据，解析保存到数据库
    def get_parse_json_data(self, today):
        jsonData = self.get_one_page_json_data()
        df = pd.DataFrame(
            columns=['ItinerarDate', 'Airline', 'AirlineCode', 'FlightNumber', 'FlightNumberS', 'Aircraft',
                     'AircraftSize'
                , 'AirportTax', 'FuelOilTax', 'FromCity', 'FromCityCode', 'FromAirport', 'FromTerminal', 'FromDateTime',
                     'ToCity', 'ToCityCode', 'ToAirport'
                , 'ToTerminal', 'ToDateTime', 'DurationHour', 'DurationMinute', 'Duration', 'Currency', 'TicketPrices',
                     'Discount', 'PunctualityRate', 'AircraftCabin'])

        if bool(jsonData["fis"]):
            # 获取航空公司代码及公司名称
            company = jsonData["als"]
            for k in company.keys():
                if k not in self.Airline:
                    self.Airline[k] = company[k]

            index = 0
            for data in jsonData["fis"]:
                df.loc[index, 'ItinerarDate'] = today  # 行程日期
                # df.loc[index,'Airline'] = self.Airline[data["alc"].strip()] #航空公司
                df.loc[index, 'Airline'] = self.Airline[data["alc"].strip()] if (
                            data["alc"].strip() in self.Airline) else None  # 航空公司
                df.loc[index, 'AirlineCode'] = data["alc"].strip()  # 航空公司代码
                df.loc[index, 'FlightNumber'] = data["fn"]  # 航班号
                df.loc[index, 'FlightNumberS'] = data["sdft"]  # 共享航班号(实际航班)
                df.loc[index, 'Aircraft'] = data["cf"]["c"]  # 飞机型号
                df.loc[index, 'AircraftSize'] = data["cf"]["s"]  # 型号大小(L大;M中;S小)
                df.loc[index, 'AirportTax'] = data["tax"]  # 机场建设费
                df.loc[index, 'FuelOilTax'] = data["of"]  # 燃油税
                df.loc[index, 'FromCity'] = data["acn"]  # 出发城市
                df.loc[index, 'FromCityCode'] = data["acc"]  # 出发城市代码
                df.loc[index, 'FromAirport'] = data["apbn"]  # 出发机场
                df.loc[index, 'FromTerminal'] = data["asmsn"]  # 出发航站楼
                df.loc[index, 'FromDateTime'] = data["dt"]  # 出发时间
                df.loc[index, 'ToCity'] = data["dcn"]  # 到达城市
                df.loc[index, 'ToCityCode'] = data["dcc"]  # 到达城市代码
                df.loc[index, 'ToAirport'] = data["dpbn"]  # 到达机场
                df.loc[index, 'ToTerminal'] = data["dsmsn"]  # 到达航站楼
                df.loc[index, 'ToDateTime'] = data["at"]  # 到达时间
                df.loc[index, 'DurationHour'] = int((parse(data["at"]) - parse(data["dt"])).seconds / 3600)  # 时长(小时h)
                df.loc[index, 'DurationMinute'] = int(
                    (parse(data["at"]) - parse(data["dt"])).seconds % 3600 / 60)  # 时长(分钟m)
                df.loc[index, 'Duration'] = str(df.loc[index, 'DurationHour']) + 'h' + str(
                    df.loc[index, 'DurationMinute']) + 'm'  # 时长(字符串)
                df.loc[index, 'Currency'] = None  # 币种
                df.loc[index, 'TicketPrices'] = data["lp"]  # 票价
                df.loc[index, 'Discount'] = None  # 已打折扣
                df.loc[index, 'PunctualityRate'] = None  # 准点率
                df.loc[index, 'AircraftCabin'] = None  # 仓位(F头等舱;C公务舱;Y经济舱)
                index = index + 1
            df.to_sql("KKFlight", self.engine, index=False, if_exists='append')
            print("done!~")


if __name__ == "__main__":
    fly = FLIGHT()
    fly.set_url_headers('2023-02-16', '2023-02-16')
