from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
import json
import time
import os


def convert2num(num):
    try:
        return int(num)
    except:
        try:
            return int(num.split()[0])
        except:
            return 0


def get_data(driver, url, topic):
    driver.get(url)

    total_dict = {}

    # question_title
    driver.implicitly_wait(10)
    time.sleep(3)
    title = driver.find_element(By.XPATH, '//div[@class="post-title"]').text
    #print("Title:", title)

    # question_creation_date
    date = driver.find_element(
        By.XPATH, '//div[@class="post-meta"]//time').get_attribute("datetime")
    #print("date:", date)

    # question_upvote_count
    upvote_count = driver.find_element(
        By.XPATH, '//div[@class="post-vote vote"]//span').text
    upvote_count = convert2num(upvote_count)
    #print("question_upvote_count:", upvote_count)

    # question_body
    body = driver.find_element(
        By.XPATH, '//div[@class="post-body"]').get_attribute("innerText").strip()
    #print("body:", body)

    # answers
    answers_lst = driver.find_elements(
        By.XPATH, '//div[contains(@class,"comment-wrapper")]')
    answer_count = len(answers_lst)
    # print("answer_count:", len(answers_lst))

    total_dict["Question_title"] = title
    total_dict["Question_creation_date"] = date
    total_dict["Question_link"] = url
    total_dict["Question_answer_count"] = answer_count
    total_dict["Question_upvote_count"] = upvote_count
    total_dict["Question_topic"] = topic
    total_dict["Question_body"] = body

    total_dict["Answers"] = []

    for i in range(len(answers_lst)):
        answer = answers_lst[i]
        answer_date = answer.find_element(
            By.XPATH, './/li[@class="meta-data"]/time').get_attribute("datetime")
        
        try:
            answer_upvote_count = answer.find_element(
                By.XPATH, './/span[@class="vote-sum"]').text
            answer_upvote_count = convert2num(answer_upvote_count)
        except:
            answer_upvote_count = 0
        
        answer_body = answer.find_element(By.XPATH, './/section[@class="comment-body"]').get_attribute(
            'innerText').strip()

        #print("answer_date:", answer_date)
        #print("answer_upvote:", answer_upvote_count)
        #print("anaswer_body:", answer_body)

        total_dict["Answers"].append({
            "Answer_creation_date": answer_date,
            "Answer_upvote_count": answer_upvote_count,
            "Answer_body": answer_body
        })

    return total_dict


def get_url(driver, url):
    driver.get(url)

    posts_url = []
    urls_lst = driver.find_elements(
        By.XPATH, '//span[@class="striped-list-info"]/a')
    for post_url in urls_lst:
        posts_url.append(post_url.get_attribute('href'))

    return posts_url


def get_topic(driver, url):
    driver.get(url)

    community_urls_lst = driver.find_elements(
        By.XPATH, '//li[contains(@class, "topics-item")]/a')

    topics = []
    communities_url = []
    for community_url in community_urls_lst:
        communities_url.append(community_url.get_attribute('href'))
        topics.append(community_url.find_element(By.XPATH, './/h4').text)

    return communities_url, topics


if __name__ == '__main__':
    driver = uc.Chrome()

    base_url = 'https://tickets.dominodatalab.com/hc/en-us/community/topics'
    communities_url, topics = get_topic(driver, base_url)

    posts_dict = []
    for community_url, topic in zip(communities_url, topics):
        posts_url = get_url(driver, community_url)
        for post_url in posts_url:
            posts_dict.append(get_data(driver, post_url, topic))
            time.sleep(1)

    posts_json = json.dumps(posts_dict)
    with open(os.path.join('../Dataset/Raw', 'Domino.json'), 'w') as f:
        f.write(posts_json)
