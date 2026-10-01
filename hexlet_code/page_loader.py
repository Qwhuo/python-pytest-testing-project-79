import os
from pathlib import Path
import logging
from http.client import HTTPException
from bs4 import BeautifulSoup
import httpx
from urllib.parse import urljoin, urlsplit
import re



logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s; %(levelname)s --> %(message)s")



def disable_logging():
    logging.disable(logging.CRITICAL)

def return_logging():
    logging.disable(logging.NOTSET)

class PageLoader:
    def __init__(self):
        self.pages = {}

    def download(self, save_dir=os.getcwd(), page=None, log_show=True):
        if log_show:
            return_logging()
        else:
            disable_logging()
        if page is None:
            logger.critical("No page specified")
            raise TypeError("Cannot download unknown page")
        page_content = httpx.get(page)
        if page_content.status_code != httpx.codes.OK:
            logger.error("Page request failed")
            raise HTTPException(page_content.status_code)
        filename = self.form_file_name(page)
        p = Path(save_dir) / filename
        soup = BeautifulSoup(page_content.text, "html.parser")
        ###
        src_dir = Path(save_dir) / self.form_src_dir_name(page)
        src_dir.mkdir(parents=True, exist_ok=True)
        logger.info("Directory %s was created", src_dir)
        ext_soup = self.download_src(soup, page, src_dir).prettify()
        ###
        with open(p, "w") as f:
            f.write(ext_soup)
        logger.info("File %s was saved", p)
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
                logger.warning("Source path %s is not valid", val_path)
                continue
            val_path_abs = urljoin(page, val_path)
            if urlsplit(val_path_abs).scheme not in ["http", "https"]:
                logger.warning("Invalid source path %s", val_path)
                continue
            obj_get = httpx.get(val_path_abs)
            if obj_get.status_code != httpx.codes.OK:
                logger.warning("Source %s wasn't loaded", val_path)
                continue
            obj_cont = obj_get.content
            with open(save_dir / self.form_src_file_name(val_path_abs), "wb") as f:
                f.write(obj_cont)
            logger.info("Src %s was saved to %s", val_path, save_dir / self.form_src_file_name(val_path_abs))
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

