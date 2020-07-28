from django.conf.urls import url
from django.urls import path
from stackoverflow_search import views

urlpatterns = [
    path('',views.Home.as_view(),name='home'),
    url(r'^search/$', views.Search.as_view(), name='search'),

]
