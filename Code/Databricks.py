from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from dateutil import parser
import time
import json


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
    time.sleep(20)

    total_dict = {}

    while True:
        try:
            button = driver.find_element(
                By.XPATH, '//div[contains(@class, "showMoreComments-bottom")]//button[@class="slds-button"]')
            button.send_keys(Keys.ENTER)
            time.sleep(2)
        except:
            break

    # question_title
    title = driver.find_element(
        By.XPATH, '//article[@data-type="QuestionPost"]/div[2]').text
    # print("Title:", title)

    # question_creation_date
    date = driver.find_element(
        By.XPATH, '//article[@data-type="QuestionPost"]/div[1]//div[@class="cuf-subPreamble slds-text-body--small"]').text

    date = parser.parse(date).isoformat()
    # print("date:", date)

    # question_has_accepted_answer
    has_accepted = False
    try:
        driver.find_element(
            By.XPATH, '//div[@class="slds-p-horizontal_medium slds-p-top_large slds-p-bottom_x-small slds-text-heading_small slds-text-heading--small forceChatterFeedback"]')
        has_accepted = True
    except:
        has_accepted = False

    # # print("has_acceted:", has_accepted)

    # question_view_count
    view_count = driver.find_element(
        By.XPATH, '//li[@class="slds-item cuf-viewCount qe-viewCount"]').text
    view_count = convert2num(view_count)
    # print("question_view_count:", view_count)

    # question_upvote_count
    try:
        upvote_count = driver.find_element(
            By.XPATH, '//a[@class="upvoters-card-target"]').text
    except:
        pass
    upvote_count = convert2num(upvote_count)
    # print("question_upvote_count:", upvote_count)

    # qustion_tags
    try:
        button = driver.find_element(By.XPATH, '//li[@class="moreLi"]/a')
        button.send_keys(Keys.ENTER)
        time.sleep(2)
    except:
        pass
    tag_lst = driver.find_elements(
        By.XPATH, '//ul[@class="topic-commaSeparatedList"]/li')
    for i in range(len(tag_lst)):
        tag_lst[i] = tag_lst[i].text
    # print("tags:", tag_lst)

    # question_body
    body = driver.find_element(
        By.XPATH, '//article[@data-type="QuestionPost"]/div[3]//div[@class="feedBodyInner Desktop"]').get_attribute('innerText').strip()
    # print("body:", body)

    # other_answers
    answers_lst = driver.find_elements(
        By.XPATH, '//article[@class="cuf-commentItem slds-comment slds-media comment--threadedCommunity forceChatterComment"]')
    if has_accepted == True:
        answers_lst = answers_lst[1:]
    answer_count = len(answers_lst)
    # print("answer_count:", answer_count)

    total_dict["Question_title"] = title
    total_dict["Question_creation_date"] = date
    total_dict["Question_tag"] = tag_lst
    total_dict["Question_link"] = url
    total_dict["Question_upvote_count"] = upvote_count
    total_dict["Question_answer_count"] = answer_count
    total_dict["Question_view_count"] = view_count
    total_dict["Question_has_accepted_answer"] = has_accepted
    total_dict["Question_body"] = body

    total_dict["Answers"] = []
    for i in range(len(answers_lst)):
        answer = answers_lst[i]
        answer_date = answer.find_element(
            By.XPATH, './/time').get_attribute("datetime")
        answer_upvote_count = answer.find_element(
            By.XPATH, './/feeds_voting-vote-up-toggle').text
        answer_body = answer.find_element(
            By.XPATH, './/div[@class="slds-comment__content"]').get_attribute('innerText').strip()

        answer_upvote_count = convert2num(answer_upvote_count)

        cur_has_accepted = False
        if has_accepted == True:
            try:
                answer.find_element(
                    By.XPATH, './/span[@title="Selected as Best by ahuarte"]')
                cur_has_accepted = True
            except:
                cur_has_accepted = False
        else:
            cur_has_accepted = False

        # print("answer_date:", answer_date)
        # print("answer_upvote:", answer_upvote_count)
        # print("anaswer_body:", answer_body)
        # print("answer_has_accepted:", cur_has_accepted)

        answer_upvote_count = convert2num(answer_upvote_count)

        total_dict["Answers"].append({
            "Answer_creation_date": answer_date,
            "Answer_upvote_count": answer_upvote_count,
            "Answer_body": answer_body,
            "Answer_has_accepted": cur_has_accepted
        })

    return total_dict


def get_url(driver, url):
    driver.get(url)
    time.sleep(10)

    while True:
        try:
            button = driver.find_element(
                By.XPATH, '//div[@class="cuf-showMoreContainer slds-var-p-vertical_x-small"]/button')
            button.send_keys(Keys.ENTER)
            time.sleep(2)
        except:
            break

    urls_node_lst = driver.find_elements(
        By.XPATH, '//a[@class="cuf-feedElement-wrap"]')
    urls_lst = []
    for urls_node in urls_node_lst:
        url = urls_node.get_attribute('href')
        if url.find("question") != -1:
            urls_lst.append(url)

    return urls_lst


if __name__ == "__main__":
    driver = webdriver.Chrome(service=ChromeService(
        ChromeDriverManager().install()))

    base_url = 'https://community.databricks.com/s/topic/0TO3f000000CiCIGA0/machine-learning'
    posts_url = get_url(driver, base_url)

    posts = []
    for url in posts_url:
        posts.append(get_data(driver, url))

    res_json = json.dumps(posts)
    with open('Databricks.json', 'w') as f:
        f.write(res_json)
