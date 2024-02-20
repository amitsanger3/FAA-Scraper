import os, traceback
import requests
from bs4 import BeautifulSoup
from db_process import *
import config
from urllib.parse import urljoin


class FaaScraper(object):

    def __int__(self, base_img_url="https://images.fineartamerica.com/images/artworkimages/mediumlarge/"):
        self.img_num = 300
        self.base_img_url = base_img_url
        self.faa_url_db = FaaDatabase()

    @staticmethod
    def response(url):
        res = requests.get(url)
        print("PAGE RESPONSE: ", res.status_code, res.url)
        if res.status_code == 200 and res.url == url:
            return res
        return None

    @staticmethod
    def get_soup(content):
        return BeautifulSoup(content)

    @staticmethod
    def make_directory(dir_path):
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

    def url_uniqueness_check(self, url):
        return self.faa_url_db.gdelt_url_insert(url)

    def save_image(self, img_url, op_dir):

        if self.url_uniqueness_check(img_url):
            res = requests.get(img_url)
            print(res.status_code, img_url)
            if res.status_code == 200:
                fl = open(os.path.join(op_dir, f"{self.img_num}.jpg"), "wb")
                fl.write(res.content)
                fl.close()
                self.img_num += 1

    def scrape_faa(self):
        for url, category in config.FAA_URLS:
            op_dir = os.path.join(config.OP_DIR, category)
            self.make_directory(op_dir)
            url_num = 1
            while True:
                page_url = f"{url}{config.URL_EXT}{url_num}"
                print(url_num, " >>>>>>>>>>>>>>>>>>>>. ", page_url)
                url_num += 1
                res = self.response(page_url)

                if res:
                    if res.url == page_url:
                        soup = self.get_soup(res.content)
                        a_tags = soup.select(config.IMG_SELECTOR)
                        print("TOTAL A TAGS: ", len(a_tags))
                        if len(a_tags) > 0:
                            for a_t in a_tags:
                                try:
                                    img_data_url = a_t.attrs['data-src'].strip().split('/mediumlarge/')
                                    if len(img_data_url) > 1:
                                        img_url = urljoin(
                                            self.base_img_url,
                                            img_data_url[1])
                                        # print("*************** >>>>> ", img_url)
                                        self.save_image(img_url, op_dir)
                                except:
                                    print(traceback.print_exc(), "A TAGS ERROR !!!!!!!!!!1")
                                    pass
                        else:
                            break
                    else:
                        break
                else:
                    break
                # break


if __name__ == "__main__":
    faa = FaaScraper()
    faa.__int__(base_img_url="https://images.fineartamerica.com/images/artworkimages/mediumlarge/")
    faa.scrape_faa()
