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

    # question_title
    title = driver.find_element(
        By.XPATH, '//div[@data-test="question-title"]/h1').text
    # print("Title:", title)

    # Question_created_time
    data_json = driver.find_element(
        By.XPATH, '//script[@id="__NEXT_DATA__"]').get_attribute("innerText")
    data_dict = json.loads(data_json)
    date = data_dict["props"]["pageProps"]["question"]["createdAt"]
    # print("date:", date)

    # question_view_count
    view_count = driver.find_element(
        By.XPATH, '//div[@class="ant-typography ant-typography-ellipsis ant-typography-single-line ant-typography-ellipsis-single-line Avatar_age___5eSl"]/span').text
    view_count = convert2num(view_count)
    # print("question_view_count:", view_count)

    # Question_score_count
    upvote_count = driver.find_element(
        By.XPATH, '//div[@class="Vote_textContainer__5bmNJ"]').text
    upvote_count = convert2num(upvote_count)
    # print("Question_score_count:", upvote_count)

    # question_body
    body = driver.find_element(
        By.XPATH, '//div[@class="QuestionView_container__37ZXp"]//div[@class="custom-md-style"]').get_attribute("innerText").strip()
    # print("body:", body)

    # other_answers
    answers_lst = driver.find_elements(
        By.XPATH, '//div[@class="AnswerView_gridContainer__DDxNy"]')
    # print("answer_count:", len(answers_lst))

    answer_count = len(answers_lst)

    post = {}
    post["Question_title"] = title
    post["Question_created_time"] = date
    post["Question_link"] = url
    post["Question_score_count"] = upvote_count
    post["Question_view_count"] = view_count
    post["Question_answer_count"] = answer_count
    post["Question_body"] = body
    post['Question_closed_time'] = np.nan
    post['Answer_score_count'] = np.nan
    post['Answer_body'] = np.nan

    # question_has_accepted_answer
    try:
        driver.find_element(
            By.XPATH, '//div[@class="AnswerView_acceptedTag__MIxHg"]')
        has_accepted = True
    except:
        has_accepted = False
    # print("has_acceted:", has_accepted)
    
    if has_accepted:
        for i in range(answer_count):
            try:
                answers_lst[i].find_element(By.XPATH, './/div[@class="AnswerView_acceptedTag__MIxHg"]')
                post['Question_closed_time'] = data_dict["props"]["pageProps"]["question"]["answers"][i]["createdAt"]
                Answer_score_count = answers_lst[i].find_element(By.XPATH, './/div[@class="Vote_textContainer__5bmNJ"]').text
                post['Answer_score_count'] = convert2num(Answer_score_count)
                post['Answer_body'] = answers_lst[i].find_element(By.XPATH, './/div[@class="custom-md-style"]').get_attribute('innerText').strip()
                break
            except:
                continue

    return post


def get_url(driver, url):
    driver.get(url)

    posts_url = []
    urls_lst = driver.find_elements(
        By.XPATH, '//div[@class="QuestionCard_contentContainer__TjFsN QuestionCard_grid__yEHnj"]/a')
    for url_node in urls_lst:
        posts_url.append(url_node.get_attribute('href'))

    next_page_button = driver.find_element(
        By.XPATH, '//li[@title="Next Page"]')

    if next_page_button.get_attribute('aria-disabled') == 'true':
        return posts_url, ''

    next_page_url = next_page_button.find_element(
        By.XPATH, './/a').get_attribute('href')

    return posts_url, next_page_url


if __name__ == '__main__':
    driver = uc.Chrome()
    driver.implicitly_wait(2)

    next_page_url = 'https://repost.aws/tags/TAT80swPyVRPKPcA0rsJYPuA/amazon-sage-maker'
    cur_urls_lst = []

    while True:
        cur_urls, next_page_url = get_url(driver, next_page_url)
        cur_urls_lst.extend(cur_urls)

        if not next_page_url:
            break
    
    posts = pd.DataFrame()
    for post_url in cur_urls_lst:
        post = get_data(driver, post_url)
        post = pd.DataFrame([post])
        posts = pd.concat([posts, post], ignore_index=True)
        
    posts.to_json(os.path.join('Dataset/Tool-specific/Raw', 'Amazon SageMaker.json'), indent=4, orient='records')
    
