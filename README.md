# MoviezHub Project

## Overview
**MoviezHub** is a private OTT (Over-The-Top) streaming platform designed for personal use. It allows users to watch movies and series with enhanced features like personalized profiles, streaming, and content management. This platform provides a secure and optimized experience for managing movie collections, user profiles, and viewing preferences.

## Features
1. **User Authentication:**
   - User registration, login, and password recovery.
   - Secure password management and user authentication.
   
2. **Profile Management:**
   - Users can create and update their profiles, including adding a profile picture.
   - Profile information includes name, email, bio, and location.
   - Users can change or delete their profile picture.

3. **Movie and Series Management:**
   - Admin can upload and manage movies and series.
   - Movies can be searched and filtered by name and genre.
   - Movies and series are displayed with posters, titles, and descriptions.
   - Series display seasons and episodes with thumbnails.

4. **Video Streaming:**
   - Video player supports full-screen mode and playback options (forward, rewind, volume control).
   - Movies and series are streamed in 1080p resolution with subtitles.

5. **Basic Search and Filtering:**
   - Search movies and series by name and genre.
   - Movies are grouped by language and genre.

6. **Security Features:**
   - Secured email configurations for notifications and user authentication.
   - All user and movie data are securely stored.

7. **Admin Panel (Django):**
   - Admin panel for managing movies, series, users, and settings.
   - Easy control over movie and profile data.

## Installation

### Prerequisites
- Python 3.9+
- Django 4.x
- PostgreSQL (or any database of choice)

### Steps to Run the Project Locally

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/moviezhub.git
   cd moviezhub
   
2. Set up a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # For Linux/Mac
   venv\Scripts\activate     # For Windows

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   
5. Set up the database:
   Modify settings.py to configure the database (PostgreSQL or SQLite).
   Run migrations:
   ```bash
   python manage.py migrate

6. Create a superuser for admin access:
   ```bash
   python manage.py createsuperuser

 7. Start the development server:
    ```bash
      python manage.py runserver
    
8. Open the browser and navigate to http://127.0.0.1:8000 to see the website.


Usage

User Registration and Login:

Navigate to the registration page to create a new account.
After logging in, users can update their profiles and browse movies.

Admin Panel:

Admin users can log in to the admin panel at http://127.0.0.1:8000/admin to manage content.
Movie Streaming:

Users can view movies, add them to their profiles, and stream content.
Profile Settings:

Users can edit their profile details and upload a new profile picture.
Technologies Used
Frontend: HTML, CSS, JavaScript (for interactive UI)
Backend: Django (Python)
Database: PostgreSQL
File Storage: (Local or Cloud-based, e.g., AWS S3 for production)
Authentication: Django authentication system with email-based verification
Video Streaming: Supports 1080p video resolution and subtitle integration
Contributing
Feel free to fork the repository and submit pull requests to improve the project. Contributions can be in any of the following areas:

Fixing bugs
Adding new features (e.g., advanced search, more user options)
Improving UI/UX design
Enhancing security features
To contribute:

Fork the repository.
Create a new branch.
Make your changes.
Push the changes and create a pull request.
License
This project is open-source and available under the MIT License.

Author
Developed by Sam!
