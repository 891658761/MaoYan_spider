import datetime

import pymysql
from pymysql.cursors import DictCursor


class DBHelper:
    def __init__(self, database=None, host='localhost', port=3306, username='root', password='root'):
            self.conn = pymysql.connect(
                host=host,
                port=port,
                user=username,
                password=password,
                database=database
            )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self.conn.close()

    # 写入日志
    def addLog(self, text):
        logLocation = 'log.txt'
        curr_time = datetime.datetime.now()
        start_time = datetime.datetime.strftime(curr_time, '%Y-%m-%d %H:%M:%S')
        f = open(logLocation, mode='a', encoding='utf-8')
        f.write(f'\n================={start_time}===============\n')
        f.write(text)
        f.write(f'\n================={start_time}===============\n')
        f.close()

    def _change(self, sql,  *args, isInsert=False):
        cursor = self.conn.cursor()
        try:
            rownum = cursor.execute(sql, args)
            self.conn.commit()
            if isInsert:
                return cursor.lastrowid
            else:
                return rownum
        except Exception as e:
            print(e)
            self.addLog(f"Mysql写入出错:{e}")
            self.conn.rollback()
        finally:
            cursor.close()

    def insert(self, sql, *args):
        return self._change(sql, *args, isInsert=True)

    def update(self, sql, *args):
        return self._change(sql, *args)

    def delete(self, sql, *args):
        return self._change(sql, *args)

    def query_list(self, sql, *args):
        cursor = self.conn.cursor(DictCursor)
        try:
            cursor.execute(sql, args)
            result = cursor.fetchall()
            return result
        finally:
            cursor.close()

    def query_one(self, sql, *args):
        cursor = self.conn.cursor(DictCursor)
        try:
            cursor.execute(sql, args)
            result = cursor.fetchone()
            return result
        finally:
            cursor.close()


# if __name__ == '__main__':
#     with DBHelper("student") as db:
#         # result = db.query_list("select * from stu_info where name=%s and age = %s", "张三", 18)
#         # print(result)
#         # result = db.delete("delete from stu_info where id = %s", 7)
#         # print(result)
#         result = db.insert("insert into stu_info(name, age) values('李四海', 28)")
#         print(result)