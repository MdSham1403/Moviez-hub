from django.contrib import admin, messages
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django import forms
from django.utils.html import format_html
from django.contrib.auth import get_user_model
from .models import Category, Genre, Movie, Profile, Watchlist, Series, Season, Episode, Update, CastMember, BroadcastEmail
from django.contrib.auth.models import User

from .models import BroadcastEmail
User = get_user_model()

# Register models that do not need customization
admin.site.register(Category)
admin.site.register(Genre)
admin.site.register(Watchlist)


# 🎬 Cast Member Inline (for Movie editing)
class CastMemberInline(admin.StackedInline):  
    model = CastMember
    extra = 1
    fields = ['name', 'role', 'photo']


# 🎥 Movie Admin
@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'release_year', 'poster', 'thumbnail', 'poster_url', 'thumbnail_url')
    search_fields = ('title',)
    list_filter = ('release_year',)
    inlines = [CastMemberInline]


# 📺 Series Admin
@admin.register(Series)
class SeriesAdmin(admin.ModelAdmin):
    list_display = ('title', 'release_year', 'language', 'genre', 'category', 'poster', 'poster_url', 'thumbnail', 'thumbnail_url')
    search_fields = ('title',)
    list_filter = ('release_year', 'language', 'genre', 'category')
    fieldsets = (
        (None, {'fields': ('title', 'description', 'release_year', 'language', 'genre', 'category')}),
        ('Poster and Thumbnail', {'fields': ('poster', 'poster_url', 'thumbnail', 'thumbnail_url')}),
    )


# 🎞 Episode Admin
@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    list_display = ('season', 'episode_number', 'title', 'video_file', 'video_url')
    fieldsets = (
        (None, {'fields': ('season', 'episode_number', 'title', 'description', 'duration')}),
        ('Video', {'fields': ('video_file', 'video_url')}),
    )


# 📅 Season Admin
@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ('series', 'season_number')


# 📰 Update Admin
@admin.register(Update)
class UpdateAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title', 'description')
    ordering = ('-created_at',)


# 🎭 Cast Member Admin
@admin.register(CastMember)
class CastMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'movie')
    search_fields = ('name', 'role', 'movie__title')

from django import forms

# 📩 Broadcast Email Form (customize textarea)
class BroadcastEmailForm(forms.ModelForm):
    class Meta:
        model = BroadcastEmail
        fields = "__all__"
        widgets = {
            "message": forms.Textarea(attrs={"rows": 10, "cols": 80}),
        }

# ✅ Custom Form for Broadcast
class BroadcastEmailForm(forms.ModelForm):
    send_to_all = forms.BooleanField(required=False, initial=True, label="Send to ALL users?")
    recipients = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(is_active=True),
        required=False,
        help_text="Select users if not sending to all",
    )

    class Meta:
        model = BroadcastEmail
        fields = ["subject", "message", "send_to_all", "recipients"]


# 📩 Broadcast Email Admin
@admin.register(BroadcastEmail)
class BroadcastEmailAdmin(admin.ModelAdmin):
    form = BroadcastEmailForm
    list_display = ("subject", "sent_by", "created_at")

    def save_model(self, request, obj, form, change):
        """Send email based on admin choice"""
        obj.sent_by = request.user
        super().save_model(request, obj, form, change)

        # ✅ Decide recipients
        if form.cleaned_data.get("send_to_all"):
            recipients = User.objects.filter(is_active=True).values_list("email", flat=True)
        else:
            recipients = form.cleaned_data.get("recipients").values_list("email", flat=True)

        # ✅ Send with BCC so emails are hidden
        if recipients:
            email = EmailMessage(
                subject=obj.subject,
                body=obj.message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[settings.DEFAULT_FROM_EMAIL],  # only sender in "to"
                bcc=list(recipients),              # real users in BCC
            )
            email.send(fail_silently=False)

# ✅ Register Profile with custom admin
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_email', 'bio', 'location')

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = "Email"
