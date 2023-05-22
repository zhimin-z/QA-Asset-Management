from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
import pandas as pd
import numpy as np
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

    # Question_created_time
    date = driver.find_element(By.XPATH, '//local-time[@format="datetime"]').get_attribute("datetime")
    # print("date:", date)

    # question_comment_count
    comment_count = driver.find_element(By.XPATH, '//span[@class="font-size-sm is-visually-hidden-mobile"]').text
    comment_count = convert2num(comment_count)
    # print("comment_count", comment_count)
    
    data_json = driver.find_element(
        By.XPATH, '//script[@type="application/ld+json"]').get_attribute("innerText")
    data_dict = json.loads(data_json)

    # question_title
    title = data_dict["mainEntity"]["name"]
    # print("Title:", title)

    # question_answer_count
    answer_count = data_dict["mainEntity"]["answerCount"]
    # print("answer_count:", answer_count)

    # question_score_count
    score_count = data_dict["mainEntity"]["upvoteCount"]
    # print("score_count:", score_count)

    # question_body
    body = data_dict["mainEntity"]["text"]
    # print("body:", body)

    post = {}
    post["Question_title"] = title
    post["Question_created_time"] = date
    post["Question_link"] = url
    post["Question_score_count"] = score_count
    post["Question_answer_count"] = answer_count
    post["Question_comment_count"] = comment_count
    post["Question_body"] = body
    post["Question_closed_time"] = np.nan
    post["Answer_score_count"] = np.nan
    post["Answer_comment_count"] = np.nan
    post["Answer_body"] = np.nan

    acceptedAnswer = data_dict["mainEntity"]["acceptedAnswer"]
    if acceptedAnswer:
        post["Answer_body"] = acceptedAnswer["text"]
        post["Answer_score_count"] = acceptedAnswer["upvoteCount"]
        answer = driver.find_element(By.XPATH, '//div[@class="card-content padding-none margin-none"]')
        post["Question_closed_time"] = answer.find_element(By.XPATH, './/local-time[@format="datetime"]').get_attribute("datetime")
        Answer_comment_count = answer.find_element(By.XPATH, './/span[@class="font-size-sm is-visually-hidden-mobile"]').text
        post["Answer_comment_count"] = convert2num(Answer_comment_count)
        
    return post


def get_url(driver, url):
    driver.get(url)

    urls_lst = []
    urls_node_lst = driver.find_elements(By.XPATH, '//h2[@class="title is-6 margin-bottom-xxs"]/a')

    for urls_node in urls_node_lst:
        urls_lst.append(urls_node.get_attribute('href'))

    return urls_lst, driver.current_url


if __name__ == '__main__':
    driver = uc.Chrome()
    driver.implicitly_wait(3)

    base_url = 'https://learn.microsoft.com/en-us/answers/tags/75/azure-machine-learning?page='
    posts_url_lst = []
    last_url = ''
    index = 0

    while True:
        index += 1
        cur_url = base_url + str(index)
        posts_url, ref_url = get_url(driver, cur_url)
        
        if ref_url == last_url:
            break
        
        posts_url_lst.extend(posts_url)
        last_url = cur_url
        
    posts = pd.DataFrame()
    for post_url in posts_url_lst:
        post = get_data(driver, post_url)
        post = pd.DataFrame([post])
        posts = pd.concat([posts, post], ignore_index=True)
    
    posts.to_json(os.path.join('../Dataset/Tool-specific/Raw', 'Azure Machine Learning.json'), indent=4, orient='records')
