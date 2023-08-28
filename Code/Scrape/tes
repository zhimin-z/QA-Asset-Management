from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
from dateutil import parser
import pandas as pd
import time
import os
import re


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

    # question_title
    title = driver.find_element(By.XPATH, '//h1[@class="KPwZRb gKR4Fb"]').text
    # print("question_title:", title)

    # question_view_count
    view_count = driver.find_element(By.XPATH, '//div[@class="Nadu4b"]').get_attribute('innerText')
    view_count = convert2num(view_count)
    # print("question_view_count:", view_count)

    # question_answer_count
    section_lst = driver.find_elements(By.XPATH, '//div[@class="ptW7te"]')
    answer_count = len(section_lst) - 1
    # print("answer_count:", answer_count)
    
    # date
    date = driver.find_element(By.XPATH, '//span[@class="zX2W9c"]').text
    date = re.sub(r'\(.+\)', '', date)
    date = parser.parse(date).isoformat()
    # print("date:", date)
    
    #body
    body = section_lst[0].get_attribute("innerText").strip()
    #print("body:", body)

    post = {}            
    post["Question_title"] = title
    post["Question_created_time"] = date
    post["Question_link"] = url
    post["Question_comment_count"] = answer_count
    post["Question_view_count"] = view_count
    post["Question_body"] = body 

    return post


def get_url(driver):
    posts_url = set()
    urls_lst = driver.find_elements(By.XPATH, '//div[@class="yhgbKd"]')

    for url_node in urls_lst:
        post_url = url_node.get_attribute('data-rowid')
        posts_url.add(post_url)

    return posts_url


if __name__ == '__main__':
    driver = uc.Chrome()
    driver.implicitly_wait(5)
    
    base_url = 'https://groups.google.com/g/mlflow-users'
    driver.get(base_url)
    posts_url_lst = set()

    while True:
        posts_url = get_url(driver)
        posts_url_lst = posts_url_lst.union(posts_url)
        
        next_button = driver.find_element(By.XPATH, '//div[@role="button" and @aria-label="Next page"]')
        next_page = next_button.get_attribute('tabindex')
        if next_page == '-1':
            break
        next_button = next_button.find_element(By.XPATH, './/span[@class="DPvwYc sm8sCf"]')
        next_button.click()
        time.sleep(5)
        
    posts = pd.DataFrame()
    for post_url in posts_url_lst:
        post_url = base_url + '/c/' + post_url
        post = get_data(driver, post_url)
        post = pd.DataFrame([post])
        posts = pd.concat([posts, post], ignore_index=True)
    
    posts.to_json(os.path.join('../Dataset/Tool-specific', 'MLflow.json'), indent=4, orient='records')
