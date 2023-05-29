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
    
    data_json = driver.find_element(
        By.XPATH, '//script[@id="__NEXT_DATA__"]').get_attribute("innerText")
    data_dict = json.loads(data_json)
    
    question = data_dict["props"]["pageProps"]["question"]

    # question_title
    title = question["title"]
    # print("Title:", title)

    # Question_created_time
    date = question["createdAt"]
    # print("date:", date)

    # Question_created_time
    date_update = question["updatedAt"]
    # print("date:", date)

    # question_view_count
    view_count = question["views"]
    # print("view_count:", view_count)
    
    # question_follower_count
    follower_count = question["totalFollowers"]
    # print("follower_count:", follower_count)

    # Question_score_count
    upvote_count = question["votes"]
    # print("Question_score_count:", upvote_count)

    # Question_comment_count
    comments = question["comments"]
    comment_count = len(comments)
    # print("Question_comment_count:", comment_count)

    # question_body
    body = question["description"]
    # print("body:", body)

    # answers
    answers_lst = question["answers"]
    # print("answer_count:", answer_count)
    
    # author
    author_q = question["author"]
    isAwsEmployee = author_q["isAwsEmployee"]
    isModerator = author_q["isModerator"]
    isExpert = author_q["isExpert"]
    isCse = author_q["isCse"]
    # print("isAwsEmployee:", isAwsEmployee)
    # print("isModerator:", isModerator)
    # print("isExpert:", isExpert)
    # print("isCse:", isCse)

    post = {}
    post["Question_title"] = title
    post["Question_created_time"] = date
    post["Question_last_edit_time"] = date_update
    post["Question_link"] = url
    post["Question_score_count"] = upvote_count
    post["Question_favorite_count"] = follower_count
    post["Question_comment_count"] = comment_count
    post["Question_view_count"] = view_count
    post["Question_answer_count"] = len(answers_lst)
    post["Question_body"] = body
    post["Poster_isAwsEmployee"] = isAwsEmployee
    post["Poster_isModerator"] = isModerator
    post["Poster_isExpert"] = isExpert
    post["Poster_isCse"] = isCse
    post['Question_closed_time'] = np.nan
    post['Answer_score_count'] = np.nan
    post['Answer_last_edit_time'] = np.nan
    post['Answer_comment_count'] = np.nan
    post['Answer_body'] = np.nan
    post["Answerer_isAwsEmployee"] = np.nan
    post["Answerer_isModerator"] = np.nan
    post["Answerer_isExpert"] = np.nan
    post["Answerer_isCse"] = np.nan
                
    if question["accepted"]:
        for answer in answers_lst:
            if answer["accepted"]:
                post['Question_closed_time'] = answer["createdAt"]
                post['Answer_last_edit_time'] = answer["updatedAt"]
                post['Answer_comment_count'] = len(answer["comments"])
                post['Answer_score_count'] = answer["votes"]
                post['Answer_body'] = answer["body"]
                author_a = answer["author"]
                post["Answerer_isAwsEmployee"] = author_a["isAwsEmployee"]
                post["Answerer_isModerator"] = author_a["isModerator"]
                post["Answerer_isExpert"] = author_a["isExpert"]
                post["Answerer_isCse"] = author_a["isCse"]
                post["Question_self_resolution"] = author_a["id"] == author_q["id"]
                break

    return post


def get_url(driver, url):
    driver.get(url)

    posts_url = []
    urls_lst = driver.find_elements(
        By.XPATH, '//a[@class="QuestionCard_cardLink__7XTIk"]')
    for url_node in urls_lst:
        posts_url.append(url_node.get_attribute('href'))

    next_page_url = driver.find_element(
        By.XPATH, '//li[@title="Next Page"]/a').get_attribute('href')

    return posts_url, next_page_url


if __name__ == '__main__':
    driver = uc.Chrome()
    driver.implicitly_wait(2)

    next_page_url = 'https://repost.aws/tags/TAT80swPyVRPKPcA0rsJYPuA/amazon-sage-maker'
    cur_urls_lst = []

    while True:
        cur_urls, next_page_url = get_url(driver, next_page_url)

        if next_page_url == driver.current_url:
            break
        
        cur_urls_lst.extend(cur_urls)
    
    posts = pd.DataFrame()
    for post_url in cur_urls_lst:
        post = get_data(driver, post_url)
        post = pd.DataFrame([post])
        posts = pd.concat([posts, post], ignore_index=True)
        
    posts.to_json(os.path.join('../Dataset/Tool-specific/Raw', 'Amazon SageMaker.json'), indent=4, orient='records')
    
