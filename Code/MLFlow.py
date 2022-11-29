from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
import time
import json
import re


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

    total_dict = {}

    # question_title
    title = driver.find_element(By.XPATH, '//h1[@class="KPwZRb gKR4Fb"]').text
    # print("question_title:", title)

    # question_view_count
    view_count = driver.find_element(
        By.XPATH, '//div[@class="Nadu4b"]').get_attribute('innerText')
    view_count = convert2num(view_count)
    # print("question_view_count:", view_count)

    # sections
    section_lst = driver.find_elements(By.XPATH, '//div[@role="list"]/section')
    # print("list_number:", len(section_lst))

    for i in range(len(section_lst)):
        answer = section_lst[i]
        answer_time = answer.find_element(
            By.XPATH, './/span[@class="zX2W9c"]').text
        answer_body = answer.find_element(
            By.XPATH, './/div[@class="ptW7te"]').get_attribute("innerText").strip()

        k = answer_time.find('(')
        answer_time = answer_time[:k-1]
        answer_time = re.sub('\u5e74', '-', answer_time)
        answer_time = re.sub('\u6708', '-', answer_time)
        answer_time = re.sub('\u65e5 ', 'T', answer_time)
        answer_time = answer_time + 'Z'
        # print(answer_time)
        # print(answer_time.encode('utf-8'))

        if i == 0:
            total_dict["Question_title"] = title
            total_dict["Question_creation_date"] = answer_time
            total_dict["Question_link"] = url
            total_dict["Question_answer_count"] = len(section_lst) - 1
            total_dict["Question_view_count"] = view_count
            total_dict["Question_body"] = answer_body
            total_dict["Answers"] = []

            # print("questino_time:", answer_time)
            # print("question_body:", answer_body)
        else:
            total_dict["Answers"].append({
                "Answer_creation_time": answer_time,
                "Answer_body": answer_body
            })
            # print("answer_time:", answer_time)
            # print("answer_body:", answer_body)

    return total_dict


def get_url(driver):
    urls_lst = driver.find_elements(By.XPATH, '//div[@jscontroller="MAWgde"]')
    for i in range(len(urls_lst)):
        urls_lst[i] = urls_lst[i].find_element(
            By.XPATH, './/a[@class="ZLl54"]').get_attribute("href")
    return urls_lst


if __name__ == '__main__':
    driver = uc.Chrome()

    base_url = 'https://groups.google.com/g/mlflow-users'

    res_dict = []
    page_count = 0

    while True:
        driver.get(base_url)
        time.sleep(3)

        next_button = driver.find_element(
            By.XPATH, '//div[@role="button" and @jslog="95005; track:JIbuQc"]')

        is_quit = False

        for i in range(page_count):
            try:
                next_button.click()
            except:
                continue
            time.sleep(3)

        cur_urls_lst = get_url()

        for cur_url in cur_urls_lst:
            if cur_url == 'https://groups.google.com/g/mlflow-users/c/QnASq7ITAoI':
                is_quit = True
            d = get_data(cur_url)
            res_dict.append(d)

        if is_quit == True:
            break

        page_count += 1

    res_json = json.dumps(res_dict)
    with open("MLFlow.json", 'w') as f:
        f.write(res_json)
