from unittest.mock import Mock, patch, MagicMock
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

@pytest.fixture
def test_cont2():
    return """
    <!DOCTYPE html>
    <html lang="ru">
      <head>
        <meta charset="utf-8">
        <title>Курсы по программированию Хекслет</title>
        <link rel="stylesheet" media="all" href="https://cdn2.hexlet.io/assets/menu.css">
        <link rel="stylesheet" media="all" href="/assets/application.css">
        <link href="/courses" rel="canonical">
      </head>
      <body>
        <img src="/assets/professions/python.png" alt="Иконка профессии Python-программист">
        <h3>
          <a href="/professions/python">Python-программист</a>
        </h3>
        <script src="https://js.stripe.com/v3/"></script>
        <script src="https://ru.hexlet.io/packs/js/runtime.js"></script>
      </body>
    </html>
    """

@pytest.fixture
def test_cont2_corr():
    return """
    <!DOCTYPE html>
    <html lang="ru">
      <head>
        <meta charset="utf-8"/>
        <title>Курсы по программированию Хекслет</title>
        <link href="https://cdn2.hexlet.io/assets/menu.css" media="all" rel="stylesheet"/>
        <link href="ru-hexlet-io-courses_files/ru-hexlet-io-assets-application.css" media="all" rel="stylesheet"/>
        <link href="ru-hexlet-io-courses_files/ru-hexlet-io-courses.html" rel="canonical"/>
      </head>
      <body>
        <img alt="Иконка профессии Python-программист" src="ru-hexlet-io-courses_files/ru-hexlet-io-assets-professions-python.png"/>
        <h3>
          <a href="/professions/python">Python-программист</a>
        </h3>
        <script src="https://js.stripe.com/v3/"></script>
        <script src="ru-hexlet-io-courses_files/ru-hexlet-io-packs-js-runtime.js"></script>
      </body>
    </html>
    """


# @patch("hexlet_code.page_loader.httpx.get")
# def test_file_downloading(tmp_path):
#     downloaded = page_loader.download(page="https://habr.com", save_dir=tmp_path)
#     # with open(downloaded, "r") as f:
#     #     downloaded_page = f.read()
#     # assert page == downloaded_page
#     p = tmp_path / "habr-com.html"
#     assert downloaded == p


def test_errors():
    with pytest.raises(TypeError):
        page_loader.download()


@patch("hexlet_code.page_loader.httpx.get")
def test_not_standard_path(mock_get, test_cont, test_cont_corr, tmp_path):
    page_mock = MagicMock()
    page_mock.status_code = 200
    page_mock.text = test_cont
    tmp_mock = MagicMock()
    tmp_mock.status_code = 200
    tmp_mock.content = b"..."
    mock_get.side_effect = [
        page_mock,
        tmp_mock,
    ]
    page_loader.download(page="https://ru.hexlet.io/courses", save_dir=tmp_path)
    with open(os.path.join(tmp_path, "ru-hexlet-io-courses.html"), "r") as f:
        result = f.read()
    assert result == BeautifulSoup(test_cont_corr, "html.parser").prettify()


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
    name = ""
    for child in p.iterdir():
        name = child.name
        amt += 1
    assert amt == 1

    with open(os.path.join(tmp_path, "ru-hexlet-io-courses.html"), "r") as f:
        result = f.read()
    assert result == BeautifulSoup(test_cont_corr, "html.parser").prettify()
    with open(os.path.join(p, name), "r") as f:
        result2 = f.read()
    assert result2 == "..."


@patch("hexlet_code.page_loader.httpx.get")
def test_src_downloading(mock_get, test_cont2, test_cont2_corr, tmp_path):
    page_mock = Mock()
    page_mock.status_code = 200
    page_mock.text = test_cont2
    css_mock = Mock()
    css_mock.status_code = 200
    css_mock.content = b"..."
    css_mock2 = Mock()
    css_mock2.status_code = 200
    css_mock2.content = b"..."
    css_mock3 = Mock()
    css_mock3.status_code = 200
    css_mock3.content = b"..."
    image_mock = Mock()
    image_mock.status_code = 200
    image_mock.content = b"..."
    script_mock = Mock()
    script_mock.status_code = 200
    script_mock.content = b"..."
    script2_mock = Mock()
    script2_mock.status_code = 200
    script2_mock.content = b"..."
    mock_get.side_effect = [
        page_mock,
        css_mock,
        css_mock2,
        css_mock3,
        image_mock,
        script_mock,
        script2_mock
    ]

    page_loader.download(page="https://ru.hexlet.io/courses", save_dir=tmp_path)
    p = tmp_path / "ru-hexlet-io-courses_files"
    amt = 0
    js_file = ""
    for child in p.iterdir():
        amt += 1
        if child.name.endswith("js"):
            js_file = child.name
    assert amt == 4

    with open(os.path.join(tmp_path, "ru-hexlet-io-courses.html"), "r") as f:
        result = f.read()
    assert result == BeautifulSoup(test_cont2_corr, "html.parser").prettify()
    assert js_file == "ru-hexlet-io-packs-js-runtime.js"
    with open(os.path.join(p, js_file), "r") as f:
        result2 = f.read()
    assert result2 == "..."



