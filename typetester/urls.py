from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('test/', views.typing_test, name='typing_test'),
    path('save-result/', views.save_result, name='save_result'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('my-results/', views.my_results, name='my_results'),
]