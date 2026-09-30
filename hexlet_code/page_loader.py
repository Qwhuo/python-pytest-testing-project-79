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
        for val in soup.find_all(["img", "script", "link"]):
            val_path = None
            attr = ""
            if "src" in val.attrs:
                val_path = val.get("src")
                attr = "src"
            if "href" in val.attrs:
                val_path = val.get("href")
                attr = "href"
            if val_path is None or (val_path.startswith("http") and urlsplit(val_path).hostname != urlsplit(page).hostname):
                continue
            val_path_abs = urljoin(page, val_path)
            obj_get = httpx.get(val_path_abs)
            if obj_get.status_code != httpx.codes.OK:
                warnings.warn("Image wasn't loaded")
                continue
            obj_cont = obj_get.content
            with open(save_dir / self.form_src_file_name(val_path_abs), "wb") as f:
                f.write(obj_cont)
            val[attr] = self.form_src_dir_name(page) + "/" + self.form_src_file_name(val_path_abs)
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
    def form_src_file_name(src):
        name = re.sub(r"(http|https):\/\/", "", src.lower())
        name = re.sub(r"\W", "-", name)
        ending = re.split("-", name)[-1]
        if ending not in ["css", "js", "png", "jpg", "jpeg", "svg", "mp4", "gif"]:
            ending = "-" + ending + ".html"
        else:
            ending = "." + ending
        name = "-".join(name.split("-")[:-1]) + ending
        return name

