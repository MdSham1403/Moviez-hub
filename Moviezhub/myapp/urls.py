from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import CustomPasswordResetForm
from django.views.defaults import page_not_found, server_error

urlpatterns = [
    # ==========================================x
    # 1. CORE & LANDING
    # ==========================================
    path('', views.welcome, name='welcome'),
    path('home/', views.home, name='home'),
    path('updates/', views.updates, name='updates'), # Unified updates path
    path('test-email/', views.test_email, name='test_email'),
    path('send-updates/', views.send_updates, name='send_updates'),

    # ==========================================
    # 2. AUTHENTICATION
    # ==========================================
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('accounts/login/', views.user_login, name='custom_login'),
    path('logout/', views.user_logout, name='logout'),
    path('deactivate/', views.deactivate_account, name='deactivate_account'),
    path('request-reactivation/', views.request_reactivation, name='request_reactivation'),

    # Password Reset
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='password_reset_form.html',
        form_class=CustomPasswordResetForm
    ), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(
        template_name='password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='password_reset_complete.html'
    ), name='password_reset_complete'),

    # ==========================================
    # 3. USER PROFILE & SOCIAL
    # ==========================================
    path('profile/', views.profile, name='profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('change_password/', views.change_password, name='change_password'),
    path('watchlist/', views.my_watchlist, name='my_watchlist'),
    path('watch-history/', views.watch_history, name='watch_history'),
    path('clear-watch-history/', views.clear_watch_history, name='clear_watch_history'),

    # ==========================================
    # 4. MOVIE MANAGEMENT
    # ==========================================
    path('movies/', views.movie_list, name='movie_list'),
    path('movies/', views.movie_list, name='movies'),
    path('explore_movies/', views.explore_movies, name='explore_movies'),
    path('movies_by_language/<str:language>/', views.movies_by_language, name='movies_by_language'),
    path('movie/<int:movie_id>/', views.movie_detail, name='movie_detail'),
    path('movie/<int:id>/', views.movie_detail, name='movie_detail'),
    path('movie/<int:movie_id>/watchlist/', views.add_to_watchlist, name='add_to_watchlist'),
    path('remove-from-watchlist/<int:movie_id>/', views.remove_from_watchlist, name='remove_from_watchlist'),
    
    # Movie Upload & Admin Utils
    path('upload-movies/', views.upload_movie, name='upload_movie'),
    path('upload/', views.upload, name='upload'),
    path('add_genre/', views.add_genre, name='add_genre'),
    path('request-movie/', views.request_movie, name='request_movie'),
    path("request-success/", views.request_success, name="request_success"),

    # ==========================================
    # 5. SERIES & EPISODES
    # ==========================================
    path('series/', views.series_list, name='series_list'),
    path('series/<int:series_id>/seasons/', views.season_list, name='season_list'),
    path('seasons/<int:season_id>/episodes/', views.episode_list, name='episode_list'),
    path('episodes/<int:episode_id>/', views.episode_detail, name='episode_detail'),
    path('upload-series/', views.upload_series, name='upload_series'),

    # ==========================================
    # 6. STREAMING ENGINE (The "Watch Now" Logic)
    # ==========================================
    # This triggers your Plyr player
    path('movies/<int:movie_id>/watch/', views.watch_movie, name='watch_movie'),
    path("api/next-episode/<int:movie_id>/", views.next_episode),
    
    # This saves the 5-second interval progress via AJAX
    path('stream/update/<uuid:stream_id>/', views.update_stream_progress, name='get_stream'),
]

