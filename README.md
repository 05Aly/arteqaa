# Edu-Plat LMS

A scalable Learning Management System built with Django and Django REST Framework.

## Features
- Custom User Model with roles (Admin, Instructor, Student)
- JWT Authentication
- Course & Lesson Management (Instructor)
- Enrollment & Progress Tracking (Student)
- Quiz Engine with Auto-grading
- Mock Payment Integration (Checkout -> Enrollment)
- Background Tasks (Celery + Redis)
- Automated Certificate Generation (PDF)
- Cloud Media Storage (Cloudinary)

## Setup

1. **Clone the repository**
2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
4. **Setup Environment Variables**
   Create a `.env` file based on the provided configuration in the project.
5. **Run Migrations**
   ```bash
   python manage.py migrate
   ```
6. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   ```
7. **Run the server**
   ```bash
   python manage.py runserver
   ```

## Background Tasks
To run Celery:
```bash
celery -A core worker -l info
```

## Testing
```bash
python manage.py test
```
