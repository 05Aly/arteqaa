# apps/reviews/urls.py
from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('course/<int:course_id>/create/', views.create_review_view, name='create'),
    path('course/<int:course_id>/', views.course_reviews_view, name='list'),
]
