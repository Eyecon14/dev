from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    contact = models.CharField(max_length=15, blank=True)
    first_name = models.CharField(max_length=50)
    other_name = models.CharField(max_length=50, blank=True)
    surname = models.CharField(max_length=50)
    picture = models.ImageField(upload_to='profile_pictures/', default='profile_pictures/default-profile.png')
    followers = models.ManyToManyField(User, related_name='following', blank=True)
    following_count = models.PositiveIntegerField(default=0)  # Following count
    followers = models.ManyToManyField(User, related_name='following', blank=True)

    def __str__(self):
        return self.user.username

    # Count total followers of a user
    def total_followers(self):
        return self.followers.count()

    # Count total following (how many people this user follows)
    def total_following(self):
        return self.user.following.count()


class Post(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    picture = models.ImageField(upload_to='post_images/', blank=True, null=True)
    link = models.URLField(max_length=200, blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)  # Author of the post
    created_at = models.DateTimeField(auto_now_add=True)  # Auto-add date/time when created
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)  # Users who liked the post
    share_count = models.PositiveIntegerField(default=0)
    allow_comments = models.BooleanField(default=True)

    shares = models.ManyToManyField(User, related_name='shared_posts', blank=True)

    def total_likes(self):
        return self.likes.count()
    

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='liked_comments', blank=True)

    def total_likes(self):
        return self.likes.count()

    def __str__(self):
        return f"{self.user.username}: {self.content[:20]}"

class Reply(models.Model):
    comment = models.ForeignKey(Comment, related_name='replies', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class PostShares(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Recommendation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    likes = models.ManyToManyField(User, related_name='liked_recommendations', blank=True)

    def __str__(self):
        return f'{self.user.username}: {self.message[:20]}...'
    

class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()  # Changed from 'content' to 'message'

        # Add date and time fields
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Feedback by {self.user.username}"