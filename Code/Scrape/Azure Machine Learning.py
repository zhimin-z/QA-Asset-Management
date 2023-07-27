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
            return int(num.strip().split()[0])
        except:
            return 0


def get_data(driver, url):
    driver.get(url)

    # Question_created_time
    date = driver.find_element(By.XPATH, '//local-time[@format="datetime"]').get_attribute("datetime")
    # print("date:", date)

    # question_comments
    question_comments = driver.find_element(By.XPATH, '//div[@class="expandable is-expanded"]')
    Question_comment_score = question_comments.find_elements(By.XPATH, './/button[@class="comment-vote button button-clear text-decoration-none has-inner-focus margin-bottom-none button-primary button-sm sign-in-modal "]')
    comment_score = sum([convert2num(score.get_attribute("data-vote-count")) for score in Question_comment_score])
    comments = question_comments.find_elements(By.XPATH, './/div[@class="content font-size-sm"]')
    
    # question_tag_count
    tag_count = len(driver.find_elements(By.XPATH, '//details[@class="popover popover-left"]'))
    # print("tag_count:", tag_count)
    
    data_json = driver.find_element(
        By.XPATH, '//script[@type="application/ld+json"]').get_attribute("innerText")
    data_dict = json.loads(data_json)
    question = data_dict["mainEntity"]

    # question_title
    title = question["name"]
    # print("Title:", title)

    # question_answer_count
    answer_count = question["answerCount"]
    # print("answer_count:", answer_count)

    # question_score_count
    score_count = question["upvoteCount"]
    # print("score_count:", score_count)

    # question_body
    body = question["text"]
    # print("body:", body)

    post = {}
    post["Question_title"] = title
    post["Question_tag_count"] = tag_count
    post["Question_created_time"] = date
    post["Question_link"] = url
    post["Question_score_count"] = score_count
    post["Question_answer_count"] = answer_count
    post["Question_comment_count"] = len(comments)
    post["Question_comment_body"] = ' '.join([comment.text for comment in comments])
    post["Question_comment_score"] = comment_score
    post["Question_body"] = body
    post["Question_closed_time"] = np.nan
    post["Answer_score_count"] = np.nan
    post["Answer_comment_count"] = np.nan
    post["Answer_body"] = np.nan
    post["Question_self_closed"] = np.nan

    acceptedAnswer = question["acceptedAnswer"]
    if acceptedAnswer:
        post["Answer_body"] = acceptedAnswer["text"]
        post["Answer_score_count"] = acceptedAnswer["upvoteCount"]
        post["Question_self_closed"] = acceptedAnswer["authorId"] == question["authorId"]
        answer = driver.find_element(By.XPATH, '//div[@class="card-content padding-none margin-none"]')
        post["Question_closed_time"] = answer.find_element(By.XPATH, './/local-time[@format="datetime"]').get_attribute("datetime")
        Answer_comment_count = answer.find_element(By.XPATH, './/span[@class="font-size-sm is-visually-hidden-mobile"]').text
        post['Answer_comment_count'] = convert2num(Answer_comment_count)
        Answer_comment_score = answer.find_elements(By.XPATH, './/button[@class="comment-vote button button-clear text-decoration-none has-inner-focus margin-bottom-none button-primary button-sm sign-in-modal "]')
        post["Answer_comment_score"] = sum([convert2num(score.get_attribute("data-vote-count")) for score in Answer_comment_score])
        comments = question_comments.find_elements(By.XPATH, './/div[@class="content font-size-sm"]')
        post["Answer_comment_body"] = ' '.join([comment.text for comment in comments])
            
    return post


def get_url(driver, url):
    driver.get(url)

    urls_lst = set()
    urls_node_lst = driver.find_elements(By.XPATH, '//h2[@class="title is-6 margin-bottom-xxs"]/a')

    for urls_node in urls_node_lst:
        urls_lst.add(urls_node.get_attribute('href'))

    return urls_lst, driver.current_url


if __name__ == '__main__':
    driver = uc.Chrome()
    driver.implicitly_wait(5)

    base_url = 'https://learn.microsoft.com/en-us/answers/tags/75/azure-machine-learning?page='
    posts_url_lst = set()
    last_url = ''
    index = 0

    while True:
        index += 1
        cur_url = base_url + str(index)
        posts_url, ref_url = get_url(driver, cur_url)
        
        if ref_url == last_url:
            break
        
        posts_url_lst = posts_url_lst.union(posts_url)
        last_url = cur_url
    
    posts = pd.DataFrame()
    for post_url in posts_url_lst:
        post = get_data(driver, post_url)
        post = pd.DataFrame([post])
        posts = pd.concat([posts, post], ignore_index=True)
    
    posts.to_json(os.path.join('Dataset/Tool-specific', 'Azure Machine Learning.json'), indent=4, orient='records')
