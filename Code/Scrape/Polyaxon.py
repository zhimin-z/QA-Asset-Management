from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
import json
import re
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
    driver.Manage().Timeouts().ImplicitWait

    total_dict = {}

    # question_title
    title = driver.find_element(
        By.XPATH, '//span[@class="js-issue-title markdown-title"]').text
    # print("Title:", title)

    # question_creation_date
    date = driver.find_element(
        By.XPATH, '//relative-time[@class="no-wrap"]').get_attribute("datetime")
    # print("date:", date)

    # Question_score
    upvote_count = driver.find_element(
        By.XPATH, '//div[@class="text-center discussion-vote-form position-relative"]//button').text
    upvote_count = convert2num(upvote_count)
    # print("Question_score:", upvote_count)

    # question_category
    category_lst = driver.find_elements(
        By.XPATH, '//div[@class="discussion-sidebar-item"]/a')
    for i in range(len(category_lst)):
        category_lst[i] = category_lst[i].text
    # print("question_category:", category_lst)

    # qustion_label
    label_lst = driver.find_elements(
        By.XPATH, '//div[@class="d-flex flex-wrap"]/a')
    for i in range(len(label_lst)):
        label_lst[i] = label_lst[i].text
    # print("qustion_label:", label_lst)

    # question_issue
    issue_lst = driver.find_elements(
        By.XPATH, '//div[@class="discussion-sidebar-item"]')
    try:
        issue = convert2num(re.findall(r'\d+', issue_lst[2].text)[0])
    except:
        issue = -1
    # print("question_issue:", issue)

    # question_body
    body = driver.find_element(
        By.XPATH, '//div[@class="flex-shrink-0 col-12 col-md-9 mb-4 mb-md-0"]//task-lists').get_attribute("innerText").strip()
    # print("body:", body)

    # other_answers
    answers_node_lst = driver.find_elements(
        By.XPATH, '//div[@class="TimelineItem discussion-timeline-item mx-0 js-comment-container"]')
    answer_count = len(answers_node_lst)
    # print("answer_count:", len(answers_lst))

    total_dict["Question_title"] = title
    total_dict["Question_link"] = url
    total_dict["Question_creation_date"] = date
    total_dict["Question_tags"] = label_lst
    total_dict["Question_converted_from_issue"] = issue
    total_dict["Question_answer_count"] = answer_count
    total_dict["Question_score"] = upvote_count
    total_dict["Question_body"] = body
    total_dict["Answer_list"] = []

    for i in range(len(answers_node_lst)):
        answer = answers_node_lst[i]
        answer_date = answer.find_element(
            By.XPATH, './/relative-time').get_attribute('datetime')
        Answer_score = answer.find_element(
            By.XPATH, './/div[@class="text-center discussion-vote-form position-relative"]//button').text
        Answer_score = convert2num(Answer_score)
        answer_body = answer.find_element(
            By.XPATH, './/table[@role="presentation"]').get_attribute('innerText').strip()

        # print("answer_date:", answer_date)
        # print("answer_upvote:", Answer_score)
        # print("anaswer_body:", answer_body)
        # print("answer_has_accepted:", cur_has_accepted)

        total_dict["Answer_list"].append({
            "Answer_creation_date": answer_date,
            "Answer_score": Answer_score,
            "Answer_body": answer_body
        })

    return total_dict


def get_url(driver, url):
    driver.get(url)
    driver.Manage().Timeouts().ImplicitWait

    posts_url = []
    post_list = driver.find_elements(
        By.XPATH, '//a[@class="discussion-Link--secondary markdown-title Link--primary no-underline text-bold f3"]')

    for post in post_list:
        posts_url.append(post.get_attribute('href'))

    return posts_url


if __name__ == '__main__':
    driver = uc.Chrome()

    posts = []
    index = 0
    base_url = 'https://github.com/orgs/polyaxon/discussions?page='

    while True:
        index += 1
        page_url = base_url + str(index)
        posts_url = get_url(driver, page_url)

        if not posts_url:
            break

        for url in posts_url:
            posts.append(get_data(driver, url))

    posts_json = json.dumps(posts, indent='\t')
    with open(os.path.join('..\Dataset\Tool-specific Others\Round#1\Raw', 'Polyaxon.json'), 'w') as f:
        f.write(posts_json)
