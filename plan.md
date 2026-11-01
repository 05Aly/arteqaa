# Edu-Plat: Comprehensive Learning Management System (LMS)
## Current Project Specification & Architecture Plan

This document outlines the complete architecture, features, database schema, and workflows of the current production-ready LMS platform.

---

## 1. Project Overview
A scalable, modern Learning Management System (LMS) built with a Monolithic-ish Django architecture. It handles user authentication, course delivery, assessments, content management, role-based access control, and payment mock integration. The frontend utilizes Django Templates infused with a custom "Glassmorphism" design system and asynchronous JavaScript (Vanilla JS) for dynamic updates.

**Core Technologies Stack:**
- **Backend:** Django 6.x, Django REST Framework (DRF)
- **Database:** SQLite (development) / PostgreSQL (production ready)
- **Caching & Background Tasks:** Redis + Celery
- **Storage:** Cloudinary (configured for media storage)
- **Admin Theme:** Django Unfold (modern Tailwind-based admin panel)
- **Frontend:** Django Templates, Vanilla CSS (Glassmorphism UI), Vanilla JS
- **Authentication:** JWT (JSON Web Tokens) via simplejwt

---

## 2. Database Schema Design (Models)

### 2.1 Users & Accounts (`users` app)
- **User (Custom AbstractUser):**
  - Fields: `email` (Username field), `full_name`, `role` (Admin, Instructor, Student), `profile_image`, `bio`.
- **Profile:**
  - Fields: `user` (OneToOne), `profile_image`, `bio`, `purchased_courses` (ManyToMany to Course), `joined_at`.

### 2.2 Educational Content (`courses` app)
- **Category:**
  - Fields: `name`, `slug`, `description`.
- **Course:**
  - Fields: `title`, `slug`, `description`, `price`, `thumbnail`, `category`, `instructor`, `created_at`, `updated_at`.
- **Module:**
  - Fields: `course`, `title`, `order`.
- **Lesson:**
  - Fields: `course` (direct link for standalone lessons), `module` (hierarchical link), `title`, `video_url`, `pdf_file`, `content`, `duration`, `order`, `is_preview`.
  - *Logic:* Lessons can be assigned directly to a Course or inside a Module.
- **Announcement:**
  - Fields: `course`, `title`, `content`, `created_at`.

### 2.3 Access Control & Payments (`payments` app)
- **Enrollment (Inside `courses` app):**
  - Fields: `student`, `course`, `is_active`, `enrolled_at`, `progress`.
  - *Logic:* Acts as the primary Paywall gateway.
- **Payment:**
  - Fields: `student`, `course`, `amount`, `transaction_id`, `status` (PENDING, COMPLETED, FAILED), `created_at`.

### 2.4 Assessments & Interactions (`courses` app)
- **Quiz:** `course`, `title`.
- **Question:** `quiz`, `question_text`, `type` (MCQ, True/False).
- **Answer:** `question`, `answer_text`, `is_correct`.
- **Review:** `student`, `course`, `rating`, `review_text`, `created_at`.
- **Comment:** `lesson`, `user`, `content`, `created_at`.

---

## 3. Core Business Logic & Workflows

### 3.1 Paywall & Lesson Access System
- **API Protection:** The `LessonViewSet` checks if a lesson is marked as `is_preview=True`. If not, it validates whether an active `Enrollment` exists for the requesting student.
- **Unauthorized Access:** Non-enrolled users are blocked (HTTP 403) and returned a payload containing the `buy_url` to redirect them to the purchase page.
- **Content Restriction:** Only enrolled students and admins/instructors can access video streams, lesson files, and comments.

### 3.2 Student Dashboard (Feed System)
- The API (`StudentDashboardView`) dynamically aggregates and returns:
  - **Learning Progress:** Courses the student is enrolled in along with completion percentages.
  - **Recent Lessons:** Up to 5 most recently added lessons across enrolled courses.
  - **Announcements:** Up to 5 recent announcements from instructors of enrolled courses.
  - **Recommended Courses:** Up to 3 courses the student is NOT currently enrolled in.

### 3.3 Enrollment & Checkout Flow
- **Checkout Process:** Clicking "Enroll" on the frontend triggers an API POST request to `/api/payments/checkout/` with the JWT token.
- **Mock Payment:** The system creates a `Payment` object marked as `COMPLETED` and auto-generates a `transaction_id`.
- **Auto-Enrollment:** An active `Enrollment` record is instantly generated, unlocking course content.

### 3.4 Interactive Community (Comments)
- Comments can be added to individual lessons via the `CommentViewSet`.
- **Security Rule:** The backend strictly verifies enrollment before accepting a POST request to add a comment.

---

## 4. Admin Panel Architecture (Django Unfold)

The Django admin is heavily customized using **Django Unfold** to provide a sleek, dark-mode compatible interface:
- **Dashboard Sidebar Navigation:** Custom groupings for `Users & Accounts`, `Educational Content`, `Assessments`, and `Enrollment & Payments`.
- **Course Management:** 
  - `CourseAdmin` uses Inlines to allow creating Modules, Direct Lessons, and Announcements directly from the single Course edit page.
- **Profiles Management:** Profiles are managed directly within the `Users & Accounts` tab for detailed insights into student histories.
- **Analytics:** Data filtering and search functionalities are integrated across Enrollments, Payments, and Reviews.

---

## 5. Frontend UI/UX (Templates + JS)

The UI is built using a modern **Glassmorphism** aesthetic defined in `style.css`:
- **Pages:**
  - `index.html`: Landing page with dynamic navigation.
  - `courses.html`: Course catalog fetched asynchronously via `/api/courses/courses/`.
  - `course_detail.html`: Displays course info, grouped modules, direct lessons ("Other Lessons"), and an AJAX checkout button.
  - `lesson_detail.html`: Renders the secure video player, PDF downloads, and interactive comment threads.
  - `dashboard.html`: The Student Hub displaying statistics, active courses, recent lessons, and announcements.
  - `login.html` / `register.html`: Secure JWT-based authentication forms.
- **JavaScript Engine (`main.js`):**
  - Handles token storage (`localStorage`), dynamic DOM injection, logout routing, and seamless API calls without page reloads.

---

## 6. Deployment & Security Readiness

### 6.1 Security Optimizations
- **JWT Authentication:** Stateful sessions are avoided in API interactions to ensure mobility and cross-platform readiness.
- **Endpoint Security:** All transactional and content-delivery endpoints strictly enforce `IsAuthenticated` and custom ownership permissions (`IsInstructorOrReadOnly`).
- **CORS Setup:** Configured to handle cross-origin requests securely.

### 6.2 Asset & Media Management
- Configured to use `MediaCloudinaryStorage` out of the box, meaning video and image uploads bypass the main server and go directly to a CDN, ensuring scalability.
- Static files optimized via `WhiteNoiseMiddleware`.

## 7. Future Expansion Potential
- **Instructor Dashboard Frontend:** Add specific template views for instructors to track revenue and upload courses outside of the Django Admin.
- **Payment Gateway Integration:** Swap the mock logic in `payments/views.py` with actual Stripe, Paymob, or Fawry webhooks.
- **Real-Time Features:** Upgrade comments to WebSockets (Django Channels) for live chat during video lessons.