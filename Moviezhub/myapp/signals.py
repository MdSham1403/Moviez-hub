from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Profile, Movie


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create Profile when a new User is created"""
    if created:
        Profile.objects.create(user=instance)

# myapp/signals.py

from allauth.account.signals import user_signed_up
from django.dispatch import receiver
from .views import send_welcome_email

@receiver(user_signed_up)
def send_welcome_on_signup(request, user, **kwargs):
    send_welcome_email(user)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Ensure Profile is saved whenever User is updated"""
    if hasattr(instance, 'profile'):
        instance.profile.save()


@receiver(post_save, sender=Movie)
def send_movie_notification(sender, instance, created, **kwargs):
    """Send email notification when a new movie is added"""
    if created:
        send_mail(
            subject='🎬 New Movie Added!',
            message=f'Hello!\n\nA new movie has just been added: {instance.title}.\nCheck it out on MoviezHub!',
            from_email=settings.DEFAULT_FROM_EMAIL,   # Uses project settings email
            recipient_list=[settings.ADMIN_EMAIL],    # Send to admin or user list
            fail_silently=True,
        )
