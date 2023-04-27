from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
from dateutil import parser
import time
import json
import os


def convert2num(num):
    try:
        return int(num)
    except:
        try:
            return int(num.split()[0])
        except:
            return 0


def get_data(driver, url):
    driver.get(url)
    driver.implicitly_wait(1)

    total_dict = {}

    # question_title
    title = driver.find_element(By.XPATH, '//h1[@class="KPwZRb gKR4Fb"]').text
    # print("question_title:", title)

    # question_view_count
    view_count = driver.find_element(
        By.XPATH, '//div[@class="Nadu4b"]').get_attribute('innerText')
    view_count = convert2num(view_count)
    # print("question_view_count:", view_count)

    # sections
    section_lst = driver.find_elements(By.XPATH, '//div[@role="list"]/section')
    # print("list_number:", len(section_lst))

    for i in range(len(section_lst)):
        date = section_lst[i].find_element(
            By.XPATH, './/span[@class="zX2W9c"]').text
        date = parser.parse(date).isoformat()
        body = section_lst[i].find_element(
            By.XPATH, './/div[@class="ptW7te"]').get_attribute("innerText").strip()

        if i < 1:
            total_dict["Question_title"] = title
            total_dict["Question_created_time"] = date
            total_dict["Question_link"] = url
            total_dict["Question_answer_count"] = len(section_lst) - 1
            total_dict["Question_view_count"] = view_count
            total_dict["Question_body"] = body
            total_dict["Answer_list"] = []
            # print("question_time:", answer_time)
            # print("question_body:", answer_body)
        else:
            total_dict["Answer_list"].append({
                "Answer_created_time": date,
                "Answer_body": body
            })
            # print("answer_time:", answer_time)
            # print("answer_body:", answer_body)

    return total_dict


def get_url(driver):
    posts_url = []
    urls_lst = driver.find_elements(By.XPATH, '//div[@jscontroller="MAWgde"]')

    for url_node in urls_lst:
        post_url = url_node.find_element(
            By.XPATH, './/a[@class="ZLl54"]').get_attribute('href')
        posts_url.append(post_url)

    return posts_url


if __name__ == '__main__':
    driver = uc.Chrome()

    posts_url = []
    last_page = ''
    base_url = 'https://groups.google.com/g/mlflow-users'
    driver.get(base_url)

    while True:
        posts_url.extend(get_url(driver))
        if last_page == '-1':
            break

        next_button = driver.find_element(
            By.XPATH, '//div[@role="button" and @aria-label="Next page"]')
        next_button.click()

        time.sleep(1)

        last_page = next_button.get_attribute('tabindex')

    posts = []
    for post_url in posts_url:
        posts.append(get_data(driver, post_url))

    posts_json = json.dumps(posts, indent='\t')
    with open(os.path.join('..\Dataset\Tool-specific Others\Round#1\Raw', 'MLflow.json'), 'w') as f:
        f.write(posts_json)
