🎬 MoviezHub

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

▶️ Steps to Run the Project Locally
1️⃣ Clone the Repository
git clone https://github.com/yourusername/moviezhub.git
cd moviezhub
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
