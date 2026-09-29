import os
from pathlib import Path
import warnings
from http.client import HTTPException
from bs4 import BeautifulSoup
import httpx
from urllib.parse import urljoin, urlsplit
import re



class PageLoader:
    def __init__(self):
        self.pages = {}

    def download(self, save_dir=os.getcwd(), page=None):
        if page is None:
            raise TypeError("Cannot download unknown page")
        page_content = httpx.get(page)
        if page_content.status_code != httpx.codes.OK:
            raise HTTPException(page_content.status_code)
        filename = self.form_file_name(page)
        p = Path(save_dir) / filename
        soup = BeautifulSoup(page_content.text, "html.parser")
        ###
        src_dir = Path(save_dir) / self.form_src_dir_name(page)
        src_dir.mkdir(parents=True, exist_ok=True)
        ext_soup = self.download_src(soup, page, src_dir).prettify()
        ###
        with open(p, "w") as f:
            f.write(ext_soup)
        self.pages[filename] = p
        return p

    def download_src(self, soup, page, save_dir):
        for img in soup.find_all("img"):
            img_path = img.get("src")
            if img_path is None:
                continue
            img_path_abs = urljoin(page, img_path)
            image_get = httpx.get(img_path_abs)
            if image_get.status_code != httpx.codes.OK:
                warnings.warn("Image wasn't loaded")
                continue
            image_cont = image_get.content
            with open(save_dir / self.form_src_file_name(page, img_path), "wb") as f:
                f.write(image_cont)
            img["src"] = self.form_src_dir_name(page) + "/" + self.form_src_file_name(page, img_path)
        return soup


    @staticmethod
    def form_file_name(src):
        name = re.sub(r"(http|https):\/\/", "", src.lower())
        name = re.sub(r"\W", "-", name)
        name += ".html"
        return name

    @staticmethod
    def form_src_dir_name(src):
        name = re.sub(r"(http|https):\/\/", "", src.lower())
        name = re.sub(r"\W", "-", name)
        name += "_files"
        return name

    @staticmethod
    def form_src_file_name(page, src):
        path_beg = urlsplit(page).hostname
        path_beg = re.sub(r"\W", "-", path_beg)
        name = re.sub(r"\/", "-", src.lower())
        name = path_beg + name
        return name

