"""
This is the app engine,
- Runs backend for application
- Handles OAuth and API requests for pages/actions
"""

from math import ceil
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, abort
from authlib.integrations.flask_client import OAuth
from sqlalchemy.orm import sessionmaker
from sqlalchemy import desc
from fetch import engine
from models.user import User
from models.postlikes import PostLikes
from models.newsitem import NewsItem

app = Flask(__name__)
app.secret_key = "whatever-it-takes-to-pass"
Session = sessionmaker(bind=engine)

oauth = OAuth(app)
google = oauth.register(
    name="google",
    client_id="206652896652-nj7mcf039m1b42vgsfnihjp2h15qsmnu.apps.googleusercontent.com",
    client_secret= "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",
    access_token_url= "https://www.googleapis.com/oauth2/v4/token",
    access_token_params=None,
    authorize_url= "https://accounts.google.com/o/oauth2/v2/auth",
    authorize_params=None,
    api_base_url= "https://www.googleapis.com/oauth2/v3/",
    client_kwargs= {"scope": "openid email profile"},
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
    server_metadata_url= 'https://accounts.google.com/.well-known/openid-configuration',
)

@app.route('/')
def index():
    """Will redirect user to mainfeed if no input in URL"""
    return redirect(url_for('mainfeed'))

@app.route('/like_post', methods=['POST'])
def like_post():
    """If a post is liked or unliked, manages UI and table interactions"""
    data = request.get_json()
    session_db = Session()

    post_id = str(data.get('id'))
    user_id = session['user']['id']
    _id = post_id + user_id

    activity = session_db.query(PostLikes).filter_by(id=_id).first()
    post = session_db.query(NewsItem).filter_by(id=post_id).first()

    if activity is None:
        is_liked = True
        activity = PostLikes(id=_id, user_id=user_id, post_id=post_id, is_liked=is_liked)
        session_db.add(activity)
        post.score += 1
        is_liked = True
    else:
        if activity.is_liked:
            session_db.delete(activity)
            if post.score > 0:
                post.score -= 1
            is_liked = False
        else:
            activity.is_liked = True
            post.score += 1
            is_liked = True

    session_db.commit()
    session_db.close()

    return jsonify(success=True, is_liked=is_liked)

@app.route('/dislike_post', methods=['POST'])
def dislike_post():
    """If a post is liked or unliked, manages UI and table interactions"""
    data = request.get_json()
    session_db = Session()

    post_id = str(data.get('id'))
    user_id = session['user']['id']
    _id = post_id + user_id

    post = session_db.query(NewsItem).filter_by(id=post_id).first()
    activity = session_db.query(PostLikes).filter_by(id=_id).first()

    if activity is None:
        is_liked = False
        activity = PostLikes(id=_id, user_id=user_id, post_id=post_id, is_liked=is_liked)
        session_db.add(activity)
        if post.score > 0:
            post.score -= 1
        is_disliked = True
    else:
        if activity.is_liked == False:
            session_db.delete(activity)
            post.score += 1
            is_disliked = False
        else:
            activity.is_liked = False
            if post.score > 0:
                post.score -= 1
            is_disliked = True

    session_db.commit()
    session_db.close()

    return jsonify(success=True, is_disliked=is_disliked)



@app.route('/login')
def login():
    """Google Login"""
    redirect_uri = url_for('authorize', _external=True)
    print(redirect_uri)
    return google.authorize_redirect(redirect_uri)

@app.route('/authorize')
def authorize():
    """Google token generation and OAUTH"""
    google.authorize_access_token()
    resp = google.get('userinfo').json()
    session_db = Session()
    user = session_db.query(User).filter_by(google_id=resp['sub']).first()
    if not user:
        # my emails -> admin accounts
        admin_emails = ["corrano14@gmail.com"]
        _role = 'user' if resp['email'] not in admin_emails else 'admin'

        user = User(name=resp['name'], email=resp['email'], google_id=resp['sub'], role= _role)
        session_db.add(user)
        session_db.commit()

    session['user'] = {
        'name': user.name,
        'email': user.email,
        'id': user.google_id,
        'role': user.role}
    session_db.close()

    return redirect(url_for('mainfeed'))

@app.route('/logout')
def logout():
    """pop user from session on logout"""
    session.pop('user', None)
    return redirect('/')

@app.route('/newsfeed', methods=['GET'])
def newsfeed():
    """newsfeed API, returns JSON latest news"""
    _session = Session()
    news_items = _session.query(NewsItem).all()
    _session.close()

    news_items_dict = [item.__dict__ for item in news_items]

    for item in news_items_dict:
        item.pop('_sa_instance_state', None)

    return jsonify(news_items_dict)

@app.route('/deletePost/<int:deleted_id>', methods=['POST', 'GET'])
def delete_post(deleted_id):
    """removes post from both the newsfeed and postlikes table"""
    if 'user' not in session or session['user']['role'] != 'admin':
        # If the user is not logged in or is not an admin, redirect them
        return redirect(url_for('login'))

    session_db = Session()
    post = session_db.query(NewsItem).filter_by(id=deleted_id).first()

    if post is None:
        abort(404, description="Post not found")
    session_db.query(NewsItem).filter_by(id=deleted_id).delete()
    session_db.query(PostLikes).filter_by(post_id=deleted_id).delete()
    session_db.commit()
    return redirect(url_for('mainfeed'))


@app.route('/profile')
def profile():
    """profile page, shows the user information and liked and disliked posts"""
    session_db = Session()
    # Check if a user is logged in.
    if 'user' not in session:
        # If no user is logged in, redirect to login page.
        return redirect(url_for('login'))
    user_id = session['user']['id']
    user = session_db.query(User).filter_by(google_id=user_id).first()
    liked_posts = session_db.query(NewsItem)\
        .join(PostLikes, (PostLikes.post_id == NewsItem.id) & (PostLikes.user_id == user_id))\
        .filter(PostLikes.is_liked)\
        .all()
    disliked_posts = session_db.query(NewsItem)\
        .join(PostLikes, (PostLikes.post_id == NewsItem.id) & (PostLikes.user_id == user_id))\
        .filter(PostLikes.is_liked == False)\
        .all()
    session_db.close()
    return render_template('profile.html',
                           user=user,
                           liked_posts=liked_posts,
                           disliked_posts=disliked_posts)

@app.route('/mainfeed', methods=['GET'])
def mainfeed():
    """main page, displays news items"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    session_db = Session()
    total_items = session_db.query(NewsItem).count()
    total_pages = ceil(total_items / per_page)

    # Check if a user is logged in.
    if 'user' in session:
        user_id = session['user']['id']
        news_items = session_db.query(NewsItem, PostLikes.is_liked)\
            .outerjoin(PostLikes, (PostLikes.post_id == NewsItem.id)\
                       & (PostLikes.user_id == user_id))\
            .order_by(desc(NewsItem.time), desc(NewsItem.score))\
            .offset((page - 1) * per_page)\
            .limit(per_page)\
            .all()
    else:
        user_id = 0
        news_items = session_db.query(NewsItem, PostLikes.is_liked)\
            .outerjoin(PostLikes, (PostLikes.post_id == NewsItem.id)\
                       & (PostLikes.user_id == user_id))\
            .order_by(desc(NewsItem.time), desc(NewsItem.score))\
            .offset((page - 1) * per_page)\
            .limit(per_page)\
            .all()
    session_db.close()
    return render_template('mainfeed.html',
                           news_items=news_items,
                           page=page,
                           total_pages=total_pages)

# HTTP Headers
@app.after_request
def add_x_content_type_options_header(response):
    """content type header"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

@app.after_request
def add_x_xss_protection_header(response):
    """x_xss protection header"""
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

@app.after_request
def add_x_frame_options_header(response):
    """x frame options header"""
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    return response

@app.after_request
def add_hsts_header(response):
    """hsts header"""
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response

def create_app(test_config=None):
    app = Flask(__name__)

    if test_config is not None:
        app.config.from_mapping(test_config)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host= "0.0.0.0", port=5000)
