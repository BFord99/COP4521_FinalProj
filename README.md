# HackerNews Clone with Flask

This is a simple web application that mimics HackerNews user interactions such as liking and disliking posts. The application is built using Flask and interacts with the HackerNews API.

## Project Structure

- `app.py`: This is the main application file where the routes and main logic of the application resides.
- `models/`: This directory contains the ORM models for the application, specifically `User`, `PostLikes`, and `NewsItem`.
- `templates/`: This directory contains the HTML templates for the application. It includes `mainfeed.html` and `profile.html`.
- `static/`: This directory contains static files for the application, such as CSS stylesheets.
- `data/`: This directory contains the SQLite database file for the application, `app_database.db`.

## App Features

- User authentication via Google OAuth: Users can log in using their Google accounts.
- Main Feed: The main feed displays news items fetched from the HackerNews API.
- Liking and Disliking Posts: Users can like and dislike posts, and this activity is tracked and reflected in the UI.
- User Profiles: User profiles display user information and their liked and disliked posts.
- Admin Capabilities: Admin users can delete posts from the main feed.

## Installation and Running

1. Clone the repository.
2. Install the required Python packages with `pip install -r requirements.txt`.
3. Run the application with `flask run`.

The application will be accessible at `http://0.0.0.0:5000`.
