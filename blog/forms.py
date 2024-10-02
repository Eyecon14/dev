from django import forms
from django.contrib.auth.models import User
from .models import Profile, Post, Comment, Recommendation
from .models import Feedback

class UserSignupForm(forms.ModelForm):
    username = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=True)

    class Meta:
        model = Profile
        fields = ['first_name', 'other_name', 'surname', 'contact', 'picture', 'bio']  # Fields from Profile model

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

    def save(self, commit=True):
        # Create the user first
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
        )
        user.set_password(self.cleaned_data['password'])  # Hash password
        if commit:
            user.save()

        # Now create the profile linked to the user
        profile = Profile(
            user=user,
            first_name=self.cleaned_data['first_name'],
            other_name=self.cleaned_data['other_name'],
            surname=self.cleaned_data['surname'],
            contact=self.cleaned_data['contact'],
            picture=self.cleaned_data['picture'],
            bio=self.cleaned_data['bio'],
        )
        if commit:
            profile.save()

        return user

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'picture', 'link']

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'contact', 'first_name', 'surname', 'other_name', 'picture']
        widgets = {
            'bio': forms.Textarea(attrs={'placeholder': 'Enter your bio'}),
            'contact': forms.TextInput(attrs={'placeholder': 'Enter your contact'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'Enter your first name'}),
            'surname': forms.TextInput(attrs={'placeholder': 'Enter your surname'}),
            'other_name': forms.TextInput(attrs={'placeholder': 'Enter your other name'}),
        }

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.fields['picture'].widget.attrs.update({'class': 'form-control-file'})  # Add CSS for file input


class ProfilePictureForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['picture']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']

class RecommendationForm(forms.ModelForm):
    class Meta:
        model = Recommendation
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'placeholder': 'Share your recommendation...', 'rows': 3}),
        }

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'placeholder': 'Leave your feedback...'}),
        }