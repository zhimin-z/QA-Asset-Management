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
    title = driver.find_element(By.XPATH, '//div[@class="post-title"]').text
    #print("Title:", title)

    # Question_created_time
    date = driver.find_element(By.XPATH, '//div[@class="post-meta"]//time').get_attribute("datetime")
    #print("date:", date)

    # Question_score_count
    upvote_count = driver.find_element(By.XPATH, '//div[@class="post-vote vote"]//span').text
    upvote_count = convert2num(upvote_count)
    #print("Question_score_count:", upvote_count)

    # question_body
    body = driver.find_element(By.XPATH, '//div[@class="post-body"]').get_attribute("innerText").strip()
    #print("body:", body)

    # answers
    answers_lst = driver.find_elements(By.XPATH, '//div[contains(@class,"comment-wrapper")]')
    # print("answer_count:", len(answers_lst))

    post = {}
    post["Question_title"] = title
    post["Question_created_time"] = date
    post["Question_link"] = url
    post["Question_answer_count"] = len(answers_lst)
    post["Question_score_count"] = upvote_count
    post["Question_body"] = body

    return post


def get_url(driver, url):
    driver.get(url)

    posts_url = []
    urls_lst = driver.find_elements(By.XPATH, '//span[@class="striped-list-info"]/a')
    for post_url in urls_lst:
        posts_url.append(post_url.get_attribute('href'))

    return posts_url


def get_topic(driver, url):
    driver.get(url)

    community_urls_lst = driver.find_elements(By.XPATH, '//li[contains(@class, "topics-item")]/a')

    topics = []
    communities_url = set()
    for community_url in community_urls_lst:
        communities_url.add(community_url.get_attribute('href'))
        topics.append(community_url.find_element(By.XPATH, './/h4').text)

    return communities_url, topics


if __name__ == '__main__':
    driver = uc.Chrome()
    driver.implicitly_wait(2)

    base_url = 'https://tickets.dominodatalab.com/hc/en-us/community/topics'
    communities_url, topics = get_topic(driver, base_url)
    posts_url_lst = set()

    for community_url, topic in zip(communities_url, topics):
        posts_url = get_url(driver, community_url)
        posts_url_lst = posts_url_lst.union(posts_url)
    
    posts = pd.DataFrame()
    for post_url in posts_url_lst:
        post = get_data(driver, post_url)
        post = pd.DataFrame([post])
        posts = pd.concat([posts, post], ignore_index=True)
    
    posts.to_json(os.path.join('../Dataset/Tool-specific', 'Domino.json'), indent=4, orient='records')
