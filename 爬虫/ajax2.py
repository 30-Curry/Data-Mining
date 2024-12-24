#encoding:utf-8
from selenium import webdriver
import time
import json
from selenium.webdriver.common.by import By




class BilBil:
    def __init__(self):
        self.start_url="https://www.bilibili.com/v/kichiku/guide/?spm_id_from=333.92.b_7072696d6172795f6d656e75.68#/"
        self.driver=webdriver.Chrome()

    def nextpage(self,driver):

        # 获取当前页面的高度
        last_height = driver.execute_script("return document.body.scrollHeight")

        # 模拟下拉操作，直到滑动到底部
        while True:
            # 模拟下拉操作
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # 等待页面加载
            time.sleep(2)

            # 获取当前页面的高度
            new_height = driver.execute_script("return document.body.scrollHeight")

            # 判断是否已经到达页面底部
            if new_height == last_height:
                break

            # 继续下拉操作
            last_height = new_height

    def get_content_list(self):
        li_list = self.driver.find_elements(By.XPATH,"//h3[@class='bili-video-card__info--tit']/a")
        content_list = []
        print(li_list)
        for li in li_list:
            item = {}
            x = li.text
            item["title"] =x
            print(x)

            content_list.append(item)
            # print(content_list)

        return content_list
    def save_content_list(self,content_list):
        with open("bilibili.txt","a",encoding="utf-8") as f:
            for content in content_list:
                f.write(json.dumps(content,ensure_ascii=False))
                f.write("\n")
    def run(self):
        self.driver.get(self.start_url)
        for i in range(0,3):
            self.nextpage(self.driver)
        content_list=self.get_content_list()
        self.save_content_list(content_list)


        self.driver.quit()

if __name__=="__main__":
    bilibili=BilBil()
    bilibili.run()