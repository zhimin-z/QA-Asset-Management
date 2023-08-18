import pandas as pd
import requests
import os


def convert2num(num):
    try:
        return int(num)
    except:
        return 0


if __name__ == '__main__':
    page_url = 'https://community.h2o.ai/categories/general.json'
    entries = requests.get(page_url).json()['Discussions']
    posts = pd.DataFrame()
    
    for entry in entries:
        post = {}
        post['Question_link'] = entry['Url']
        url = entry['Url'] + '.json'
        content = requests.get(url).json()
        
        question = content['Discussion']
        post['Question_title'] = question['Name']
        post['Question_body'] = question['Body']
        post['Question_created_time'] = question['FirstDate']
        post['Question_comment_count'] = question['CountComments']
        post['Question_score_count'] = convert2num(question['Score'])
        post['Question_view_count'] = question['CountViews']
        
        comments = content['Comments']
        post['Question_comment_body'] = ' '.join([comment['Body'] for comment in comments])
        post['Question_comment_score'] = sum([convert2num(comment['Score']) for comment in comments])
        
        post = pd.DataFrame([post])
        posts = pd.concat([posts, post], ignore_index=True)
        
    posts.to_json(os.path.join('Dataset/Tool-specific', 'H2O AI Cloud.json'), indent=4, orient='records')