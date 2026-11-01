from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import Category, Course

User = get_user_model()

class CourseTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.instructor = User.objects.create_user(
            email="inst@example.com", 
            password="pass", 
            full_name="Instructor",
            role="INSTRUCTOR"
        )
        self.category = Category.objects.create(name="Tech")
        self.client.force_authenticate(user=self.instructor)

    def test_create_course(self):
        data = {
            "title": "Django for Beginners",
            "description": "Learn Django",
            "price": "99.99",
            "category": self.category.id
        }
        response = self.client.post('/api/courses/courses/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Course.objects.count(), 1)
        self.assertEqual(Course.objects.get().instructor, self.instructor)
