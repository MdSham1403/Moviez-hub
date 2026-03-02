import threading
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from allauth.account.signals import user_signed_up
from .models import Profile, Movie
from .views import send_welcome_email

# --- Helper Function for Background Tasks ---
def run_in_background(target_func, *args, **kwargs):
    """Helper to run any function in a separate thread"""
    thread = threading.Thread(target=target_func, args=args, kwargs=kwargs)
    thread.daemon = True  # Ensures thread closes if the main process stops
    thread.start()

# --- Signal Receivers ---

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(user_signed_up)
def send_welcome_on_signup(request, user, **kwargs):
    """
    Runs send_welcome_email in a background thread.
    The user is redirected instantly, NO MORE 500 ERRORS.
    """
    run_in_background(send_welcome_email, user)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()

@receiver(post_save, sender=Movie)
def send_movie_notification(sender, instance, created, **kwargs):
    """Runs send_mail in a background thread so saving a movie is fast."""
    if created:
        email_args = {
            'subject': '🎬 New Movie Added!',
            'message': f'Hello!\n\nA new movie has just been added: {instance.title}.\nCheck it out on MoviezHub!',
            'from_email': settings.DEFAULT_FROM_EMAIL,
            'recipient_list': [settings.ADMIN_EMAIL],
            'fail_silently': False, # Set to False so you see errors in Railway logs
        }
        run_in_background(send_mail, **email_args)