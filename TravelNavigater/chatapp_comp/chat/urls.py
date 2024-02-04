from django.urls import path

from . import views

app_name = 'chat'
urlpatterns = [
    path('', views.index, name='index'),  # views.pyのindex関数へアクセス
    path('post', views.post, name='post'),  # views.pyのpost関数へアクセス
    path('lottery', views.lottery, name='lottery'),  # views.pyのlottery関数へアクセス

]