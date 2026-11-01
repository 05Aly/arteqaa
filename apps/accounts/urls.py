# apps/accounts/urls.py
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/student/', views.student_dashboard, name='student_dashboard'),
    path('dashboard/instructor/', views.instructor_dashboard, name='instructor_dashboard'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    path('instructors/', views.instructors_list_view, name='instructors'),
    path('profile/<path:username>/', views.profile_view, name='profile'),
]

