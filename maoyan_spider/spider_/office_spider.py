import random
import time
import requests
import os
from selenium.webdriver import Chrome
from tujian.tujian import base64_api
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from lxml import etree
import Maoyan as Ma


class Office:
    # 爬取资讯=======================================================
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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'
        }
        Data = requests.get(url, headers=headers)
        return Data.text

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
    # 保存数据到Csv
    def saveNewsDataCsv(self, data):
        if not os.path.exists('News_data.csv'):
            f = open('News_data.csv', mode='w', encoding='utf-8')
            f.write("title,blurb,movie,writer,timer,viewNam,link\n")
            f.write(data)
            f.close()
        else:
            f = open('News_data.csv', mode='a', encoding='utf-8')
            f.write(data)
            f.close()

    def getOfficeMain(self):
        print('\n================【开启爬取资讯数据】================')
        # 脚本运行时间计算
        star_time = time.time()
        # 基本数据配置
        page = Ma.needNum3
        ire = page * 24
        news_num = 0
        # 测试专用
        Ma.delFile("News_data.csv")
        for i in range(0, ire, 12):
            url = f'https://www.maoyan.com/news?showTab=2&offset={i}'
            data = self.getMovieData(url)
            get = etree.HTML(data)
            lists = get.xpath('//*[@id="app"]/div/div[1]/div[1]/div')
            if not lists:
                i -= 12
                self.MovieCode(url)
            else:
                for list in lists:
                    title = list.xpath('./div/h4/a/text()')
                    if not title:
                        title = list.xpath('./h4/a/text()')
                    if not title:
                        continue
                    link = f"https://www.maoyan.com{list.xpath('./a/@href')[0]}"
                    count = "".join(list.xpath('./div/div[1]/text()')).replace(" ", "").replace("\n", "").replace("?",
                                                                                                                  "").replace(
                        ",", "")
                    if not count:
                        count = "暂无简介"
                    movie = list.xpath('./div/div[2]/div/span/a/text()')
                    if not movie:
                        movie = list.xpath('./div/div/div/span/a/text()')
                    movie = "".join(movie).replace(" ", "").replace("\n", "").replace("?", "").replace(",", "")
                    writer = list.xpath('./div/div[2]/span[1]/text()')
                    if not writer:
                        writer = list.xpath('./div/div/span[1]/text()')
                    timer = list.xpath('./div/div[2]/span[2]/text()')
                    if not timer:
                        timer = list.xpath('./div/div/span[2]/text()')
                    viewNam = list.xpath('./div/div[2]/span[3]/text()')
                    if not viewNam:
                        viewNam = list.xpath('./div/div/span[3]/text()')
                    print(f"爬取到资讯【{title}】")
                    # print(f"数据汇报:\n【标题】:{title[0]}\n【简介】:{count}\n【电影名称】:{movie}\n【作者】:{writer[0]}\n【发布时间】:{timer[0]}\n【观看人数】:{viewNam[0]}\n【链接】:{link}\n\n")
                    self.saveNewsDataCsv(f"{title[0]},{count},{movie},{writer[0]},{timer[0]},{viewNam[0]},{link}\n")
                    Ma.saveDataToMongoDb("Movie_db", "News_data", {
                        "title": title[0],
                        "count": count,
                        "movie": movie,
                        "writer": writer[0],
                        "timer": timer[0],
                        "viewNam": viewNam[0],
                        "link": link
                    })
                    Ma.saveDataToMySQL("Movie_db", "News_data",
                                    f"null,'{title[0]}','{count}','{movie}','{writer[0]}','{timer[0]}','{viewNam[0]}','{link}'")
                    news_num += 1
        end_time = time.time()
        run_time = round(end_time - star_time, 2)
        print('\n======================================================')
        print(
            f"爬虫运行结束|运行日志如下:\n【共计爬取资讯总数】:{news_num}\n【脚本运行时间】:{run_time}秒\n【保存文件名称】:News_data.csv")
        print('======================================================')
        Ma.addLog(f'【共计爬取资讯总数】:{news_num}\n【脚本运行时间】:{run_time}秒\n【保存文件名称】:News_data.csv')
    # 爬取资讯=======================================================