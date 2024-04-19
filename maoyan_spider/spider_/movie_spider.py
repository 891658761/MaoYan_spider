# -- coding: utf-8 --**
import random
import time
import requests
import os
from selenium.webdriver import Chrome
import spider_.Maoyan as Ma
from tujian.tujian import base64_api
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from lxml import etree


class Movie_spider():
    # 爬取电影=======================================================
    # 计算步长
    def get_steps(self, dis):  # 模拟手动移动
        # 计算公式：v=v0+at, s=v0t+½at², v²-v0²=2as
        v = 0
        t = 0.3
        steps = []
        current = 0
        mid = dis / 2
        while current < dis:
            if current < mid:
                a = 2
            else:
                a = -2
            v0 = v
            s = v0 * t + 0.5 * a * (t ** 2)
            current += s
            steps.append(round(s))
            v = v0 + a * t
        return steps

    # 获取网页数据
    def getMovieData(self, url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0'
        }
        Data = requests.get(url, headers=headers)
        return Data.text

    # 保存数据到Csv
    def saveMovieDataCsv(self, data):
        if not os.path.exists('Movie_data.csv'):
            f = open('Movie_data.csv', mode='w', encoding='utf-8')
            f.write("title,score,types,actor,timer\n")
            f.write(data)
            f.close()
        else:
            f = open('Movie_data.csv', mode='a', encoding='utf-8')
            f.write(data)
            f.close()

    # 验证码
    def MovieCode(self, url):
        web = Chrome()
        web.get(url)
        time.sleep(1)
        iframe = web.find_element(By.XPATH, '//*[@id="tcaptcha_iframe"]')
        web.switch_to.frame(iframe)
        time.sleep(3)
        img_big = web.find_element(By.XPATH, '//*[@id="slideBgWrap"]')
        img_big.screenshot("a.png")
        img_path = "a.png"
        x = base64_api(uname=Ma.tujian_user, pwd=Ma.tujian_password, img=img_path, typeid=33)
        slider = web.find_element(By.XPATH, '//*[@id="tcaptcha_drag_thumb"]')
        # 移动滑块
        actions = ActionChains(web)  # 创建动作链
        actions.click_and_hold(slider).perform()  # 点击滑块，并保持点击动作
        time.sleep(0.5)
        steps = self.get_steps(float(x) - 41)
        for step in steps:
            ActionChains(web).move_by_offset(step, random.randint(-5, 5)).perform()
            time.sleep((random.randint(1, 2) / 1000))
        actions.release().perform()  # 松开滑块，验证完成。
        time.sleep(4)
        web.close()

    # 电影主函数
    def getMovieMain(self):
        print('\n================【开启爬取电影数据】================')
        # 脚本运行时间计算
        star_time = time.time()
        # 数据配置
        page = Ma.needNum2
        allPage = page * 30
        # 输出日志配置
        comment_num = 0
        ce_num = 0
        # 测试专用
        Ma.delFile("Movie_data.csv")
        for offset in range(0, allPage, 1):
            url = f'https://www.maoyan.com/films?catId=12&showType=3&offset={offset}'
            htmlData = self.getMovieData(url)
            htmlData = etree.HTML(htmlData)
            dds = htmlData.xpath('//*[@id="app"]/div/div[2]/div[2]/dl/dd')
            if not dds:
                allPage += 1
                ce_num += 1
                self.MovieCode(url)
                time.sleep(0.5)
            for dd in dds:
                title = dd.xpath('./div[2]/a/text()')[0]
                score = dd.xpath('./div[3]/text()')
                if not score:
                    score1 = dd.xpath('./div[3]/i[1]/text()')[0]
                    score2 = dd.xpath('./div[3]/i[2]/text()')[0]
                    score = f"{score1}{score2}"
                else:
                    score = score[0]
                types = dd.xpath('./div[1]/div[2]/a/div/div[2]/text()')[1].replace(" ", "").replace("\n", "")
                actor = dd.xpath('./div[1]/div[2]/a/div/div[3]/text()')[1].replace(" ", "").replace("\n", "")
                timer = dd.xpath('./div[1]/div[2]/a/div/div[4]/text()')[1].replace(" ", "").replace("\n", "")
                if not timer:
                    timer = "暂无上映时间"
                self.saveMovieDataCsv(f"{title}, {score}, {types}, {actor}, {timer}\n")
                Ma.saveDataToMongoDb("Movie_db", "Movie_data", {
                    "title": title,
                    "score": score,
                    "types": types,
                    "actor": actor,
                    "timer": timer
                })
                Ma.saveDataToMySQL("Movie_db", "Movie_data",
                                   f"'{title}', '{score}', '{types}', '{actor}', '{timer}',null")
                print("获取到电影【{}】的数据".format(title))
                comment_num += 1
        end_time = time.time()
        run_time = round(end_time - star_time, 2)
        print('\n======================================================')
        print(
            f"爬虫运行结束|运行日志如下:\n【共计爬取电影总数】:{comment_num}\n【被拦截次数】:{ce_num}\n【脚本运行时间】:{run_time}秒\n【保存文件名称】:Movie_data.csv")
        print('======================================================')
        Ma.addLog(
            f'【共计爬取电影总数】:{comment_num}\n【被拦截次数】:{ce_num}\n【脚本运行时间】:{run_time}秒\n【保存文件名称】:Movie_data.csv')
    # 爬取电影=======================================================
