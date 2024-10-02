from django.shortcuts import render, get_object_or_404, redirect
from .forms import UserSignupForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .models import Profile, Post, Comment
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from .forms import PostForm, ProfilePictureForm
from django.contrib import messages
from .models import Comment, Reply, Recommendation
from .forms import CommentForm, RecommendationForm
from django.urls import reverse
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.core.paginator import Paginator
from .models import Feedback
from .forms import FeedbackForm

@login_required
def view_posts(request):
    posts = Post.objects.all()  # Fetch all posts

        # Check if the user is a superuser
    is_superuser = request.user.is_superuser

    # Fetch the authenticated users and any additional data needed
    # Assuming you have a User model or similar to fetch users
    authenticated_users = User.objects.filter(is_authenticated=True)
    return render(request, 'view_posts.html', {
        'authenticated_users': authenticated_users,
        'is_superuser': is_superuser,
    })

@login_required
def eyeconlink(request):
    # Ensure only superusers can access this view
    if request.user.is_superuser:
        # Fetch users and any additional data if needed
        users = User.objects.all()  # Modify this as per your requirement
        return render(request, 'eyeconlink.html', {'users': users})
    else:
        # Optionally redirect or raise a 403 Forbidden error
        return render(request, '403.html')  # Create a custom 403 page

def signup(request):
    if request.method == 'POST':
        form = UserSignupForm(request.POST, request.FILES)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Check if username already exists
            if User.objects.filter(username=username).exists():
                return render(request, 'signup.html', {'form': form, 'error': 'Username already taken'})

            try:
                # Create the user
                user = User.objects.create_user(
                    username=username,
                    email=email,
                )
                user.set_password(password)  # Set the password securely
                user.save()

                # Create the profile
                profile = Profile(
                    user=user,
                    first_name=form.cleaned_data['first_name'],
                    other_name=form.cleaned_data['other_name'],
                    surname=form.cleaned_data['surname'],
                    contact=form.cleaned_data['contact'],
                    picture=form.cleaned_data['picture'],
                    bio=form.cleaned_data['bio']
                )
                profile.save()

                return redirect('blog:login')  # Use the namespace for the login page

            except IntegrityError:
                return render(request, 'signup.html', {'form': form, 'error': 'Username or email already taken'})
    else:
        form = UserSignupForm()

    return render(request, 'signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('blog:home')  # Redirect to the home page after login using namespaced URL
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('blog:login')  # Use the namespace for the login page


@login_required  # Ensure only logged-in users can create posts
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user  # Assign the logged-in user as the author
            post.save()
            return redirect('blog:view_posts')
    else:
        form = PostForm()
    
    return render(request, 'create_post.html', {'form': form})

def view_posts(request):
    posts = Post.objects.all().order_by('-created_at')  # Order by latest post
    return render(request, 'view_posts.html', {'posts': posts})

def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('blog:view_posts')  # Include the 'blog' namespace here
    else:
        form = PostForm(instance=post)

    return render(request, 'edit_post.html', {'form': form, 'post': post})

@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user in post.likes.all():
        post.likes.remove(request.user)  # Unlike
    else:
        post.likes.add(request.user)  # Like
    return redirect('blog:view_posts')

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            comment = Comment.objects.create(post=post, author=request.user, content=content)
            comment.save()
    return redirect('blog:view_posts')

@login_required
def share_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    # Increment the share count
    post.share_count += 1
    post.shares.add(request.user)  # Optionally track users who shared the post
    post.save()
    
    return JsonResponse({'success': True, 'share_count': post.share_count})


def view_posts(request):
    posts = Post.objects.all()  # Fetch all posts
    context = {
        'posts': posts,
        'user': request.user,  # Pass the user object to the template
    }
    return render(request, 'view_posts.html', context)

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Profile

@login_required
def change_settings(request):
    # Ensure the user has a profile, or create one if not found
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Update the user's email
        user = request.user
        user.email = request.POST.get('email', user.email)
        user.save()

        # Update profile details
        profile.bio = request.POST.get('bio', profile.bio)
        profile.contact = request.POST.get('contact', profile.contact)
        
        # Handle full name splitting (consider empty fields)
        full_name = request.POST.get('full_name', '')
        if full_name:
            name_parts = full_name.split()
            profile.first_name = name_parts[0] if len(name_parts) > 0 else profile.first_name
            profile.surname = name_parts[-1] if len(name_parts) > 1 else profile.surname
            profile.other_name = " ".join(name_parts[1:-1]) if len(name_parts) > 2 else profile.other_name

        # Check if a new picture is uploaded
        if 'picture' in request.FILES:
            profile.picture = request.FILES['picture']

        # Save the profile
        profile.save()

        # Send a success message and redirect
        messages.success(request, 'Your settings have been updated!')
        return redirect('blog:view_posts')

    # Pass profile details to the template for rendering
    return render(request, 'change_settings.html', {'profile': profile})

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    # Ensure only the author can delete the post
    if request.user != post.author:
        return redirect('view_posts')  # Redirect to 'view_posts' if the user is not the author

    if request.method == 'POST':
        post.delete()
        return redirect('blog:view_posts')  # Redirect to 'view_posts' after deletion

    return render(request, 'delete_post.html', {'post': post})

@login_required
def user_profile(request, username):
    user = get_object_or_404(User, username=username)
    profile = user.profile
    posts = Post.objects.filter(author=user)

    # Check if the logged-in user is already following the profile
    is_following = profile.followers.filter(id=request.user.id).exists()

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'follow':
            if not is_following:  # Only add if not already following
                profile.followers.add(request.user)
        elif action == 'unfollow':
            if is_following:  # Only remove if already following
                profile.followers.remove(request.user)

        # Redirect to the same profile after action to avoid duplicate form submissions
        return redirect('blog:user_profile', username=user.username)

    return render(request, 'user_profile.html', {
        'user': user,
        'profile': profile,
        'posts': posts,
        'is_following': is_following,
        'total_likes': sum(post.total_likes() for post in posts),
        'total_followers': profile.total_followers(),
        'total_following': profile.total_following(),
    })

@login_required
def change_profile_pic(request):
    profile = request.user.profile  # Get the logged-in user's profile

    if request.method == 'POST':
        form = ProfilePictureForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('blog:user_profile', username=request.user.username)  # Redirect to the profile page
    else:
        form = ProfilePictureForm(instance=profile)

    return render(request, 'change_profile_pic.html', {'form': form})

@login_required
def toggle_comments(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user == post.author:
        post.allow_comments = not post.allow_comments
        post.save()
    return redirect('view_posts', post_id=post_id)

@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog:view_posts', post_id=comment.post.id)  # Adjust redirection as per your app's logic
    else:
        form = CommentForm(instance=comment)
    return render(request, 'edit_comment.html', {'form': form, 'comment': comment})

@login_required
def delete_comment(request, comment_id):
    # Use get_object_or_404 to fetch the comment, raising a 404 if not found
    comment = get_object_or_404(Comment, id=comment_id)
    
    # Assuming the comment is linked to a post
    post_id = comment.post.id  # Ensure the comment has a `post` ForeignKey
    
    # Delete the comment
    comment.delete()
    
    # Redirect back to the post's detail page
    return redirect('blog:view_post', post_id=post_id)
   
def toggle_comments(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    post.allow_comments = not post.allow_comments  # Example logic for toggling comments
    post.save()

    # Redirect to the view_posts URL
    return redirect('blog:view_posts')

def some_view(request):
    post_id = 4  # Example ID
    return redirect(reverse('blog:view_posts', args=[post_id]))

@login_required
def update_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            # Redirect to the post view
            return redirect('blog:view_post', post_id=comment.post.id)  # Ensure this is the correct post ID
    else:
        form = CommentForm(instance=comment)
    return render(request, 'update_comment.html', {'form': form, 'comment': comment})

def view_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    return render(request, 'post_detail.html', {'post': post})

@login_required
def like_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user in comment.likes.all():
        comment.likes.remove(request.user)  # Unlike
    else:
        comment.likes.add(request.user)  # Like
    return JsonResponse({
        'success': True,
        'total_likes': comment.likes.count(),
    })

@login_required
def reply_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            reply = Comment.objects.create(post=comment.post, author=request.user, content=content, parent=comment)
            reply.save()
            return JsonResponse({
                'success': True,
                'content': reply.content,
                'created_at': reply.created_at.strftime('%Y-%m-%d %H:%M:%S'),  # Format the datetime as needed
            })
    return JsonResponse({'success': False, 'error': 'Content is required.'})

def load_more_posts(request):
    page_number = request.GET.get('page', 1)
    posts = Post.objects.all().order_by('-created_at')  # Modify as needed
    paginator = Paginator(posts, 5)  # Load 5 posts at a time
    page_obj = paginator.get_page(page_number)

    if page_obj.has_next():
        context = {'posts': page_obj}
        html = render_to_string('your_template_path.html', context)  # Use your post template path
        return JsonResponse(html, safe=False)
    else:
        return JsonResponse(None, safe=False)  # No more posts to load

@login_required
def feedback_view(request):
    if request.method == "POST":
        form = RecommendationForm(request.POST)
        if form.is_valid():
            recommendation = form.save(commit=False)
            recommendation.user = request.user
            recommendation.save()
            return redirect('blog:feedback_view')
    else:
        form = RecommendationForm()

    recommendations = Recommendation.objects.all().order_by('-id')
    paginator = Paginator(recommendations, 5)  # Show 5 recommendations per page
    page_number = request.GET.get('page')
    recommendations_page = paginator.get_page(page_number)

    return render(request, 'feedback.html', {
        'form': form,
        'recommendations': recommendations_page,
    })

@login_required
def like_recommendation(request, pk):
    if request.method == "POST":
        try:
            recommendation = Recommendation.objects.get(pk=pk)
            
            if request.user in recommendation.likes.all():
                recommendation.likes.remove(request.user)
                message = "Unlike successful"
            else:
                recommendation.likes.add(request.user)
                message = "Like successful"
                
            recommendation.save()
            
            return JsonResponse({
                "success": True,
                "message": message,
                "likes_count": recommendation.likes.count()
            })
        except Recommendation.DoesNotExist:
            return JsonResponse({"error": "Recommendation not found"}, status=404)

    return JsonResponse({"error": "Invalid request method"}, status=400)

def feedback_view(request):
    # Fetch all feedback in reverse order (newest first)
    feedback_list = Feedback.objects.all().order_by('-created_at')

    # Pagination
    paginator = Paginator(feedback_list, 5)  # Show 5 feedback per page
    page_number = request.GET.get('page')
    feedback_page = paginator.get_page(page_number)

    # If the form is submitted
    if request.method == "POST":
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user = request.user  # Set the user
            feedback.save()
            return redirect('blog:feedback_view')  # Redirect after POST
    else:
        form = FeedbackForm()

    context = {
        'form': form,
        'recommendations': feedback_page,
    }
    return render(request, 'feedback.html', context)

def feedback_edit(request, feedback_id):
    feedback = get_object_or_404(Feedback, id=feedback_id)
    if request.method == 'POST':
        form = FeedbackForm(request.POST, instance=feedback)
        if form.is_valid():
            form.save()
            # Redirect to the feedback page after saving
            return redirect('blog:feedback_view')  # Replace 'feedback_view' with the correct name of your feedback page URL
    else:
        form = FeedbackForm(instance=feedback)

    return render(request, 'feedback_edit.html', {
        'form': form,
        'feedback': feedback,
    })

def feedback_delete(request, pk):
    feedback = get_object_or_404(Feedback, pk=pk)
    feedback.delete()
    return redirect('blog:feedback_view')

def developer_profile(request):
    return render(request, 'developer_profile.html')