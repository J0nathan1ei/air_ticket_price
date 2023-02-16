# -*- coding:utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer

engine = create_engine("mysql+pymysql://lpc:jona8931.@13.112.124.234:33067/air_ticket_prices", echo=True)
# 连接mysql数据库，echo为是否打印结果

Base = declarative_base()  # 生成orm基类


class User(Base):  # 继承生成的orm基类
    __tablename__ = "sql_test"  # 表名
    id = Column(Integer, primary_key=True)  # 设置主键
    user_name = Column(String(32))
    user_password = Column(String(64))


class Admin(Base):
    __tablename__ = "admin"
    id = Column(Integer, primary_key=True)
    username = Column(String(32))
    password = Column(String(64))


Base.metadata.create_all(engine)  # 创建表结构