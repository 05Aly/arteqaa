# apps/enrollments/urls.py
from django.urls import path
from . import views

app_name = 'enrollments'

urlpatterns = [
    path('enroll/<int:course_id>/', views.enroll_view, name='enroll'),
    path('mark-complete/<int:lesson_id>/', views.mark_lesson_complete, name='mark_complete'),
    path('my-courses/', views.my_courses_view, name='my_courses'),
    path('certificate/<uuid:certificate_id>/', views.certificate_view, name='certificate'),
]
