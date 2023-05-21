from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
from dateutil import parser
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

    # question_has_accepted_answer
    has_accepted = False
    try:
        driver.find_element(
            By.XPATH, '//div[@class="custom-google-accepted-solution root"]')
        has_accepted = True
    except:
        has_accepted = False
    # print("has_acceted:", has_accepted)

    # Question_score_count
    upvote_count = driver.find_element(
        By.XPATH, '//span[@class="message-stat kudos-stat"]').text
    upvote_count = convert2num(upvote_count)
    # print("upvote_count", upvote_count)

    # question_answer_count
    answer_count = driver.find_element(
        By.XPATH, '//span[@class="message-stat replies-stat"]').text
    answer_count = convert2num(answer_count)
    # print("question_answer_count", answer_count)

    # question_view_count
    view_count = driver.find_element(
        By.XPATH, '//span[@class="message-stat views-stat"]').text
    view_count = convert2num(view_count)
    # print("view_count", view_count)

    # # qustion_topic
    # topic_lst = driver.find_elements(
    #     By.XPATH, '//*[@class="label-link lia-link-navigation lia-custom-event"]')
    # for i in range(len(topic_lst)):
    #     topic_lst[i] = topic_lst[i].text
    # # print("topic:", topic_lst)

    # question_body
    body_lst = driver.find_elements(By.XPATH, '//*[@id="bodyDisplay"]/div/p')
    for i in range(len(body_lst)):
        body_lst[i] = body_lst[i].text
    body = ''.join(body_lst)
    # print("body:", body)

    total_dict = {}

    # answers
    answers_lst = driver.find_elements(
        By.XPATH, '//div[@class="lia-quilt lia-quilt-forum-message lia-quilt-layout-custom-message"]')
    if len(answers_lst) > 1:
        answers_lst = answers_lst[1:]
    # print("len:", len(answers_lst))

    total_dict["Question_title"] = title
    total_dict["Question_created_time"] = date
    total_dict["Question_link"] = url
    # total_dict["Question_topic"] = topic_lst
    total_dict["Question_has_accepted_answer"] = has_accepted
    total_dict["Question_answer_count"] = answer_count
    total_dict["Question_score_count"] = upvote_count
    total_dict["Question_view_count"] = view_count
    total_dict["Question_body"] = body
    total_dict["Answer_list"] = []

    for i in range(len(answers_lst)):
        answer = answers_lst[i]
        answer_date = answer.find_element(
            By.XPATH, './/span[@class="local-friendly-date"]').get_attribute('title')
        answer_date = convert2date(answer_date)

        try:
            Answer_score_count = answer.find_element(
                By.XPATH, './/div[@class="lia-button-image-kudos-count"]/span/span[1]').text
            Answer_score_count = convert2num(Answer_score_count)
        except:
            Answer_score_count = 0
        answer_body = answer.find_element(
            By.XPATH, './/div[@class="lia-message-body-content"]').get_attribute('innerText').strip()

        cur_has_accepted = False
        if has_accepted:
            try:
                driver.find_element(
                    By.XPATH, './/div[@class="custom-google-accepted-solution root"]')
                cur_has_accepted = True
            except:
                pass
        # print("answer_date:", answer_date)
        # print("answer_upvote:", Answer_score_count)
        # print("anaswer_body:", answer_body)

        total_dict["Answer_list"].append({
            "Answer_created_time": answer_date,
            "Answer_has_accepted": cur_has_accepted,
            "Answer_score_count": Answer_score_count,
            "Answer_body": answer_body
        })

    return total_dict


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

    index = 0
    posts = []
    last_url = ''
    base_url = 'https://www.googlecloudcommunity.com/gc/AI-ML/bd-p/cloud-ai-ml/page/'

    while True:
        index += 1
        cur_url = base_url + str(index)
        posts_url, ref_url = get_url(driver, cur_url)

        if ref_url == last_url:
            break

        last_url = cur_url

        for post_url in posts_url:
            posts.append(get_data(driver, post_url))

    posts_json = json.dumps(posts, indent='\t')
    with open(os.path.join('..\Dataset\Tool-specific\Round#1\Raw', 'Vertex AI.json'), 'w') as f:
        f.write(posts_json)
