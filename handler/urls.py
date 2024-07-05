from django.contrib import admin
from django.urls import path,include
from .views import translate_view
from . import views
urlpatterns = [
    path('',views.translate_view,name="translate"),
]
