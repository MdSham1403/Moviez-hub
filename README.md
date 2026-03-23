🎬 **MoviezHub**

MoviezHub is a high-performance OTT streaming platform built with Django.
It features a sleek, responsive UI, Google Social Authentication, and a robust backend deployed on Railway.

Designed for personal use, it offers a seamless experience for managing and streaming movies and series.

🚀 Live Demo: https://moviezhub14.up.railway.app

✨ Key Features

🔐 Social Authentication
Secure login via Google OAuth using django-allauth

🎥 Dynamic Streaming
Integrated YouTube / Video player with mobile-responsive configurations

🗂️ Content Management
Advanced Django Admin suite for managing Movies, Series, Seasons, and Episodes

🔎 Smart Search
Filter and search content by title, genre, and language

👤 Personalization
User profiles with customizable avatars and viewing preferences

🚀 Production Ready
Configured for PostgreSQL and served via Gunicorn on Railway

---

🛠️ Tech Stack

| Layer      | Technology                          |
| ---------- | ----------------------------------- |
| Backend    | Django 5.1 (Python 3.11)            |
| Database   | PostgreSQL                          |
| Auth       | Google OAuth 2.0 / Django Allauth   |
| Deployment | Railway (CI/CD Enabled)             |
| Frontend   | Bootstrap 5, Custom CSS, JavaScript |

🚀 Installation & Local Setup
📦 Prerequisites

Python 3.11+

Google Cloud Account (for OAuth)

Railway CLI (for production management)

---

▶️ Steps to Run the Project Locally

1️⃣ Clone the Repository
  ```bash
  git clone https://github.com/yourusername/moviezhub.git
  cd moviezhub
  python -m venv .venv
  source .venv/bin/activate  # Windows: .venv\Scripts\activate
  pip install -r requirements.txt
```
2️⃣ Apply Database Migrations

  ```bash
python manage.py makemigrations
python manage.py migrate
```
3️⃣ Google OAuth Setup
1. Create credentials in Google Cloud Console
2. Add this to Authorized Redirect URIs:
```bash
http://127.0.0.1:8000/accounts/google/login/callback/
```
3. Add Client ID and Client Secret to your .env or Django Admin panel

4️⃣ Run the Development Server
```bash
python manage.py runserver
```
☁️ Deployment (Railway)

This project is optimized for deployment on Railway

🔐 Environment Variables

Set these inside your Railway dashboard:
```bash
DATABASE_URL=your_postgres_connection_string
SITE_ID=1
DEBUG=False
ALLOWED_HOSTS=moviezhub14.up.railway.app
```
🧰 Railway CLI Management Commands
```bash
# Apply migrations to production
railway run python manage.py migrate

# Create a production admin user
railway run python manage.py createsuperuser

# Check Site IDs in production
railway run python manage.py shell
```
🤝 Contributing

Fork the project

Create your feature branch:
```bash
git checkout -b feature/NewFeature
```
Commit your changes:
```bash
git commit -m "Add some NewFeature"
```
Push to the branch:
```bash
git push origin feature/NewFeature
```
Open a Pull Request 🚀

---

📄 License

Distributed under the MIT License

---
👨‍💻 Author

Developed with ❤️ by Sam
