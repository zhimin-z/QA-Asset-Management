from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
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
    title = driver.find_element(By.XPATH, '//h2[@class="question-title"]').text
    # print("Title:", title)

    # question_creation_date
    date = driver.find_element(
        By.XPATH, '//span[contains(@class, "action-date")]/time[@role="presentation"]').get_attribute("datetime")
    # print("date:", date)

    # question_has_accepted_answer
    has_accepted = False
    try:
        driver.find_element(By.XPATH, '//span[@aria-label="Best Answer"]')
        has_accepted = True
    except:
        has_accepted = False
    # print("has_acceted:", has_accepted)

    # Question_score
    upvote_count = driver.find_element(
        By.XPATH, '//div[@class="vote-widget"]/span/span[2]').text
    upvote_count = convert2num(upvote_count)
    # print("upvote_count", upvote_count)

    # question_follower_count
    try:
        follower_count = driver.find_element(
            By.XPATH, '//div[@class="widget-content"]/p/strong').text
        follower_count = convert2num(follower_count)
    except:
        follower_count = 0
    # print("question_follower_count", follower_count)

    # question_comment_count
    comment_count = driver.find_element(By.XPATH, '//div[@class="control-bar"]').find_element(
        By.XPATH, '//span[@class="control-score-counter comment-count"]').text
    comment_count = convert2num(comment_count)
    # print("comment_count", comment_count)

    # question_answer_count
    answer_count = driver.find_element(
        By.XPATH, '//span[@itemprop="answerCount"]').text
    # print("answer_count:", answer_count)
    answer_count = convert2num(answer_count)

    # # qustion_tags
    tag_lst = driver.find_elements(
        By.XPATH, '//span[@class="tags"]/a[@class="tag"]')
    for i in range(len(tag_lst)):
        tag_lst[i] = tag_lst[i].find_element(By.XPATH, './a').text
    # print("tags:", tag_lst)

    # question_body
    body = driver.find_element(
        By.XPATH, '//div[@class="question-body post-body"]').get_attribute("innerText").strip()
    # print("body:", body)

    total_dict["Question_title"] = title
    total_dict["Question_creation_date"] = date
    total_dict["Question_link"] = url
    total_dict["Question_tags"] = tag_lst
    total_dict["Question_has_accepted_answer"] = has_accepted
    total_dict["Question_answer_count"] = answer_count
    total_dict["Question_comment_count"] = comment_count
    total_dict["Question_follower_count"] = follower_count
    total_dict["Question_score"] = upvote_count
    total_dict["Question_body"] = body

    total_dict["Answer_list"] = []

    accepted_answer_lst = driver.find_elements(
        By.XPATH, '//div[@class="post-container answer-container  accepted-answer"]')
    if accepted_answer_lst:
        ac_answer = accepted_answer_lst[0]
        ac_answer_date = ac_answer.find_element(
            By.XPATH, './/time[@role="presentation"]').get_attribute("datetime")
        ac_Answer_score = ac_answer.find_element(
            By.XPATH, './/div[@class="vote-widget"]/span/span[2]').text
        ac_Answer_score = convert2num(ac_Answer_score)
        ac_answer_body = ac_answer.find_element(
            By.XPATH, './/div[@class="answer-body"]').get_attribute('innerText').strip()
        ac_answer_comment_count = ac_answer.find_element(
            By.XPATH, './/span[@class="control-score-counter comment-count"]').get_attribute("innerText")
        ac_answer_comment_count = convert2num(ac_answer_comment_count)

        # print("ac_answer_date:", ac_answer_date)
        # print("ac_answer_upvote:", ac_Answer_score)
        # print("ac_anaswer_body:", ac_answer_body)
        # print("ac_answer_comment_count:", ac_answer_comment_count)
        # print("ac_answer_has_accepted:", True)

        total_dict["Answer_list"].append({
            "Answer_creation_date": ac_answer_date,
            "Answer_score": ac_Answer_score,
            "Answer_body": ac_answer_body,
            "Answer_comment_count": ac_answer_comment_count,
            "Answer_has_accepted": True
        })

    # other_answers
    answers_lst = driver.find_elements(
        By.XPATH, '//div[@class="widget widget-nopad answer-list"]/div[@class="widget-content"]/div[@class="post-container answer-container "]')
    # print("len:", len(answers_lst))

    for i in range(len(answers_lst)):
        answer = answers_lst[i]
        answer_date = answer.find_element(
            By.XPATH, './/time[@role="presentation"]').get_attribute("datetime")
        Answer_score = answer.find_element(
            By.XPATH, './/div[@class="vote-widget"]/span/span[2]').text
        Answer_score = convert2num(Answer_score)
        answer_body = answer.find_element(
            By.XPATH, './/div[@class="answer-body"]').get_attribute('innerText').strip()
        answer_comment_count = answer.find_element(
            By.XPATH, './/span[@class="control-score-counter comment-count"]').get_attribute("innerText")
        answer_comment_count = convert2num(answer_comment_count)

        # print("answer_date:", answer_date)
        # print("answer_upvote:", Answer_score)
        # print("anaswer_body:", answer_body)
        # print("answer_comment_count:", answer_comment_count)
        # print("answer_has_accepted:", False)

        total_dict["Answer_list"].append({
            "Answer_creation_date": answer_date,
            "Answer_score": Answer_score,
            "Answer_body": answer_body,
            "Answer_comment_count": answer_comment_count,
            "Answer_has_accepted": False
        })

    return total_dict


def get_url(driver, url):
    driver.get(url)

    urls_lst = []
    urls_node_lst = driver.find_elements(By.XPATH, '//h2[@class="title"]/a')

    for urls_node in urls_node_lst:
        # the marker post for out-of-bound pages
        if urls_node.text == 'Your question goes here':
            break
        urls_lst.append(urls_node.get_attribute('href'))

    return urls_lst


if __name__ == '__main__':
    driver = uc.Chrome()

    base_url = 'https://learn.microsoft.com/en-us/answers/topics/25447/azure-machine-learning.html?page='
    posts = []
    index = 0

    while True:
        index += 1
        page_url = base_url + str(index)
        posts_url = get_url(driver, page_url)

        if not posts_url:
            break

        for post_url in posts_url:
            posts.append(get_data(driver, post_url))

    posts_json = json.dumps(posts, indent='\t')
    with open(os.path.join('..\Dataset\Tool-specific Others\Round#1\Raw', 'Azure Machine Learning.json'), 'w') as f:
        f.write(posts_json)
