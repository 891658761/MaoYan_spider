# -- coding: utf-8 --**
import datetime
import random
import time
import requests
import os
import emoji
from selenium.webdriver import Chrome
from tujian.tujian import base64_api
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
import Maoyan as Ma


class Comment:
    # 爬取评论=======================================================
    # 模拟滑块验证|
    def selenium_get_html(self,url):
        web = Chrome()
        web.get(url)
        time.sleep(1)
        slider = web.find_element(By.XPATH, '//*[@id="yodaBox"]')
        # 移动滑块
        img_big = web.find_element(By.XPATH, '//*[@id="yodaBoxWrapper"]')
        time.sleep(2)
        img_big.screenshot("a.png")
        img_path = "a.png"
        x = base64_api(uname='账号', pwd='密码', img=img_path, typeid=33)
        actions = ActionChains(web)  # 创建动作链
        actions.click_and_hold(slider).perform()  # 点击滑块，并保持点击动作
        sep = 0
        for step in range(0, 197, random.randint(3, 4)):
            sep += step
            web.maximize_window()
            ActionChains(web).move_by_offset(sep, 0).perform()
        actions.release().perform()  # 松开滑块，验证完成。
        # 判断释放验证成功
        tips = web.find_element(By.XPATH, '//*[@id="yodaSliderTip"]').text
        print(tips)
        while tips in ['操作速度过快']:
            # 移动滑块
            time.sleep(2)
            actions = ActionChains(web)  # 创建动作链
            actions.click_and_hold(slider).perform()  # 点击滑块，并保持点击动作
            sep = 0
            for step in range(0, 197, random.randint(3, 4)):
                sep += step
                web.maximize_window()
                ActionChains(web).move_by_offset(sep, 0).perform()
            actions.release().perform()  # 松开滑块，验证完成。
            # 判断释放验证成功
            tips = web.find_element(By.XPATH, '//*[@id="yodaSliderTip"]').text
        time.sleep(5)
        web.close()

    # 获取到网页数据
    def getUrlData(self,url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'
        }
        Data = requests.get(url, headers=headers)
        try:
            date_list = Data.json()
            return date_list['cmts']
        except:
            Ma.addLog(
                f'\n================={time.time()}===============\n网页数据获取失败\n================={time.time()}===============\n')

    # 保存数据到Csv
    def saveDataCsv(self,data_name, datas):
        for data in datas:
            # 处理数据
            data['content'] = data['content'].replace(" ", "")
            data['content'] = data['content'].replace("\n", "")
            data['content'] = data['content'].replace(",", "，")
            # 去除表情
            data['content'] = emoji.demojize(data['content'])
            data['nickName'] = emoji.demojize(data['nickName'])
            Ma.saveDataToMongoDb("Movie_db", "Comment_data", {
                "movieId": data['movieId'],
                "id": data['id'],
                "nickName": data['nickName'],
                "cityName": data['cityName'],
                "content": data['content'],
                "score": data['score'],
                "time": data['time']
            })
            Ma.saveDataToMySQL("Movie_db", "Comment_data",
                            f"'{data['movieId']}','{data['id']}','{data['nickName']}','{data['cityName']}','{data['content']}','{data['score']}','{data['time']}'")
            data = f"{data['movieId']},{data['id']},{data['nickName']},{data['cityName']},{data['content']},{data['score']},{data['time']}\n"
            if not os.path.exists(data_name + r'_data.csv'):
                f = open(data_name + r'_data.csv', mode='w', encoding='utf-8')
                f.write("movieId,comment_id,nickName,cityName,content,score,comment_time\n")
                f.write(data)
                f.close()
            else:
                f = open(data_name + r'_data.csv', mode='a', encoding='utf-8')
                f.write(data)
                f.close()

    # 评论主函数
    def getCommentMain(self):
        print('\n================【开启爬取评论】================')
        # 脚本运行时间计算
        star_time = time.time()
        # 获取当前时间，从当前时间往回读取评论数据|时间格式 2022-10-08 21:35:37 |
        curr_time = datetime.datetime.now()
        start_time = datetime.datetime.strftime(curr_time, '%Y-%m-%d %H:%M:%S')
        # 设置爬取总数，若达到对应数字则结束爬虫
        data_Size = Ma.needNum1
        now_Data_Size = 0
        # 电影id
        movie_id = 1224712
        # 测试专用
        Ma.delFile(f'{movie_id}_data.csv')
        while now_Data_Size <= data_Size:
            url = f'https://api.maoyan.com/mmdb/comments/movie/{movie_id}.json?_v_=yes&offset=1&startTime=' + start_time.replace(
                ' ', '%20')
            data = self.getUrlData(url)
            if data == []:
                print(f"时间节点为【{start_time}】的数据爬取失败|\nurl路径是{url}")
                start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S') + datetime.timedelta(hours=1)
                start_time = datetime.datetime.strftime(start_time, '%Y-%m-%d %H:%M:%S')  # 转换为str
                now_Data_Size += 15
            elif data is None:
                print(f"时间节点为【{start_time}】的数据爬取失败|\n正在模拟滑块验证")
                self.selenium_get_html(url)
            else:
                now_Data_Size += len(data)
                # 获取末尾评论时间
                over_time = data[-1]['startTime']
                print(
                    f"==当前已经爬取{now_Data_Size}条数据|正在爬取时间为【{start_time} ~ {over_time}】的数据==|url路径是")
                print(url)
                # 转换为datetime类型，减1秒，避免获取到重复数据
                start_time = datetime.datetime.strptime(over_time, '%Y-%m-%d %H:%M:%S') + datetime.timedelta(seconds=-1)
                start_time = datetime.datetime.strftime(start_time, '%Y-%m-%d %H:%M:%S')  # 转换为str
                # 保存数据
                self.saveDataCsv(str(data[0]['movieId']), data)
                time.sleep(0.1)
            # time.sleep(random.uniform(0.1, 0.2))
        end_time = time.time()
        run_time = round(end_time - star_time, 2)
        print('\n======================================================')
        print(
            f"爬虫运行结束|运行日志如下:\n【电影ID】:{movie_id}\n【共计爬取评论总数】:{now_Data_Size}\n【脚本运行时间】:{run_time}秒\n【保存文件名称】:{movie_id}_data.csv")
        print('======================================================')
        Ma.addLog(
            f'【电影ID】:{movie_id}\n【共计爬取评论总数】:{now_Data_Size}\n【脚本运行时间】:{run_time}秒\n【保存文件名称】:{movie_id}_data.csv')
    # 爬取评论=======================================================