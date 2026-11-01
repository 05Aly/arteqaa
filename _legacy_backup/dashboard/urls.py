from django.urls import path
from .views import StudentDashboardView, InstructorDashboardView

urlpatterns = [
    path('student/', StudentDashboardView.as_view(), name='student-dashboard'),
    path('instructor/', InstructorDashboardView.as_view(), name='instructor-dashboard'),
]
