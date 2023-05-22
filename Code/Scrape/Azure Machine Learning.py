from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
import pandas as pd
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
    title = driver.find_element(By.XPATH, '//h1[@class="title is-2"]').text
    # print("Title:", title)

    # Question_created_time
    date = driver.find_element(
        By.XPATH, '//div[@class="level-right margin-top-none")]/span[@class="font-size-xs"]').get_attribute("datetime")
    # print("date:", date)

    # question_has_accepted_answer
    try:
        driver.find_element(By.XPATH, '//span[@value="Accepted answer"]')
        has_accepted = True
    except:
        has_accepted = False
    # print("has_acceted:", has_accepted)

    # Question_score_count
    upvote_count = driver.find_element(
        By.XPATH, '//span[@class="vote-count"]').text
    upvote_count = convert2num(upvote_count)
    # print("upvote_count", upvote_count)

    # question_comment_count
    comment_count = driver.find_element(By.XPATH, '//div[@class="buttons margin-block-xxs margin-top-xs"]/span/span[2]').text
    comment_count = convert2num(comment_count)
    # print("comment_count", comment_count)

    # question_answer_count
    answer_count = driver.find_element(By.XPATH, '//span[@itemprop="answerCount"]').text
    # print("answer_count:", answer_count)
    answer_count = convert2num(answer_count)

    # question_body
    body = driver.find_element(
        By.XPATH, '//div[@class="question-body post-body"]').get_attribute("innerText").strip()
    # print("body:", body)

    post = {}
    post["Question_title"] = title
    post["Question_created_time"] = date
    post["Question_link"] = url
    post["Question_has_accepted_answer"] = has_accepted
    post["Question_answer_count"] = answer_count
    post["Question_comment_count"] = comment_count
    post["Question_score_count"] = upvote_count
    post["Question_body"] = body

    post["Answer_list"] = []

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

        post["Answer_list"].append({
            "Answer_created_time": ac_answer_date,
            "Answer_score_count": ac_Answer_score,
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
        Answer_score_count = answer.find_element(
            By.XPATH, './/div[@class="vote-widget"]/span/span[2]').text
        Answer_score_count = convert2num(Answer_score_count)
        answer_body = answer.find_element(
            By.XPATH, './/div[@class="answer-body"]').get_attribute('innerText').strip()
        answer_comment_count = answer.find_element(
            By.XPATH, './/span[@class="control-score-counter comment-count"]').get_attribute("innerText")
        answer_comment_count = convert2num(answer_comment_count)

        # print("answer_date:", answer_date)
        # print("answer_upvote:", Answer_score_count)
        # print("anaswer_body:", answer_body)
        # print("answer_comment_count:", answer_comment_count)
        # print("answer_has_accepted:", False)

        post["Answer_list"].append({
            "Answer_created_time": answer_date,
            "Answer_score_count": Answer_score_count,
            "Answer_body": answer_body,
            "Answer_comment_count": answer_comment_count,
            "Answer_has_accepted": False
        })

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
    
    posts.to_json(os.path.join('Dataset/Tool-specific/Raw', 'Azure Machine Learning.json'), indent=4, orient='records')
