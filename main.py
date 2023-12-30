from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json
from datetime import datetime

current_date = datetime.now().strftime("%Y_%m_%d")
WEIBO_HOT_URL = 'https://s.weibo.com/top/summary?cate=realtimehot'
FILE_PATH = f'data/weibo_hot_{current_date}.json'


def run():
    hots = get_weibo_hots()
    current_time = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    item_hots = parse_item_hots(hots)
    hots_data = get_existing_data()
    hots_data.append({'time': current_time, 'hots': item_hots})
    save_data(hots_data)
    update_readme(current_time)


def get_weibo_hots():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(WEIBO_HOT_URL)

    wait = WebDriverWait(driver, timeout=10)
    wait.until(EC.visibility_of_element_located((By.ID, 'pl_top_realtimehot')))

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    hots = soup.find(id='pl_top_realtimehot')
    return hots


def get_existing_data():
    try:
        with open(FILE_PATH, 'r', encoding='utf-8') as file:
            data_list = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data_list = []
    return data_list


def parse_item_hots(hots):
    item_list = []
    tr_elements = hots.find('tbody').find_all('tr')

    for tr in tr_elements:
        topic = tr.select_one('.td-02 a').text.strip()

        if tr.select_one('.td-01 i.icon-top'):
            rank = 0
            score = 0
            tag = 'top'
        else:
            rank_text = tr.select_one('.td-01').text.strip()
            score_text = tr.select_one('.td-02 span').text.strip()

            if not rank_text.isdigit():
                continue
            rank = int(rank_text)
            if score_text.isdigit():
                score = int(score_text)
                tag = ''
            else:
                result = score_text.split(' ')
                tag = result[0]
                score = int(result[1])

        item_list.append({'rank': rank, 'topic': topic,
                         'score': score, 'tag': tag})
    return item_list


def save_data(data):
    with open(FILE_PATH, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def update_readme(current_time):
    with open('README.md', 'r', encoding='utf-8') as file:
        lines = file.readlines()

    for i, line in enumerate(lines):
        if line.startswith('last update:'):
            lines[i] = f"last update: {current_time}\n"
            break

    with open('README.md', 'w', encoding='utf-8') as file:
        file.writelines(lines)


if __name__ == '__main__':
    run()
