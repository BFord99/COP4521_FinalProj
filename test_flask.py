import pytest
from flask import Flask, json
from app import app, NewsItem, Session, User, PostLikes

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_newsfeed(client):
    response = client.get('/newsfeed')
    assert response.status_code == 200

def test_add_newsfeed(client):
    test_session = Session()
    test_item = NewsItem(created_by='Test User', title='Test Title', score=1, text='Test Text', time=None)
    response1 = client.get('/newsfeed')
    s_data = json.loads(response1.data)
    assert response1.status_code == 200
    init_len = len(s_data)
    test_session.add(test_item)
    test_session.commit()
    test_session.delete(test_item)
    test_session.commit()
    response2 = client.get('/newsfeed')
    f_data = json.loads(response2.data)
    assert response2.status_code == 200
    final_len = len(f_data)
    assert init_len == final_len
    test_session.close()

def test_add_likepost(client):
    test_session = Session()
    test_item = PostLikes(id='1234', post_id='123', user_id='12345', is_liked=False)
    test_session.add(test_item)
    test_session.commit()
    test_session.delete(test_item)
    test_session.commit()
    test_session.close()

def test_add_dislikepost(client):
    test_session = Session()
    test_item = PostLikes(id='1234', post_id='123', user_id='12345', is_liked=True)
    test_session.add(test_item)
    test_session.commit()
    test_session.delete(test_item)
    test_session.commit()
    test_session.close()

