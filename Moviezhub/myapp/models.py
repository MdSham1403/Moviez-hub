from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.conf import settings
from django.core.exceptions import ValidationError
import uuid

# --- Categories & Genres ---

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Genre(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# --- Stream Model (The Playing Engine) ---

class Stream(models.Model):
    STREAM_TYPE_CHOICES = (
        ('movie', 'Movie'),
        ('episode', 'Episode'),
    )

    stream_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True
    )

    stream_type = models.CharField(
        max_length=10,
        choices=STREAM_TYPE_CHOICES
    )

    movie = models.ForeignKey(
        'Movie',
        on_delete=models.CASCADE,
        related_name='streams',
        null=True,
        blank=True
    )

    episode = models.ForeignKey(
        'Episode',
        on_delete=models.CASCADE,
        related_name='streams',
        null=True,
        blank=True
    )

    quality = models.CharField(
        max_length=20,
        help_text="Example: 480p, 720p, 1080p"
    )

    video_file = models.FileField(
        upload_to='streams/',
        blank=True,
        null=True
    )

    video_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="CDN / Cloud storage URL"
    )

    codec = models.CharField(max_length=50, blank=True, null=True)
    bitrate = models.PositiveIntegerField(blank=True, null=True, help_text="Bitrate in kbps")
    duration = models.PositiveIntegerField(help_text="Duration in seconds", null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['stream_id']),
            models.Index(fields=['movie']),
            models.Index(fields=['episode']),
        ]

    def clean(self):
        if not self.movie and not self.episode:
            raise ValidationError("Stream must be linked to a Movie or an Episode.")
        if self.movie and self.episode:
            raise ValidationError("Stream cannot be linked to both Movie and Episode.")

    def __str__(self):
        target = self.movie.title if self.movie else str(self.episode)
        return f"{target} - {self.quality}"

# --- Content Models ---

class Movie(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=2000)
    release_year = models.PositiveIntegerField(default=2000)
    genre = models.ManyToManyField(Genre)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    director = models.CharField(max_length=100, blank=True, null=True)
    duration = models.PositiveIntegerField(help_text="Duration in minutes", blank=True, null=True)
    language = models.CharField(max_length=50, default="Tamil")
    
    # Original Media Fields (Kept as per your request)
    poster = models.ImageField(upload_to='posters/', blank=True, null=True)
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True)
    poster_url = models.URLField(blank=True, null=True)
    thumbnail_url = models.URLField(blank=True, null=True)
    trailer_link = models.URLField(blank=True, null=True)
    
    rating = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    
    # These were likely causing your error if empty
    video_file = models.FileField(upload_to='videos/', blank=True, null=True)
    video_url = models.URLField(blank=True, null=True, max_length=500)
    upload_date = models.DateTimeField(auto_now_add=True, null=True)
    
    @property
    def poster_display(self):
        if self.poster:
            return self.poster.url
        if self.poster_url:
            return self.poster_url
        return None
 
    def __str__(self):
        return self.title

class Series(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    release_year = models.PositiveIntegerField(default=2000)
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    language = models.CharField(max_length=50, default="Tamil")
    poster = models.ImageField(upload_to='series_posters/', null=True, blank=True)
    poster_url = models.URLField(blank=True, null=True)
    thumbnail = models.ImageField(upload_to='series_thumbnails/', blank=True, null=True)
    thumbnail_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.title

class Season(models.Model):
    series = models.ForeignKey(Series, on_delete=models.CASCADE, related_name="seasons")
    season_number = models.PositiveIntegerField()
    release_year = models.PositiveIntegerField(default=2000)

    def __str__(self):
        return f"{self.series.title} - Season {self.season_number}"

class Episode(models.Model):
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name="episodes")
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    episode_number = models.PositiveIntegerField()
    video_file = models.FileField(upload_to='episodes/', blank=True, null=True)
    video_url = models.URLField(blank=True, null=True, max_length=500)
    duration = models.DurationField(null=True, blank=True)

    def __str__(self):
        return f"{self.season.series.title} - S{self.season.season_number}E{self.episode_number}: {self.title}"

# --- User & Social ---

class WatchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stream = models.ForeignKey(Stream, on_delete=models.SET_NULL, null=True, blank=True)
    last_position = models.PositiveIntegerField(default=0)  
    completed = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'stream')
        ordering = ['-updated_at']

    def __str__(self):
        stream_val = self.stream.stream_id if self.stream else "No Stream"
        return f"{self.user.username} - {stream_val}"

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'movie')

    def __str__(self):
        return f"{self.user.username} - {self.movie.title}"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.ImageField(
        upload_to='profile_pics/',
        default='profile_pics/default-profile.jpg',
        blank=True,
        null=True
    )
    location = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return f'{self.user.username} Profile'

class Update(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='updates_images/', blank=True, null=True)
    movie_link = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class CastMember(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='cast')
    name = models.CharField(max_length=255, blank=True, null=True)
    role = models.CharField(max_length=255, blank=True, null=True)
    photo = models.ImageField(upload_to='cast_photos/', blank=True, null=True)

    def photo_url(self):
        if self.photo:
            return self.photo.url
        elif self.name:
            from django.templatetags.static import static
            return static('images/default-profile.jpg')
        return None

    def __str__(self):
        return self.name or "Unnamed Cast"

class BroadcastEmail(models.Model):
    subject = models.CharField(max_length=255)
    message = models.TextField()
    sent_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sent_emails"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject
    
class MovieRequest(models.Model):
    name = models.CharField(max_length=255)
    year = models.IntegerField(blank=True, null=True)
    language = models.CharField(max_length=50, blank=True)
    details = models.TextField(blank=True)
    user_email = models.EmailField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
