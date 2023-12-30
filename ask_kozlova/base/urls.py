from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView


urlpatterns = [
    path('', views.index, name='index'),
    path('hot/', views.hot, name='hot'),
    path('tag/<str:tag_name>/', views.tag, name='tag'),
    path('question/<int:question_id>/', views.question, name='question'),
    path('login/', views.log_in, name='login'),
    path('signup/', views.signup, name='signup'),
    path('ask/', views.ask, name='ask'),
    path('profile/edit/', views.edit, name='edit'),
    path('logout/', views.logout, name='logout'),
    path('like/', views.like, name='like'),
    path('dislike/', views.dislike, name='dislike'),
    path('like_answer/', views.like_answer, name='like_answer'),
    path('dislike_answer/', views.dislike_answer, name='dislike_answer'),
    path('correct/', views.correct, name='correct'),
    path('comment/', views.comment, name='comment'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
