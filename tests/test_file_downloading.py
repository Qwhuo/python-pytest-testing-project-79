from unittest.mock import Mock, patch
import os
import pytest
from pathlib import Path
from hexlet_code.page_loader import PageLoader
from bs4 import BeautifulSoup

page_loader = PageLoader()

@pytest.fixture
def page():
    p = Path.cwd() / "tests" / "tests_data"
    webpage = p / "web_page1.txt"
    with open(webpage, "r") as f:
        file = f.read()
        return file

@pytest.fixture
def test_cont():
    return """
    <!DOCTYPE html>
    <html lang="ru">
      <head>
        <meta charset="utf-8">
        <title>Курсы по программированию Хекслет</title>
      </head>
      <body>
        <img src="/assets/professions/python.png" alt="Иконка профессии Python-программист">
        <h3>
          <a href="/professions/python">Python-программист</a>
        </h3>
      </body>
    </html>
    """

@pytest.fixture
def test_cont_corr():
    return """
    <!DOCTYPE html>
    <html lang="ru">
      <head>
        <meta charset="utf-8"/>
        <title>Курсы по программированию Хекслет</title>
      </head>
      <body>
        <img alt="Иконка профессии Python-программист" src="ru-hexlet-io-courses_files/ru-hexlet-io-assets-professions-python.png"/>
        <h3>
          <a href="/professions/python">Python-программист</a>
        </h3>
      </body>
    </html>
    """

def test_file_downloading(page, tmp_path):
    downloaded = page_loader.download(page="https://www.example.com", save_dir=tmp_path)
    with open(downloaded, "r") as f:
        downloaded_page = f.read()
    assert page == downloaded_page
    p = tmp_path / "www-example-com.html"
    assert downloaded == p


def test_errors():
    with pytest.raises(TypeError):
        page_loader.download()


@patch("hexlet_code.page_loader.httpx.get")
def test_not_standard_path(mock_get, tmp_path):
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = """
    <!DOCTYPE html>
    <html lang="en">
     <head>
      <title>
       Example Domain
      </title>
      <link href="data:," rel="icon"/>
      <meta content="width=device-width, initial-scale=1" name="viewport"/>
      <style>
       body{background:#eee;width:60vw;margin:15vh auto;font-family:system-ui,sans-serif}h1{font-size:1.5em}div{opacity:0.8}a:link,a:visited{color:#348}
      </style>
     </head>
    """
    p = Path.cwd()/"tests"/"tests_data"
    page_loader.download(page="https://www.example.com", save_dir=tmp_path)
    with open(os.path.join(tmp_path, "www-example-com.html"), "r") as f:
        result = f.read()
    with open(os.path.join(p, "web_page2.txt"), "r") as f:
        orig = f.read()
    assert result == orig


@patch("hexlet_code.page_loader.httpx.get")
def test_image_downloading(mock_get, tmp_path, test_cont, test_cont_corr):
    page_mock = Mock()
    page_mock.status_code = 200
    page_mock.text = test_cont
    image_mock = Mock()
    image_mock.status_code = 200
    image_mock.content = b"..."
    mock_get.side_effect = [
        page_mock,
        image_mock
    ]

    page_loader.download(page="https://ru.hexlet.io/courses", save_dir=tmp_path)
    p = tmp_path / "ru-hexlet-io-courses_files"
    amt = 0
    for child in p.iterdir():
        amt += 1
    assert amt == 1

    with open(os.path.join(tmp_path, "ru-hexlet-io-courses.html"), "r") as f:
        result = f.read()
    assert result == BeautifulSoup(test_cont_corr, "html.parser").prettify()


