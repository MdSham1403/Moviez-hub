from django import forms
from .models import Movie, Profile, Genre, Category, Series
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm , PasswordResetForm, SetPasswordForm
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError

class MovieUploadForm(forms.ModelForm):

    genre = forms.ModelMultipleChoiceField(
    queryset=Genre.objects.all(),
    widget=forms.CheckboxSelectMultiple,
    required=True,
    label="Select Genres"
    )

    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        empty_label="Select Category",
        required=True
    )
    
    class Meta:
        model = Movie
        fields = ['title', 'description', 'release_year', 'genre', 'category', 'director',
                  'duration', 'language', 'poster', 'thumbnail', 'trailer_link',
                  'video_file', 'video_url']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'genre': forms.CheckboxSelectMultiple(),
        }
        
class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(required=True, max_length=30, label="Name")
    email = forms.EmailField(required=False)
    class Meta:
        model = User
        fields = ('first_name', 'username', 'email', 'password1', 'password2')

class MovieForm(forms.ModelForm):
    class Meta:
        model = Movie
        fields = ['title', 'description', 'release_year', 'genre', 'category', 'director', 'duration', 'language', 'poster', 'video_file']
         
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'email']  # Fields from the User model
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
        
class ProfileUpdateForm(forms.ModelForm):
    delete_profile_picture = forms.BooleanField(required=False, label="Delete Profile Picture")

    class Meta:
        model = Profile
        fields = ['location', 'profile_picture']  # Fields from the Profile model
        
    def clean_profile_picture(self):
        if self.cleaned_data.get('delete_profile_picture'):
            return None  # If the delete checkbox is checked, set the profile picture to None
        return self.cleaned_data.get('profile_picture')
        
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']  # Add other fields if necessary
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class PasswordChangeForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    new_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email',
        })
    )

class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label="New password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
    new_password2 = forms.CharField(
        label="Confirm password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
    
#Series Management
class EpisodeForm(forms.Form):
    episode_title = forms.CharField(max_length=100)
    episode_video = forms.FileField()

class SeasonForm(forms.Form):
    season_title = forms.CharField(max_length=100)
    episodes = forms.Form()  # This will be dynamically created per season

class SeriesForm(forms.ModelForm):
    class Meta:
        model = Series
        fields = ['title', 'release_year', 'poster', 'thumbnail', 'description']

class CustomAuthenticationForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise ValidationError(
                "Your account has been deactivated. Please contact the administrator.",
                code='inactive',
            )
