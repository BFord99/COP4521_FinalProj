'''
this creates the tables in DB and fetches data from hackernews API
'''

import requests
import json
import time
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from models.newsitem import NewsItem

base_dir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(base_dir, 'data', 'app_database.db')
Base = declarative_base()
engine = create_engine(f'sqlite:///{db_path}')

with engine.begin() as connection:
    connection.execute(text("""CREATE TABLE IF NOT EXISTS news_items_new (
        id INTEGER PRIMARY KEY,
        created_by VARCHAR(200),
        title VARCHAR(200) NOT NULL,
        score INTEGER NOT NULL,
        text TEXT,
        time INTEGER
    );"""))

    # if you want to reset the users/posts tables
    #connection.execute(text("""DROP TABLE users;"""))
    #connection.execute(text("""DROP TABLE post_likes;"""))

    connection.execute(text("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        name VARCHAR(200) NOT NULL,
        email VARCHAR(200) NOT NULL,
        role VARCHAR(200) NOT NULL,
        google_id VARCHAR(200) NOT NULL
    );"""))

    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS post_likes (
        id VARCHAR(200) PRIMARY KEY,
        user_id VARCHAR(200) NOT NULL,
        post_id VARCHAR(200) NOT NULL,
        is_liked BOOLEAN NOT NULL
    );"""))



Base.metadata.create_all(bind=engine)

Session = sessionmaker(bind=engine)
session = Session()

def fetch_and_store():
    url = "https://hacker-news.firebaseio.com/v0/newstories.json?print=pretty"
    response = requests.get(url)

    if response.status_code == 200:
        data = json.loads(response.text)
        # API returns seconds not timestamp
        prev_period = int(time.time()) - 100000

        for post_id in data:
            post_url = f"https://hacker-news.firebaseio.com/v0/item/{post_id}.json?print=pretty"
            post_response = requests.get(post_url)

            if post_response.status_code == 200:
                post_data = json.loads(post_response.text)
                id=post_data.get('id')
                created_by=post_data.get('by')
                title=post_data.get('title')
                score=post_data.get('score')
                text=post_data.get('text')
                timestamp=post_data.get('time')

                # Check if the post was created in the last hour
                if timestamp >= prev_period:
                    news_item = NewsItem(
                        id=id,
                        created_by=created_by,
                        title=title,
                        score=score,
                        text=text,
                        time=timestamp
                    )
                    session.add(news_item)
                    session.commit()

if __name__ == '__main__':
    fetch_and_store()
