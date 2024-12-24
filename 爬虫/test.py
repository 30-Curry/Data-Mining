import json
import re

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

class CtripScraper:
    def __init__(self, driver_path, url):
        self.driver = self._init_driver(driver_path)
        self.url = url
        self.records = []
        self.original_window = None
        self.scroll_pause_time = 0.5

    def _init_driver(self, driver_path):
        service = webdriver.EdgeService(executable_path=driver_path)
        return webdriver.Edge(service=service)

    def start_scraping(self):
        self.driver.get(self.url)
        self.original_window = self.driver.current_window_handle
        processed_row_count = 139

        #统计4页的数据
        for i in range(5):
            self._scroll_to_load_more()
        for num in range(1):
            rows = self._get_rows()
            print('length of total rows',len(rows))
            if len(rows) <= processed_row_count:
                print("没有新的内容加载，结束循环")
                break

            new_rows = rows[processed_row_count:]
            print('length of total new_rows', len(new_rows))
            for row in new_rows:
                self._process_row(row)

            processed_row_count = len(rows)


        self.driver.quit()
        self._save_to_excel()

    def _get_rows(self):
        return WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".forfall .city"))
        )

    def _process_row(self, row):
        title = row.find_element(By.CSS_SELECTOR, '.city-sub .cpt').text
        city = row.find_element(By.CSS_SELECTOR, '.city-sub .city-name').text
        time_info = row.find_element(By.CSS_SELECTOR, '.author .time').text
        author_name = row.find_elements(By.CSS_SELECTOR, '.author a')[1].text

        travel_link = row.find_element(By.CSS_SELECTOR, 'a.city-image')
        travel_link.click()

        WebDriverWait(self.driver, 10).until(lambda d: len(d.window_handles) > 1)
        new_window = [window for window in self.driver.window_handles if window != self.original_window][0]
        self.driver.switch_to.window(new_window)

        trip_content = self._get_trip_content()
        comments = self._get_comments()

        # 清理非法字符
        trip_content = self._remove_illegal_characters(trip_content)
        comments = self._remove_illegal_characters(json.dumps(comments, ensure_ascii=False))

        # 将记录添加到列表中
        self.records.append({
            "title": title,
            'city': city,
            "time": time_info,
            "author_name": author_name,
            "trip_content": trip_content,
            "comments": comments
        })

        print(f'title:{title}')
        print(f'city:{city}')
        print(f'time_info:{time_info}')
        print(f'author_name:{author_name}')
        print(f'trip_content:{trip_content}')
        print(f'comments:{comments}')
        print(f'length of comments:{len(comments)}')

        self.driver.close()
        self.driver.switch_to.window(self.original_window)

    def _get_trip_content(self):
        try:
            trip_content_list = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".ctd_content p"))
            )
            trip_content=''.join([i.text for i in trip_content_list]).replace(' ','')
            return trip_content
        except Exception:
            return "N/A"

    def _get_comments(self):
        comments = {}
        n = 1
        while True:
            try:
                comments_list = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#replyboxid .ctd_comments_box.cf .textarea_box.fr .ctd_comments_text"))
                )

                for com in comments_list:
                    comments[f'评论{n}'] = com.text
                    n += 1

                next_page = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "#replyboxid .pager_v1 .nextpage"))
                )
                self.driver.execute_script("arguments[0].scrollIntoView();", next_page)
                self.driver.execute_script("arguments[0].click();", next_page)

                WebDriverWait(self.driver, 10).until(
                    EC.staleness_of(comments_list[0])
                )
                time.sleep(1)
            except Exception:
                print("已到达最后一页或找不到翻页按钮。")
                break
        return comments

    def _scroll_to_load_more(self):
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(self.scroll_pause_time)

        new_height = self.driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            print("没有新的内容加载，结束循环")

    def _remove_illegal_characters(self, text):
        # 移除非法字符，范围是 ASCII 0-31 和 127
        return re.sub(r'[\x00-\x1F\x7F]', '', text)

    def _save_to_excel(self):
        df = pd.DataFrame(self.records)
        df.to_excel(r"C:\Users\Lenovo\Desktop\Xie Cheng1.xlsx")

if __name__ == "__main__":
    driver_path = r"D:\Application\Anaconda\Lib\site-packages\selenium\webdriver\edge\edgedriver_win64\msedgedriver.exe"
    url = "https://you.ctrip.com/travels/"
    scraper = CtripScraper(driver_path, url)
    scraper.start_scraping()
