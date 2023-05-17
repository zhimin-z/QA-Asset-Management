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


def get_data(driver, url, topic):
    driver.get(url)
    driver.implicitly_wait(1)

    total_dict = {}

    # question_title
    title = driver.find_element(By.XPATH, '//div[@class="post-title"]').text
    #print("Title:", title)

    # Question_created_time
    date = driver.find_element(
        By.XPATH, '//div[@class="post-meta"]//time').get_attribute("datetime")
    #print("date:", date)

    # Question_score_count
    upvote_count = driver.find_element(
        By.XPATH, '//div[@class="post-vote vote"]//span').text
    upvote_count = convert2num(upvote_count)
    #print("Question_score_count:", upvote_count)

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
    total_dict["Question_created_time"] = date
    total_dict["Question_link"] = url
    total_dict["Question_answer_count"] = answer_count
    total_dict["Question_score_count"] = upvote_count
    # total_dict["Question_topic"] = topic
    total_dict["Question_body"] = body

    total_dict["Answer_list"] = []

    for i in range(len(answers_lst)):
        answer = answers_lst[i]
        answer_date = answer.find_element(
            By.XPATH, './/li[@class="meta-data"]/time').get_attribute("datetime")

        try:
            Answer_score = answer.find_element(
                By.XPATH, './/span[@class="vote-sum"]').text
            Answer_score = convert2num(Answer_score)
        except:
            Answer_score = 0

        answer_body = answer.find_element(By.XPATH, './/section[@class="comment-body"]').get_attribute(
            'innerText').strip()

        #print("answer_date:", answer_date)
        #print("answer_upvote:", Answer_score)
        #print("anaswer_body:", answer_body)

        total_dict["Answer_list"].append({
            "Answer_created_time": answer_date,
            "Answer_score": Answer_score,
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

    posts = []
    for community_url, topic in zip(communities_url, topics):
        posts_url = get_url(driver, community_url)
        for post_url in posts_url:
            posts.append(get_data(driver, post_url, topic))

    posts_json = json.dumps(posts, indent='\t')
    with open(os.path.join('..\Dataset\Tool-specific Others\Round#1\Raw', 'Domino.json'), 'w') as f:
        f.write(posts_json)
