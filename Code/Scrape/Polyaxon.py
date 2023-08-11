from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
import pandas as pd
import numpy as np
import os


def convert2num(num):
    try:
        return int(num)
    except:
        try:
            return int(num.strip().split()[0])
        except:
            try:
                return int(num.strip().split()[-1])
            except:
                return 0


def get_data(driver, url):
    driver.get(url)

    post = {}

    # question_title
    title = driver.find_element(
        By.XPATH, '//span[@class="js-issue-title markdown-title"]').text
    # print("Title:", title)
    
    # question_tag_count
    tag_count = len(driver.find_elements(By.XPATH, '//span[@class="discussion-sidebar-item js-discussion-sidebar-item"]/div[1]/a'))
    # print("tag_count:", tag_count)

    # Question_created_time
    date = driver.find_element(
        By.XPATH, '//relative-time[@class="no-wrap"]').get_attribute("datetime")
    # print("date:", date)

    # Question_score_count
    upvote_count = driver.find_element(
        By.XPATH, '//div[@class="text-center discussion-vote-form position-relative"]//button').get_attribute("aria-label")
    upvote_count = convert2num(upvote_count)
    # print("Question_score_count:", upvote_count)

    # question_body
    body = driver.find_element(
        By.XPATH, '//td[@class="d-block color-fg-default comment-body markdown-body js-comment-body"]').get_attribute("innerText").strip()
    # print("body:", body)

    # question_answer_count
    answer_count = driver.find_element(
        By.XPATH, '//h2[@id="discussion-comment-count"]/span[1]')
    answer_count = convert2num(answer_count)
    # print("answer_count:", len(answers_lst))

    post["Question_title"] = title
    post["Question_tag_count"] = tag_count
    post["Question_link"] = url
    post["Question_created_time"] = date
    post["Question_answer_count"] = answer_count
    post["Question_score_count"] = upvote_count
    post["Question_body"] = body
    post['Question_closed_time'] = np.nan
    post['Answer_score_count'] = np.nan
    post['Answer_comment_count'] = np.nan
    post['Answer_body'] = np.nan
    post["Question_self_closed"] = np.nan
    
    info = driver.find_element(By.XPATH, '//div[@class="d-flex flex-wrap flex-items-center mb-3 mt-2"]')
    accepted = info.find_element(By.XPATH, './/span').get_attribute('title')
    
    if accepted == 'Answered':
        answerer = info.find_element(By.XPATH, './/a[@class="Link--secondary text-bold"]').text
        poster = info.find_element(By.XPATH, './/a[@class="Link--secondary text-bold d-inline-block"]').get_attribute('innerText').strip()
        post['Question_self_closed'] = poster == answerer
        answer = driver.find_element(By.XPATH, '//section[@class="width-full" and @aria-label="Marked as Answer"]')
        post['Question_closed_time'] = answer.find_element(By.XPATH, './/relative-time').get_attribute('datetime')
        post['Answer_body'] = answer.find_element(By.XPATH, './/td[@class="d-block color-fg-default comment-body markdown-body js-comment-body"]').get_attribute('innerText').strip()
        try:
            Answer_score_count = answer.find_element(By.XPATH, './/div[@class="text-center discussion-vote-form position-relative"]//button').get_attribute('aria-label')
            post['Answer_score_count'] = convert2num(Answer_score_count)
            comments = answer.find_elements(By.XPATH, './/td[@class="d-block color-fg-default comment-body markdown-body js-comment-body px-3 pt-0 pb-2"]/p')
            post['Answer_comment_count'] = len(comments)
            post['Answer_comment_body'] = ' '.join([comment.get_attribute('innerText').strip() for comment in comments])
        except:
            pass

    return post


def get_url(driver, url):
    driver.get(url)

    posts_url = set()
    post_list = driver.find_elements(
        By.XPATH, '//div[@class="lh-condensed pl-2 pr-3 flex-1"]/h3/a')

    for post in post_list:
        posts_url.add(post.get_attribute('href'))

    return posts_url


if __name__ == '__main__':
    driver = uc.Chrome()
    driver.implicitly_wait(5)

    base_url = 'https://github.com/orgs/polyaxon/discussions/categories/q-a?page='
    posts_url_lst = set()
    index = 0

    while True:
        index += 1
        page_url = base_url + str(index)
        posts_url = get_url(driver, page_url)

        if not posts_url:
            break
        
        posts_url_lst = posts_url_lst.union(posts_url)

    posts = pd.DataFrame()
    for url in posts_url_lst:
        post = get_data(driver, url)
        post = pd.DataFrame([post])
        posts = pd.concat([posts, post], ignore_index=True)
    
    posts.to_json(os.path.join('../Dataset/Tool-specific', 'Polyaxon.json'), orient='records', indent=4)
