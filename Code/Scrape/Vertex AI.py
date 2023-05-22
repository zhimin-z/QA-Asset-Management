from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
from dateutil import parser
import pandas as pd
import numpy as np
import os


def convert2num(num):
    try:
        return int(num)
    except:
        try:
            return int(num.split()[0])
        except:
            return 0


def convert2date(date):
    try:
        return parser.parse(date.strip('‎')).isoformat()
    except:
        return ''


def get_data(driver, url):
    driver.get(url)

    # question_title
    title = driver.find_element(
        By.XPATH, '//div[@class="lia-message-subject"]').text
    # print("Title:", title)

    # Question_created_time
    date = driver.find_element(
        By.XPATH, '//span[@class="local-friendly-date"]').get_attribute('title')
    date = convert2date(date)
    # print("date:", date)

    # Question_score_count
    upvote_count = driver.find_element(
        By.XPATH, '//span[@class="message-stat kudos-stat"]').text
    upvote_count = convert2num(upvote_count)
    # print("upvote_count", upvote_count)

    # question_view_count
    view_count = driver.find_element(
        By.XPATH, '//span[@class="message-stat views-stat"]').text
    view_count = convert2num(view_count)
    # print("view_count", view_count)

    # question_answer_count
    answer_count = driver.find_elements(
        By.XPATH, '//div[@class="message-stat replies-stat"]').text
    answer_count = convert2num(answer_count)
    # print("len:", len(answers_lst))

    # question_body
    comments = driver.find_elements(By.XPATH, '//div[@class="lia-quilt lia-quilt-forum-message lia-quilt-layout-custom-message"]')
    body = comments[0].get_attribute('innerText').strip()
    # print("body:", body)

    post = {}
    post["Question_title"] = title
    post["Question_created_time"] = date
    post["Question_link"] = url
    post["Question_answer_count"] = answer_count
    post["Question_score_count"] = upvote_count
    post["Question_view_count"] = view_count
    post["Question_body"] = body
    post['Question_closed_time'] = np.nan
    post['Answer_score_count'] = np.nan
    post['Answer_body'] = np.nan
    
    # question_has_accepted_answer
    has_accepted = False
    try:
        driver.find_element(
            By.XPATH, '//div[@class="custom-google-accepted-solution root"]')
        has_accepted = True
    except:
        has_accepted = False
    # print("has_acceted:", has_accepted)
    
    if has_accepted:
        post['Question_closed_time'] = comments[1].find_element(
            By.XPATH, './/span[@class="local-friendly-date"]').get_attribute('title')
        Answer_score_count = comments[1].find_element(
                By.XPATH, './/div[@class="message-stat kudos-stat').text
        post['Answer_score_count'] = convert2num(Answer_score_count)
        post['Answer_body'] = comments[1].get_attribute('innerText').strip()

    return post


def get_url(driver, url):
    driver.get(url)

    posts_url = []
    urls_lst = driver.find_elements(
        By.XPATH, '//h5[@class="message-subject"]/a')
    for url_node in urls_lst:
        posts_url.append(url_node.get_attribute('href'))

    return posts_url, driver.current_url


if __name__ == '__main__':
    driver = uc.Chrome()
    driver.implicitly_wait(1)

    base_url = 'https://www.googlecloudcommunity.com/gc/AI-ML/bd-p/cloud-ai-ml/page/'
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
    for post_url in posts_url:
        post = get_data(driver, post_url)
        post = pd.DataFrame([post])
        posts = pd.concat([posts, post], ignore_index=True)

    posts.to_json(os.path.join('Dataset/Tool-specific/Raw', 'Vertex AI.json'), indent=4, orient='records')
