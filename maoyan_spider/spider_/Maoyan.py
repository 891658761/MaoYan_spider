# -- coding: utf-8 --**
import datetime
import os
from mongo import mongodb
from mysql import mysql

# 总配置
# 爬取评论数量(条)
needNum1 = 50
# 爬取电影数量(页)
needNum2 = 1
# 爬取资讯数量(页)
needNum3 = 1
# 日志路径
logLocation = 'log.txt'
# 是否写入Mondgdb数据库
writeMongo = False
# 是否写入MySQL数据库
writeMySQL = False

# 图鉴账号密码
tujian_user = "账号名"
tujian_password = "密码"

# 删除文件|仅用于测试
def delFile(fileName):
    if os.path.exists(fileName):
        os.remove(fileName)
        print(f"{fileName}文件已存在|删除成功")
# 写入日志
def addLog(text):
    curr_time = datetime.datetime.now()
    start_time = datetime.datetime.strftime(curr_time, '%Y-%m-%d %H:%M:%S')
    f = open(logLocation, mode='a', encoding='utf-8')
    f.write(f'\n================={start_time}===============\n')
    f.write(text)
    f.write(f'\n================={start_time}===============\n')
    f.close()
# 写入mongodb数据库
def saveDataToMongoDb(dbName, table, data):
    if not writeMongo:
        return
    db = mongodb.get_db(dbName)
    mongodb.add_one(db, table, data)
# 写入mysql数据库
def saveDataToMySQL(dbName, table, data):
    if not writeMySQL:
        return
    with mysql.DBHelper(dbName) as db:
        db.insert(f"insert into {table} values({data})")