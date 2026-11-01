# apps/courses/urls.py
from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.CourseListView.as_view(), name='list'),
    path('create/', views.InstructorCourseCreateView.as_view(), name='create'),
    path('contact/', views.contact_view, name='contact'),
    path('<str:slug>/edit/', views.InstructorCourseEditView.as_view(), name='edit'),
    path('<str:slug>/manage/', views.instructor_lesson_manage_view, name='manage_content'),
    path('<str:slug>/', views.course_detail_view, name='detail'),
    path('<str:course_slug>/learn/<str:lesson_slug>/', views.lesson_player_view, name='player'),
]

