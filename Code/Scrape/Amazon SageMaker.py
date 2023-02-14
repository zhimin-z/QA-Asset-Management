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
    title = driver.find_element(
        By.XPATH, '//div[@class="QuestionView_title__C_38B"]/h1').text
    # print("Title:", title)

    # question_creation_date
    data_json = driver.find_element(
        By.XPATH, '//script[@id="__NEXT_DATA__"]').get_attribute("innerText")
    data_dict = json.loads(data_json)
    date = data_dict["props"]["pageProps"]["question"]["createdAt"]
    # print("date:", date)

    # question_has_accepted_answer
    try:
        driver.find_element(
            By.XPATH, '//div[@class="AnswerView_acceptedTag__MIxHg"]')
        has_accepted = True
    except:
        has_accepted = False
    # print("has_acceted:", has_accepted)

    # question_view_count
    view_count = driver.find_element(
        By.XPATH, '//div[@class="ant-typography ant-typography-ellipsis ant-typography-single-line ant-typography-ellipsis-single-line Avatar_age___5eSl"]/span').text
    view_count = convert2num(view_count)
    # print("question_view_count:", view_count)

    # Question_score
    upvote_count = driver.find_element(
        By.XPATH, '//div[@class="Vote_textContainer__5bmNJ"]').text
    upvote_count = convert2num(upvote_count)
    # print("Question_score:", upvote_count)

    # question_topics
    topic_lst = driver.find_elements(
        By.XPATH, '//div[@class="Metadata_container__SrVEy"]/div[1]/div[2]/a')
    for i in range(len(topic_lst)):
        topic_lst[i] = topic_lst[i].find_element(By.XPATH, './/span').text
    # print("topics:", topic_lst)

    # qustion_tags
    tag_lst = driver.find_elements(
        By.XPATH, '//div[@class="Metadata_container__SrVEy"]/div[2]/div[2]/a')
    for i in range(len(tag_lst)):
        tag_lst[i] = tag_lst[i].find_element(By.XPATH, './/span').text
    # print("tags:", tag_lst)

    # question_body
    body = driver.find_element(
        By.XPATH, '//div[@class="QuestionView_container__37ZXp"]//div[@class="custom-md-style"]').get_attribute("innerText").strip()
    # print("body:", body)

    # other_answers
    answers_lst = driver.find_elements(
        By.XPATH, '//div[@class="AnswerView_gridContainer__DDxNy"]')
    # print("answer_count:", len(answers_lst))

    answer_count = len(answers_lst)

    total_dict["Question_title"] = title
    total_dict["Question_creation_date"] = date
    total_dict["Question_link"] = url
    total_dict["Question_topic"] = topic_lst
    total_dict["Question_tags"] = tag_lst
    total_dict["Question_score"] = upvote_count
    total_dict["Question_view_count"] = view_count
    total_dict["Question_answer_count"] = answer_count
    total_dict["Question_has_accepted_answer"] = has_accepted
    total_dict["Question_body"] = body

    total_dict["Answer_list"] = []
    for i in range(len(answers_lst)):
        answer = answers_lst[i]
        # answer_date = answer.find_element(By.XPATH, './/div[@class="ant-typography ant-typography-ellipsis ant-typography-single-line ant-typography-ellipsis-single-line Avatar_age___5eSl"]').text
        answer_date = data_dict["props"]["pageProps"]["question"]["answers"][i]["createdAt"]
        Answer_score = answer.find_element(
            By.XPATH, './/div[@class="Vote_textContainer__5bmNJ"]').text
        Answer_score = convert2num(Answer_score)
        answer_body = answer.find_element(
            By.XPATH, './/div[@class="custom-md-style"]').get_attribute('innerText').strip()

        cur_has_accepted = False
        if has_accepted:
            try:
                answer.find_element(
                    By.XPATH, './/div[@class="AnswerView_acceptedTag__MIxHg"]')
                cur_has_accepted = True
            except:
                cur_has_accepted = False
        else:
            cur_has_accepted = False

        # print("answer_date:", answer_date)
        # print("answer_upvote:", Answer_score)
        # print("anaswer_body:", answer_body)
        # print("answer_has_accepted:", cur_has_accepted)

        total_dict["Answer_list"].append({
            "Answer_creation_date": answer_date,
            "Answer_score": Answer_score,
            "Answer_body": answer_body,
            "Answer_has_accepted": cur_has_accepted
        })

    return total_dict


def get_url(driver, url):
    driver.get(url)
    driver.implicitly_wait(1)

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

    posts = []
    next_page_url = 'https://repost.aws/tags/TAT80swPyVRPKPcA0rsJYPuA/amazon-sage-maker'

    while True:
        cur_urls_lst, next_page_url = get_url(driver, next_page_url)

        for post_url in cur_urls_lst:
            posts.append(get_data(driver, post_url))

        if not next_page_url:
            break

    posts_json = json.dumps(posts, indent='\t')
    with open(os.path.join('..\Dataset\Tool-specific Others\Round#1\Raw', 'Amazon SageMaker.json'), 'w') as f:
        f.write(posts_json)
