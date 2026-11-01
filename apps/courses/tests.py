# apps/courses/tests.py
from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.models import User, InstructorProfile
from apps.categories.models import Category
from apps.courses.models import Course, Section, Lesson, Resource
from apps.enrollments.models import Enrollment, LessonProgress, Certificate
from apps.reviews.models import Review
import json


class PlatformEndToEndTest(TestCase):
    def setUp(self):
        self.client = Client()
        # Create Instructor
        self.instructor = User.objects.create_user(
            username='inst@ertiqa.edu',
            email='inst@ertiqa.edu',
            password='StrongPassword123!',
            first_name='أحمد',
            last_name='المدرب',
            role='instructor'
        )
        # Create Student
        self.student = User.objects.create_user(
            username='student@ertiqa.edu',
            email='student@ertiqa.edu',
            password='StrongPassword123!',
            first_name='محمد',
            last_name='الطالب',
            role='student'
        )
        # Create Category (Arabic name to verify Unicode slug generation)
        self.category = Category.objects.create(
            name='تطوير الويب والبرمجة',
            icon='code',
            color='#3B82F6'
        )
        # Create Course
        self.course = Course.objects.create(
            title='دورة احتراف بايثون وجانغو الشاملة',
            description='تعلم بناء تطبيقات الويب من الصفر للاحتراف',
            instructor=self.instructor,
            category=self.category,
            price=100.00,
            discount_price=75.00,
            level='intermediate',
            status='published',
            is_featured=True
        )
        self.section = Section.objects.create(
            course=self.course,
            title='القسم الأول: الأساسيات',
            order=1
        )
        self.lesson1 = Lesson.objects.create(
            section=self.section,
            title='الدرس الأول: مقدمة الكورس',
            video_url='https://www.youtube.com/watch?v=dQw4w9WgXcQ',
            duration_seconds=600,
            content='محتوى الدرس الأول',
            is_preview=True,
            order=1
        )
        self.lesson2 = Lesson.objects.create(
            section=self.section,
            title='الدرس الثاني: إعداد البيئة',
            duration_seconds=900,
            content='محتوى الدرس الثاني',
            is_preview=False,
            order=2
        )

    def test_instructor_profile_signal_created(self):
        self.assertTrue(InstructorProfile.objects.filter(user=self.instructor).exists())

    def test_public_pages_render_200(self):
        for url in [
            reverse('home'),
            reverse('courses:list'),
            reverse('courses:contact'),
            reverse('accounts:instructors'),
            reverse('accounts:profile', kwargs={'username': self.instructor.username}),
            reverse('courses:detail', kwargs={'slug': self.course.slug}),
            reverse('courses:player', kwargs={'course_slug': self.course.slug, 'lesson_slug': self.lesson1.slug}),
        ]:
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 200, f"Failed on {url}")

    def test_paywall_blocks_non_preview_lesson(self):
        url = reverse('courses:player', kwargs={'course_slug': self.course.slug, 'lesson_slug': self.lesson2.slug})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 302)

    def test_student_enrollment_progress_certificate_and_review(self):
        self.client.login(username='student@ertiqa.edu', password='StrongPassword123!')

        # Enroll
        enroll_url = reverse('enrollments:enroll', kwargs={'course_id': self.course.id})
        resp = self.client.post(enroll_url)
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(Enrollment.objects.filter(student=self.student, course=self.course).exists())

        # Access locked lesson now allowed
        player_url = reverse('courses:player', kwargs={'course_slug': self.course.slug, 'lesson_slug': self.lesson2.slug})
        self.assertEqual(self.client.get(player_url).status_code, 200)

        # Complete lesson 1 (50%)
        r1 = self.client.post(reverse('enrollments:mark_complete', kwargs={'lesson_id': self.lesson1.id}))
        data1 = r1.json()
        self.assertTrue(data1['success'])
        self.assertEqual(data1['progress'], 50.0)
        self.assertFalse(data1['is_course_completed'])

        # Complete lesson 2 (100% + Certificate issued)
        r2 = self.client.post(reverse('enrollments:mark_complete', kwargs={'lesson_id': self.lesson2.id}))
        data2 = r2.json()
        self.assertTrue(data2['success'])
        self.assertEqual(data2['progress'], 100.0)
        self.assertTrue(data2['is_course_completed'])
        self.assertIsNotNone(data2['certificate_id'])

        # View Certificate
        cert_url = reverse('enrollments:certificate', kwargs={'certificate_id': data2['certificate_id']})
        self.assertEqual(self.client.get(cert_url).status_code, 200)

        # Submit Review
        rev_url = reverse('reviews:create', kwargs={'course_id': self.course.id})
        rev_resp = self.client.post(
            rev_url,
            data=json.dumps({'rating': 5, 'comment': 'كورس رائع ومفيد جداً!'}),
            content_type='application/json'
        )
        self.assertEqual(rev_resp.status_code, 200)
        self.assertEqual(Review.objects.count(), 1)
        self.assertEqual(self.course.average_rating, 5.0)

    def test_instructor_dashboard_and_curriculum_management(self):
        self.client.login(username='inst@ertiqa.edu', password='StrongPassword123!')
        self.assertEqual(self.client.get(reverse('accounts:instructor_dashboard')).status_code, 200)

        manage_url = reverse('courses:manage_content', kwargs={'slug': self.course.slug})
        self.assertEqual(self.client.get(manage_url).status_code, 200)

        # Add section via manage_content
        self.client.post(manage_url, {'action': 'add_section', 'title': 'القسم الثاني', 'order': 2})
        self.assertEqual(self.course.sections.count(), 2)

    def test_instructor_course_create_and_edit_views(self):
        self.client.login(username='inst@ertiqa.edu', password='StrongPassword123!')
        create_url = reverse('courses:create')
        resp = self.client.get(create_url)
        self.assertEqual(resp.status_code, 200)

        # Create a course
        post_resp = self.client.post(create_url, {
            'title': 'كورس تصميم النظم وقواعد البيانات',
            'description': 'شرح شامل لتصميم وتطبيع قواعد البيانات العلائقية',
            'category': self.category.id,
            'price': '85.00',
            'discount_price': '60.00',
            'level': 'advanced',
            'language': 'العربية',
            'status': 'published',
            'is_featured': True
        })
        self.assertEqual(post_resp.status_code, 302)
        new_course = Course.objects.get(title='كورس تصميم النظم وقواعد البيانات')
        self.assertIsNotNone(new_course.slug)

        # Edit the course
        edit_url = reverse('courses:edit', kwargs={'slug': new_course.slug})
        edit_resp = self.client.get(edit_url)
        self.assertEqual(edit_resp.status_code, 200)

    def test_contact_page_get_and_post(self):
        contact_url = reverse('courses:contact')
        get_resp = self.client.get(contact_url)
        self.assertEqual(get_resp.status_code, 200)

        post_resp = self.client.post(contact_url, {
            'name': 'عبد الله الباحث',
            'email': 'abdullah@example.com',
            'subject': 'استفسار عن التسجيل في الدبلوم',
            'message': 'السلام عليكم، أود الاستفسار عن شروط القبول والتسجيل.'
        })
        self.assertEqual(post_resp.status_code, 302)
        # Follow redirect
        follow_resp = self.client.get(post_resp.url)
        self.assertEqual(follow_resp.status_code, 200)

    def test_student_dashboard_and_edit_profile(self):
        self.client.login(username='student@ertiqa.edu', password='StrongPassword123!')
        dash_url = reverse('accounts:student_dashboard')
        self.assertEqual(self.client.get(dash_url).status_code, 200)

        edit_profile_url = reverse('accounts:edit_profile')
        self.assertEqual(self.client.get(edit_profile_url).status_code, 200)

        post_resp = self.client.post(edit_profile_url, {
            'first_name': 'محمد المحدث',
            'last_name': 'المنصور',
            'bio': 'طالب شغوف بعلوم الحاسب والمعرفة.'
        })
        self.assertEqual(post_resp.status_code, 302)
        self.student.refresh_from_db()
        self.assertEqual(self.student.first_name, 'محمد المحدث')
        follow_resp = self.client.get(post_resp.url)
        self.assertEqual(follow_resp.status_code, 200)

    def test_custom_404_page(self):
        resp = self.client.get('/non-existent-page-url-12345/')
        self.assertEqual(resp.status_code, 404)
        self.assertContains(resp, '404', status_code=404)


