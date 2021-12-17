import os
import time

import requests
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        print("  func {}() takes {:.2f}s".format(method.__name__, (te - ts)))
        return result
    return timed


class Milan_Pics():
    def __init__(self):
        self.IF_DEBUG = True
        self.MORE = 1  # TODO
        self.rootdir = "{}/{}".format(os.path.dirname(os.path.realpath(__file__)), "pics")
        # define selectors will be used
        self.SELECTOR_LOAD_MORE = "button[class*='LoadMoreButton__StyledLoadButton']"
        self.SELECTOR_CATEGORIES = "a[class^='NewsItemSections__NewsItemLinkContainer']"
        self.SELECTOR_RIGHT_BUTTON = "div[class*='GalleryCarousel__ControlRight']>button"
        self.SELECTOR_IMG = "li[class*='GalleryCarousel__Slide']>span>img"

        if self.IF_DEBUG:
            print("initializing chromedriver, picture dir {}".format(self.rootdir))
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--window-size=1420,1080')
        # chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('log-level=1')

        self.driver = webdriver.Chrome(chrome_options=chrome_options)

        self.wait = WebDriverWait(self.driver, 10)
        self.wait_right_button = WebDriverWait(self.driver, 3)
        self.driver.get("https://www.acmilan.com/en/news/photogallery/latest")
        self.wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, self.SELECTOR_LOAD_MORE)))

    def create_pics_folder(self):
        if(not os.path.exists(self.rootdir)):
            print("creating {} folder".format(self.rootdir))
            os.mkdir(self.rootdir)

    def remove_empty_folders(self):
        for i in os.scandir(self.rootdir):
            if i.is_dir():
                files = [x for x in os.scandir(i.path)]
                if len(files) == 0:
                    print("remove folder {} due to no files".format(i.path))
                    os.rmdir(i.path)

    @ timeit
    def run(self):
        self.create_pics_folder()
        self.load_more()
        categories = self.driver.find_elements_by_css_selector(self.SELECTOR_CATEGORIES)
        l = [i.get_attribute('href') for i in categories]
        res = {'-'.join(i.split("/")[-2:]): i for i in l}

        keys = res.keys()
        for index, key in enumerate(keys, start=1):
            if self.IF_DEBUG:
                print("  run() --> {} out of {} categories, name: {}".format(index, len(keys), key))

            self.download_category(key, res[key])

        self.driver.close()
        self.remove_empty_folders()
        print(u"下载完成")

    def load_more(self):
        for i in range(self.MORE):
            load_more_button = self.driver.find_element_by_css_selector(
                self.SELECTOR_LOAD_MORE)

            load_more_button.location_once_scrolled_into_view
            load_more_button.click()

            self.wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, self.SELECTOR_LOAD_MORE), "LOADING..."))
            self.wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, self.SELECTOR_LOAD_MORE), "LOAD MORE"))

    @ timeit
    def category_pic_links(self, category_link):
        self.driver.get(category_link)
        self.wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, self.SELECTOR_RIGHT_BUTTON)))
        right_button = self.driver.find_element_by_css_selector(self.SELECTOR_RIGHT_BUTTON)
        while True:
            try:
                right_button.click()
                self.wait_right_button.until(EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, self.SELECTOR_RIGHT_BUTTON)))
            except TimeoutException:
                break
        links = self.driver.find_elements_by_css_selector(self.SELECTOR_IMG)
        download_urls = [i.get_attribute("src").replace("&auto=format", "") for i in links]
        return download_urls

    @ timeit
    def download_category(self, category_name, category_link):
        # download only if we do not have such folder in local
        if not os.path.exists("{}/{}".format(self.rootdir, category_name)):
            download_urls = self.category_pic_links(category_link)
            dir_path = "{}/{}".format(self.rootdir, category_name)
            os.mkdir(dir_path)
            file_path = "{}/url.txt".format(dir_path)
            with open(file_path, 'w') as f:
                f.write("\n".join(download_urls))
            f.close()
            if self.IF_DEBUG:
                print("  download_category() --> url file saved to {}".format(dir_path))

    def _download(self, category_name, download_urls):
        for link in download_urls:
            print(link)
            file_name = link.split("/")[-1]
            r = requests.get(link, allow_redirects=True)
            with open("{}/{}/{}".format(self.rootdir, category_name, file_name), 'wb') as f:
                f.write(r.content)


def write_to_bat_file():
    directory = "C:\\study\\milan\\app\\pics\\"
    my_list = [x[0] for x in os.walk(directory)]

    with open("C:\\study\\milan\\app\\pics\\run.bat", 'w') as f:
        for i in my_list[1:]:
            path = i.replace(directory, "")
            download_string = "aria2c.exe -j 10 -i {}/url.txt -d {}".format(path, path)
            print("  {}".format(download_string))
            f.write("{}\n".format(download_string))
    f.close()


if __name__ == "__main__":
    m = Milan_Pics()
    m.run()
    write_to_bat_file()
