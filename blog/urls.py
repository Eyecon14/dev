from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import edit_comment, delete_comment, update_comment, reply_comment, like_comment, delete_post, load_more_posts, feedback_view, like_recommendation
from django.contrib.auth import views as auth_views

app_name = 'blog'  # Set the app namespace

urlpatterns = [
    path('', views.view_posts, name='home'),  # Set view_posts as the homepage
    path('posts/', views.view_posts, name='view_posts'),  # Ensure 'view_posts' is the correct name
    path('posts/<int:post_id>/', views.view_post, name='view_post'),
    path('delete_post/<int:post_id>/', views.delete_post, name='delete_post'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('create_post/', views.create_post, name='create_post'),  # Optional: keep for other access
    path('edit_post/<int:post_id>/', views.edit_post, name='edit_post'),
    path('like_post/<int:post_id>/', views.like_post, name='like_post'),
    path('add_comment/<int:post_id>/', views.add_comment, name='add_comment'),
    path('share_post/<int:post_id>/', views.share_post, name='share_post'),
    path('settings/', views.change_settings, name='change_settings'),
    path('profile/<str:username>/', views.user_profile, name='user_profile'),
    path('change_profile_pic/', views.change_profile_pic, name='change_profile_pic'),
    path('edit-comment/<int:comment_id>/', views.edit_comment, name='edit_comment'),
    path('delete_comment/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    path('post/<int:post_id>/toggle-comments/', views.toggle_comments, name='toggle_comments'),
    path('update-comment/<int:comment_id>/', update_comment, name='update_comment'),
    path('add_comment/', views.add_comment, name='add_comment'),
    path('reply_comment/<int:comment_id>/', views.reply_comment, name='reply_comment'),
    path('like_comment/<int:comment_id>/', views.like_comment, name='like_comment'),
    path('load-more-posts/', load_more_posts, name='load_more_posts'),
    path('feedback/', views.feedback_view, name='feedback_view'),  # Separate path for feedback
    path('like/<int:pk>/', like_recommendation, name='like_recommendation'),
    path('feedback/edit/<int:feedback_id>/', views.feedback_edit, name='feedback_edit'),
    path('feedback/delete/<int:pk>/', views.feedback_delete, name='feedback_delete'),
    path('developer-profile/', views.developer_profile, name='developer_profile'),

    path('password_reset/', 
         auth_views.PasswordResetView.as_view(template_name='password_reset.html'), 
         name='password_reset'),
    path('password_reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), 
         name='password_reset_done'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
