🎬 MoviezHub
MoviezHub is a high-performance OTT streaming platform built with Django. It features a sleek, responsive UI, Google Social Authentication, and a robust backend deployed on Railway. Designed for personal use, it offers a seamless experience for managing and streaming movies and series.

🚀 Live Demo: moviezhub14.up.railway.app

✨ Key Features
Social Authentication: Secure login via Google OAuth using django-allauth.

Dynamic Streaming: Integrated YouTube/Video player with mobile-responsive configurations.

Content Management: Advanced Django Admin suite for managing Movies, Series, Seasons, and Episodes.

Smart Search: Filter and search content by title, genre, and language.

Personalization: User profiles with customizable avatars and viewing preferences.

Production Ready: Configured for PostgreSQL and served via Gunicorn on Railway.

🛠️ Tech Stack
Backend: Django 5.1 (Python 3.11)

Database: PostgreSQL (Hosted on Railway)

Auth: Google OAuth 2.0 / Django Allauth

Deployment: Railway (with CI/CD)

Frontend: Bootstrap 5, Custom CSS, JavaScript

🚀 Installation & Local Setup
Prerequisites
Python 3.11+

Google Cloud Console Account (for OAuth)

Railway CLI (for production management)

### Steps to Run the Project Locally

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/yourusername/moviezhub.git](https://github.com/yourusername/moviezhub.git)
   cd moviezhub
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   
2. Database Migrations
   ```bash
   python manage.py makemigrations
   python manage.py migrate

3. Google OAuth Setup
   Create credentials at Google Cloud Console.
   Add http://127.0.0.1:8000/accounts/google/login/callback/ to Authorized Redirect URIs.
   Add Client ID and Secret to your .env or Django Admin.
   
4. Run Locally
   ```bash
   python manage.py runserver

☁️ Deployment (Railway)
This project is optimized for Railway.

Environment Variables
Ensure these are set in your Railway dashboard:

DATABASE_URL: Your Postgres connection string.

SITE_ID: The ID of your production domain (usually 1 or 2).

DEBUG: False in production.

ALLOWED_HOSTS: moviezhub14.up.railway.app

###Railway CLI Management Commands

   ```bash
   # Apply migrations to production
   railway run python manage.py migrate

   # Create a production admin
   railway run python manage.py createsuperuser

   # Check production Site IDs
   railway run python manage.py shell
   
   ```
🤝 Contributing
Fork the Project.
Create your Feature Branch:
   ```bash
   git checkout -b feature/NewFeature
   ```
Commit your Changes:
   ```bash
   git commit -m 'Add some NewFeature'
   ```
Push to the Branch:
   ```bash
   git push origin feature/NewFeature
   ```
Open a Pull Request.

📄 License
Distributed under the MIT License.

Author: Developed by Sam!
