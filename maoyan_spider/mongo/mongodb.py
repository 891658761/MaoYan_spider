import pymongo

def get_db(database):
    conn = pymongo.MongoClient(host='localhost', port=27017)
    # 切换数据库
    db = conn[database]
    return db

def add_one(db, table, data):
    result = db[table].insert_one(data)
    return result

def add_many(db, table, data_list):
    result = db[table].insert_many(data_list)
    return result

def upd(db, table, condition, data):
    # result = db[table].update_many(condition, {"$set": data})
    result = db[table].update_many(condition, {'$set':data})
    return result

def delete(db, table, condition):
    result = db[table].delete_many(condition)
    return result

def query(db, table, condition=''):
    result = db[table].find(condition)
    return result


if __name__ == '__main__':
    db = get_db("student")
    # result = add_one(db, 'stu_info', {'name': '张三', 'age': 800.0, 'address': '安徽省凤阳', 'score': 160.0})
    # result = add_many(db, 'stu_info', [{'name': '王五', 'age': 800.0, 'address': '安徽省凤阳', 'score': 160.0},{'name': '李四', 'age': 800.0, 'address': '安徽省凤阳', 'score': 160.0}])
    # 更新数据
    # result = upd(db, 'stu_info',  {'name': '张三'}, {'name': '张三1', 'age': 10})
    # result = delete(db, 'stu_info',  {'name': '王五'})
    # result = query(db, 'stu_info')
    result = query(db, 'stu_info' , {'name':'朱元璋'})
    print(list(result))