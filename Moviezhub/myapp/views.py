import json
from datetime import timedelta
from urllib.parse import urlparse, parse_qs
import os
import requests

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.mail import send_mail, send_mass_mail, EmailMultiAlternatives
from django.core.paginator import Paginator
from django.db.models import Q
from django.forms import modelformset_factory
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from PIL import Image
from moviepy.editor import VideoFileClip
from .models import MovieRequest
from dotenv import load_dotenv
import base64
from django.core.files.base import ContentFile
#from utils.bunny_token import generate_signed_url
from myapp.utils.bunny_token import generate_signed_url

from .forms import (
    MovieUploadForm,
    UserUpdateForm,
    ProfileUpdateForm,
    CustomUserCreationForm,
    UserProfileForm,
    PasswordChangeForm,
    SeriesForm,
    SeasonForm,
    EpisodeForm,
)
from .models import (
    Movie,
    Genre,
    Series,
    Watchlist,
    WatchHistory,
    Season,
    Episode,
    Update,
    Stream,
)
from django.contrib.auth.models import User
import hashlib
import base64
import time

BUNNY_SECRET = "edac228c-65e9-41cf-b8a4-cc9a95f7ef98"


def generate_signed_url(path):

    expires = int(time.time()) + 3600

    token_data = f"{BUNNY_SECRET}{path}{expires}"
    token = hashlib.md5(token_data.encode()).hexdigest()

    return f"{path}?token={token}&expires={expires}"


def welcome(request):
    if request.user.is_authenticated:  # Check if the user is logged in
        return redirect('home')  # Redirect to the home page
    return render(request, 'welcome.html')  # Show the welcome page if not logged in

@login_required
def profile_update(request):
    # Get the current user profile instance
    user = request.user
    profile = user.profile  # Assuming each user has a related profile instance

    if request.method == 'POST':
        # Initialize forms with the existing profile instance
        user_form = UserUpdateForm(request.POST, instance=user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            # Save the updated user and profile
            user_form.save()
            profile_form.save()
            return redirect('profile')  # Redirect to the profile page after successful update
    else:
        # Initialize the forms with the existing data
        user_form = UserUpdateForm(instance=user)
        profile_form = ProfileUpdateForm(instance=profile)

    return render(request, 'profile_update.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })

def login_view(request):
    error = None
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('home')
        else:
            error = form.errors  # Django's form provides detailed feedback

    form = AuthenticationForm()
    return render(request, 'login.html', {'form': form, 'error': error})

@login_required
def my_watchlist(request):
    # ✅ FIX: Change 'stream' to 'movie'
    watchlist_items = Watchlist.objects.filter(user=request.user).select_related('movie') 
    return render(request, 'my_watchlist.html', {'watchlist_items': watchlist_items})

# ======================
# Authentication Views
# ======================

# register view (fixed)
from allauth.account.utils import send_email_confirmation

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # 🔥 Trigger Allauth verification email

            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('home')
    else:
        form = CustomUserCreationForm()

    return render(request, 'register.html', {'form': form})


def user_login(request):
    """User Login"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'login.html')

def user_logout(request):
    """User Logout"""
    logout(request)
    return redirect('login')

def custom_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect("home")
            else:
                messages.error(request, "Your account has been deactivated. Contact admin.")
                return redirect("login")
        else:
            messages.error(request, "Invalid username or password.")
            return redirect("login")
    return render(request, "login.html")

# ======================
# Movie Management Views
# ======================

@login_required
def movie_list(request):
    search_query = request.GET.get('search', '')
    genre_filter = request.GET.get('genre', '')
    language_filter = request.GET.get('language', '')
    release_year_filter = request.GET.get('release_year', '')
    sort_by = request.GET.get('sort_by', '')

    genres = Movie.objects.values_list('genre__name', flat=True).distinct()
    languages = Movie.objects.values_list('language', flat=True).distinct()
    release_years = Movie.objects.values_list('release_year', flat=True).distinct().order_by('-release_year')

    movies = Movie.objects.all()

    if search_query:
        movies = movies.filter(Q(title__icontains=search_query) | Q(description__icontains=search_query))
    if genre_filter:
        movies = movies.filter(genre__name__icontains=genre_filter)
    if language_filter:
        movies = movies.filter(language=language_filter)
    if release_year_filter:
        movies = movies.filter(release_year=release_year_filter)

    # Default sort if none provided
    if sort_by:
        sort_map = {
            'release_year_asc': 'release_year',
            'release_year_desc': '-release_year',
            'title_asc': 'title',
            'title_desc': '-title',
            'rating_desc': '-rating',
            'rating_asc': 'rating',
        }
        movies = movies.order_by(sort_map.get(sort_by, '-id'))
    else:
        movies = movies.order_by('-id')

    paginator = Paginator(movies, 18) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'movies': page_obj, # This is your 'page_obj'
        'genres': genres,
        'languages': languages,
        'release_years': release_years,
        # Pass these back so the search bar stays filled
        'search_query': search_query,
        'selected_genre': genre_filter,
        'selected_year': release_year_filter,
        'selected_sort': sort_by,
    }
    return render(request, 'movie_list.html', context)
@login_required
@csrf_exempt
def update_stream_progress(request, stream_id):
    """
    Receives the 'heartbeat' from the Plyr player and saves the timestamp.
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            position = data.get('position', 0)
            
            # Fetch the specific stream object via UUID
            stream = get_object_or_404(Stream, stream_id=stream_id)
            
            # Update history or create new record if it doesn't exist
            history, created = WatchHistory.objects.update_or_create(
                user=request.user,
                stream=stream,
                defaults={'last_position': position}
            )
            
            # Auto-complete logic: if they are within 1 minute of the end
            # (Requires Stream.duration to be populated)
            if stream.duration and position > (stream.duration - 60):
                history.completed = True
                history.save()

            return JsonResponse({"status": "success", "saved": position})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
            
    return JsonResponse({"status": "invalid method"}, status=405)   

@login_required
def movie_detail(request, movie_id):
    """Movie Details with trailer"""
    movie = get_object_or_404(Movie, id=movie_id)

    # Extract clean YouTube ID
    youtube_id = extract_youtube_id(movie.trailer_link)

    return render(request, 'movie_detail.html', {
        'movie': movie,
        'youtube_id': youtube_id
    })
    
@login_required
def upload_movie(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("You do not have permission to upload movies.")
    
    if request.method == 'POST':
        form = MovieUploadForm(request.POST, request.FILES)
        if form.is_valid():
            movie = form.save(commit=False)
            movie.save()
            form.save_m2m()
            generate_thumbnail(movie)
            messages.success(request, 'Movie uploaded successfully!')
            return redirect('movie_list')
    else:
        form = MovieUploadForm()
    return render(request, 'movie_upload.html', {'form': form})

def generate_thumbnail(movie):
    """Generate a thumbnail from the video file"""
    try:
        video_path = movie.video_file.path
        thumbnail_path = f'thumbnails/{movie.id}.png'
        with VideoFileClip(video_path) as video:
            frame = video.get_frame(0)
            image = Image.fromarray(frame)
            image.save(os.path.join('media', thumbnail_path))
        movie.thumbnail = thumbnail_path
        movie.save()
    except Exception as e:
        print(f"Error generating thumbnail: {e}")
        
@login_required
def add_genre(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Genre.objects.create(name=name)
            messages.success(request, 'Genre added successfully!')
    return redirect('movie_upload')

@login_required
def add_to_watchlist(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    # Check if movie already exists in the watchlist
    if not Watchlist.objects.filter(user=request.user, movie=movie).exists():
        Watchlist.objects.create(user=request.user, movie=movie)
        messages.success(request, f'{movie.title} added to your watchlist.')
    else:
        messages.info(request, f'{movie.title} is already in your watchlist.')
    return redirect('movie_detail', movie_id=movie.id)

@login_required
def remove_from_watchlist(request, movie_id):
    watchlist_item = Watchlist.objects.filter(user=request.user, movie_id=movie_id).first()
    if watchlist_item:
        watchlist_item.delete()
        return JsonResponse({'status': 'success', 'message': 'Removed from vault'})
    return JsonResponse({'status': 'error', 'message': 'Item not found'}, status=404)

# ======================
# User Profile Management
# ======================
@login_required
def profile(request):
    """View & Update Profile"""
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)
    return render(request, 'profile.html', {'user_form': user_form, 'profile_form': profile_form})

@login_required
def profile_view(request):
    if not request.user.is_active:
        return redirect('account_deactivated')  # A simple info page
    return render(request, 'profile.html', {"profile": request.user.profile})

@login_required
def edit_profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            # 1. Handle Profile Picture Deletion
            if 'delete_profile_picture' in request.POST:
                request.user.profile.profile_picture = None
            
            # 2. Handle Cropped Image from Cropper.js
            cropped_data = request.POST.get('cropped_image')
            if cropped_data and cropped_data.startswith('data:image'):
                try:
                    # Parse the base64 string
                    format, imgstr = cropped_data.split(';base64,')
                    ext = format.split('/')[-1]
                    # Create a ContentFile that Django/Cloudinary can save
                    data = ContentFile(base64.b64decode(imgstr), name=f"user_avatar_{request.user.id}.{ext}")
                    request.user.profile.profile_picture = data
                except Exception as e:
                    messages.error(request, f"Image processing error: {e}")

            # 3. Save Forms
            user_form.save()
            profile_form.save()
            
            messages.success(request, "Your identity has been updated in the cloud vault!")
            return redirect('edit_profile')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    return render(request, 'edit_profile.html', {
        'user_form': user_form, 
        'profile_form': profile_form
    })

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.POST)
        if form.is_valid():
            old_password = form.cleaned_data['old_password']
            new_password = form.cleaned_data['new_password']
            confirm_password = form.cleaned_data['confirm_password']

            if request.user.check_password(old_password) and new_password == confirm_password:
                request.user.set_password(new_password)
                request.user.save()
                update_session_auth_hash(request, request.user)
                messages.success(request, 'Password updated successfully!')
            else:
                messages.error(request, 'Password change failed.')
    else:
        form = PasswordChangeForm()
    
    return render(request, 'change_password.html', {'form': form})


# ======================
# Home View
# ======================
@login_required
def home(request):
    return render(request, 'home.html')

@login_required
def series_list(request):
     series = Series.objects.all()
     return render(request, 'series_list.html', {'series': series})

@login_required
def season_list(request, series_id):
    series = get_object_or_404(Series, pk=series_id)
    seasons = series.seasons.all()
    return render(request, 'season_list.html', {'series': series, 'seasons': seasons})

def episode_list(request, season_id):
    
    season = get_object_or_404(Season, pk=season_id)
    series = season.series
    episodes = season.episodes.all()
    return render(request, 'episode_list.html', {'season': season, 'series': series,'episodes': episodes})

def episode_detail(request, episode_id):
    episode = get_object_or_404(Episode, pk=episode_id)

    # Assuming 'episode.duration' is a timedelta object (e.g., 1 hour, 30 minutes)
    total_duration_seconds = int(episode.duration.total_seconds())
    if total_duration_seconds >= 3600:  # More than 59 minutes
        formatted_duration = str(timedelta(seconds=total_duration_seconds))
    elif total_duration_seconds >= 60:  # Minutes but less than 59 minutes
        formatted_duration = f"{total_duration_seconds // 60} mins"
    else:  # Less than 60 seconds
        formatted_duration = str(timedelta(seconds=total_duration_seconds))

    return render(request, 'episode_detail.html', {
        'episode': episode,
        'formatted_duration': formatted_duration,
    })
# Series Management
@login_required
def upload_series(request):
    if request.method == 'POST':
        series_form = SeriesForm(request.POST, request.FILES)
        
        if series_form.is_valid():
            series_form.save()  # <-- FIX: use the actual form variable
            return HttpResponse('Series uploaded successfully')
            # Or you could do: return redirect('series_list')
    
    else:
        series_form = SeriesForm()  # For GET requests, provide an empty form
    
    return render(request, 'upload_series.html', {'form': series_form})

@login_required
def series_detail(request, id):
    series = Series.objects.get(id=id)
    return render(request, 'series_detail.html', {'series': series})

def series_upload_view(request):
    if request.method == 'POST':
        series_form = SeriesForm(request.POST, request.FILES)
        SeasonFormSet = modelformset_factory(Season, fields=('title', 'description', 'series'), extra=1)
        season_formset = SeasonFormSet(request.POST, queryset=Season.objects.none())

        if series_form.is_valid() and season_formset.is_valid():
            # Save the series instance
            series_instance = series_form.save()

            # Save the seasons
            for form in season_formset:
                season = form.save(commit=False)
                season.series = series_instance
                season.save()

            return redirect('series_list')  # Redirect to the series list page after submission

    else:
        series_form = SeriesForm()
        SeasonFormSet = modelformset_factory(Season, fields=('title', 'description', 'series'), extra=1)
        season_formset = SeasonFormSet(queryset=Season.objects.none())

    return render(request, 'upload_series.html', {'series_form': series_form, 'season_formset': season_formset})

@login_required
def explore_movies(request):
    languages = [
        {'name': 'Tamil', 'image': 'images/tamil.jpg'},
        {'name': 'Hindi', 'image': 'images/hindi.jpg'},
        {'name': 'Telugu', 'image': 'images/telugu.jpg'},
        {'name': 'Malayalam', 'image': 'images/malayalam.jpg'},
        {'name': 'English', 'image': 'images/english.jpg'},
    ]
    return render(request, 'explore_movies.html', {'languages': languages})

def movies_by_language(request, language):
    search_query = request.GET.get('search', '')
    genre_filter = request.GET.get('genre', '')
    year_filter = request.GET.get('release_year', '')
    sort_by = request.GET.get('sort_by', '')

    # Apply the language filter directly to the queryset
    movies = Movie.objects.filter(language=language)

    # Apply search filter (excluding the language)
    if search_query:
        movies = movies.filter(
            Q(title__icontains=search_query) | Q(description__icontains=search_query)
        )

    # Apply genre filter if selected
    if genre_filter:
        movies = movies.filter(genre__name=genre_filter)

    # Apply release year filter if selected
    if year_filter:
        movies = movies.filter(release_year=year_filter)

    # Sorting logic
    if sort_by == 'release_year_asc':
        movies = movies.order_by('release_year')
    elif sort_by == 'release_year_desc':
        movies = movies.order_by('-release_year')
    elif sort_by == 'title_asc':
        movies = movies.order_by('title')
    elif sort_by == 'title_desc':
        movies = movies.order_by('-title')
    elif sort_by == 'rating_desc':
        movies = movies.order_by('-rating')
    elif sort_by == 'rating_asc':
        movies = movies.order_by('rating')

    # Get distinct genres and release years for dropdown filters
    genres = Movie.objects.values_list('genre__name', flat=True).distinct()
    release_years = Movie.objects.values_list('release_year', flat=True).distinct()

    return render(request, 'language_movies.html', {
        'language': language,
        'movies': movies,
        'genres': genres,
        'release_years': release_years,
    })
    
@login_required
def upload(request):
    return render(request, 'upload.html')

@login_required
def check_movie_exists(request):
    query = request.GET.get('title', '').strip()
    exists = False
    movie_data = None

    if query:
        movie = Movie.objects.filter(title__iexact=query).first()
        if movie:
            exists = True
            movie_data = {
                "title": movie.title,
                "description": movie.description or "",
                "release_date": movie.release_date.strftime("%Y-%m-%d") if movie.release_date else None
            }

    return JsonResponse({
        "exists": exists,
        "movie": movie_data
    })
    
@login_required
def updates(request):
    updates = Update.objects.order_by('-created_at')
    return render(request, 'updates.html', {'updates': updates})

# ... (Keep your imports at the top)

@login_required
def watch_movie(request, movie_id):

    movie = get_object_or_404(Movie, id=movie_id)

    streams = Stream.objects.filter(
        movie=movie,
        is_active=True
    ).order_by("-quality")


    # 🎬 QUALITY SELECTION
    selected_quality = request.GET.get("quality")
    stream = None

    if selected_quality:
        stream = streams.filter(quality=selected_quality).first()

    if not stream:
        stream = streams.first()


    # ⏱ WATCH HISTORY
    last_position = 0

    if stream:
        history, _ = WatchHistory.objects.get_or_create(
            user=request.user,
            stream=stream
        )
        last_position = history.last_position


    youtube_id = None
    video_source_url = None


    # 🎥 STREAM SOURCE
    if stream:

        # Uploaded file
        if stream.video_file:
            video_source_url = stream.video_file.url

        # Bunny / external streaming
        elif stream.video_url:

            # YouTube
            if "youtube" in stream.video_url or "youtu.be" in stream.video_url:
                youtube_id = extract_youtube_id(stream.video_url)

            else:
                # Generate Bunny signed URL
                video_source_url = generate_signed_url(stream.video_url)


    # 📦 FALLBACK (old movies without streams)
    if not video_source_url and not youtube_id:

        if movie.video_file:
            video_source_url = movie.video_file.url

        elif movie.video_url:

            if "youtube" in movie.video_url:
                youtube_id = extract_youtube_id(movie.video_url)

            else:
                video_source_url = generate_signed_url(movie.video_url)


    return render(request, "watch_movie.html", {
        "movie": movie,
        "streams": streams,
        "current_stream": stream,
        "last_position": last_position,
        "youtube_id": youtube_id,
        "video_source_url": video_source_url,
    })
    movie = get_object_or_404(Movie, id=movie_id)

    streams = Stream.objects.filter(
        movie=movie,
        is_active=True
    ).order_by('-quality')


    # QUALITY SELECTION
    selected_quality = request.GET.get('quality')
    stream = None

    if selected_quality:
        stream = streams.filter(quality=selected_quality).first()

    if not stream:
        stream = streams.first()


    # WATCH HISTORY
    last_position = 0

    if stream:
        history, _ = WatchHistory.objects.get_or_create(
            user=request.user,
            stream=stream
        )
        last_position = history.last_position


    youtube_id = None
    video_source_url = generate_signed_url(stream.video_url)

    # STREAM SOURCE
    if stream:

        # Uploaded video file
        if stream.video_file:
            video_source_url = stream.video_file.url

        # External URL
        elif stream.video_url:

            # YouTube video
            if "youtube" in stream.video_url or "youtu.be" in stream.video_url:
                youtube_id = extract_youtube_id(stream.video_url)

            # HLS / MP4 streaming
            else:
                video_source_url = generate_signed_url(stream.video_url)


    # FALLBACK FOR OLD MOVIES
    if not video_source_url and not youtube_id:

        if movie.video_file:
            video_source_url = movie.video_file.url

        elif movie.video_url:
            video_source_url = movie.video_url


    return render(request, "watch_movie.html", {
        "movie": movie,
        "streams": streams,
        "current_stream": stream,
        "last_position": last_position,
        "youtube_id": youtube_id,
        "video_source_url": video_source_url,
    })

@login_required
def next_episode(request, movie_id):

    episode = Episode.objects.filter(movie_id=movie_id).first()

    if episode:
        next_ep = Episode.objects.filter(
            season=episode.season,
            number__gt=episode.number
        ).first()

        if next_ep:
            return JsonResponse({
                "next_episode_url": f"/episodes/{next_ep.id}/"
            })

    return JsonResponse({"next_episode_url": None})

def extract_youtube_id(url):
    """Extract a clean YouTube video ID from any URL"""
    if not url:
        return None
    parsed = urlparse(url)
    # youtu.be short link
    if "youtu.be" in parsed.netloc:
        return parsed.path.lstrip('/')  # removes leading slash, ignores query
    # youtube.com links
    if "youtube.com" in parsed.netloc:
        query = parse_qs(parsed.query)
        return query.get('v', [None])[0]
    return None


@login_required
def watch_history(request):
    """
    Displays the user's watch history.
    Uses select_related to reach from History -> Stream -> Movie/Episode efficiently.
    """
    history = WatchHistory.objects.filter(user=request.user).select_related(
        'stream__movie', 
        'stream__episode__season__series'
    ).order_by('-updated_at')
    
    return render(request, 'watch_history.html', {'history': history})

@login_required
def clear_watch_history(request):
    """Deletes all history records for the logged-in user."""
    if request.method == "POST":
        WatchHistory.objects.filter(user=request.user).delete()
        messages.success(request, "Watch history cleared successfully.")
    return redirect('watch_history')

def custom_404(request, exception):
    return render(request, '404.html', status=404)

def custom_500(request):
    return render(request, '500.html', status=500)

def test_email(request):
    send_mail(
        subject="MoviezHub Test Email",
        message="Hello! This is a test email from MoviezHub 🎬",
        from_email=settings.DEFAULT_FROM_EMAIL, # Use the onboarding@resend.dev from settings
        recipient_list=["mdsham1403@gmail.com"],
        fail_silently=False,
    )
    return HttpResponse("✅ Test email sent successfully! Check your inbox (and spam).")


@login_required
def get_stream(request, stream_id):
    stream = get_object_or_404(Stream, stream_id=stream_id)
    return JsonResponse({
        "video_url": stream.video_url
    })


@login_required
def send_updates(request):
    users = User.objects.all()
    subject = "Latest Updates on MoviezHub 🍿"
    message = "Hello!\n\nWe’ve added new movies and features for you. Log in and check them out!\n\n- Team MoviezHub"

    messages_data = []
    for user in users:
        if user.email:
            messages_data.append((subject, message, settings.DEFAULT_FROM_EMAIL, [user.email]))

    if messages_data:
        send_mass_mail(messages_data, fail_silently=False)
    return HttpResponse("✅ Update emails sent successfully!")

def send_welcome_email(user):
    if not user.email:
        print("❌ No email found for user:", user.username)
        return

    try:
        subject = "Welcome to MoviezHub 🎬"
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = user.email

        text_content = f"Hi {user.username}, thanks for joining MoviezHub!"
        html_content = render_to_string("emails/welcome_email.html", {"user": user})

        msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
        msg.attach_alternative(html_content, "text/html")
        
        # Add fail_silently=True here
        msg.send(fail_silently=True)
        print(f"✅ Welcome email process finished for {to_email}")
        
    except Exception as e:
        # This logs to Railway console, but doesn't crash the app
        print(f"❌ Resend API Error: {str(e)}")
    
User = get_user_model()

def send_broadcast_email(subject, message):
    users = User.objects.all()   # fetch all users
    for user in users:
        if user.email:
            # send email logic
            pass

def deactivate_account(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect("home")
            else:
                messages.error(request, "Your account has been deactivated. Contact admin.")
                return redirect("login")
        else:
            messages.error(request, "Invalid username or password.")
            return redirect("login")
    return render(request, "login.html")



@login_required
def request_reactivation(request):
    user = request.user
    if request.method == 'POST':
        # Notify admin by email
        send_mail(
            subject="Reactivation Request",
            message = (
    f"Hello Admin,\n\n"
    f"User {user.username} ({user.email}) has requested to reactivate their account.\n"
    f"Kindly review this request at your earliest convenience.\n\n"
    f"Thank you,\nMoviezHub"
),
            from_email=settings.DEFAULT_FROM_EMAIL,  # taken from settings.py
            recipient_list=[settings.ADMIN_EMAIL],   # custom admin email from settings.py
        )
        messages.success(request, "Your request has been sent. You will be notified once reactivated.")
        return redirect('home')
    return render(request, 'request_reactivation.html')

@login_required
def send_request_to_telegram(text):
    token = os.getenv("TG_REQUEST_BOT_TOKEN")
    chat_id = "7881710164"
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": text})
    print("BOT TOKEN:", os.getenv("TG_REQUEST_BOT_TOKEN"))


load_dotenv()
def send_telegram_message(text):
    BOT_TOKEN = os.getenv("TG_REQUEST_BOT_TOKEN")
    CHAT_ID = "7881710164"   # your user id or channel id

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    requests.post(url, data=payload)

def request_movie(request):
    if request.method == "POST":
        movie_name = request.POST.get("name")
        movie_year = request.POST.get("year", "N/A")
        movie_language = request.POST.get("language", "N/A")
        extra_details = request.POST.get("details", "No extra details")

        # Handle user info and email
        if request.user.is_authenticated:
            user_info = request.user.username
            user_email = request.user.email
        else:
            user_info = "Guest"
            user_email = request.POST.get("email")

        # Build the message for Telegram
        msg = f"🎬 <b>New Movie Request</b>\n\n"
        msg += f"<b>Name:</b> {movie_name}\n"
        msg += f"<b>Year:</b> {movie_year}\n"
        msg += f"<b>Language:</b> {movie_language}\n"
        msg += f"<b>Details:</b> {extra_details}\n"
        
        if user_email:
            msg += f"<b>Email:</b> {user_email}\n"
            
        msg += f"\n<b>Requested by:</b> {user_info}"

        # Send transmission
        send_telegram_message(msg)

        # Redirect to the success page instead of home
        return redirect("request_success")

    return render(request, "request_movie.html")

def request_success(request):
    return render(request, "request_success.html")
