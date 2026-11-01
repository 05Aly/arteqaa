# apps/core/management/commands/seed_data.py
import uuid
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.accounts.models import User, InstructorProfile
from apps.categories.models import Category
from apps.courses.models import Course, Section, Lesson, Resource
from apps.enrollments.models import Enrollment, LessonProgress, Certificate
from apps.reviews.models import Review


class Command(BaseCommand):
    help = "بذر بيانات أكاديمية وتراثية متكاملة لمنصة ارتقاء (Seed Academic Data)"

    def handle(self, *args, **options):
        self.stdout.write("==================================================")
        self.stdout.write("  Starting Academic Data Seeding for Ertiqa...")
        self.stdout.write("==================================================")

        # -------------------------------------------------------------
        # 1. الأساتذة والعلماء (Instructors)
        # -------------------------------------------------------------
        instructors_data = [
            {
                'username': 'dr_saadi@ertiqa.edu',
                'email': 'dr_saadi@ertiqa.edu',
                'first_name': 'د. عبد الرحمن',
                'last_name': 'السعدي',
                'role': 'instructor',
                'title': 'أستاذ هندسة البرمجيات والنظم الموزعة',
                'expertise': 'هندسة البرمجيات، معمارية السحاب، لغات بايثون وغو، الأنظمة الضخمة',
                'bio': 'باحث وأستاذ جامعي حاصل على الدكتوراه في علوم الحاسب وهندسة النظم. أشرف على العديد من الأطروحات العلمية والمشاريع السحابية الكبرى.',
                'social_links': {'github': 'https://github.com', 'linkedin': 'https://linkedin.com'},
            },
            {
                'username': 'dr_sara@ertiqa.edu',
                'email': 'dr_sara@ertiqa.edu',
                'first_name': 'أ. د. سارة',
                'last_name': 'المنصور',
                'role': 'instructor',
                'title': 'أستاذة الذكاء الاصطناعي وتعلم الآلة',
                'expertise': 'الشبكات العصبية العميقة، معالجة اللغات الطبيعية، النماذج التوليدية',
                'bio': 'باحثة أولى ومستشارة في تطبيقات الذكاء الاصطناعي التوليدي. حائزة على جوائز تميز أكاديمية في نمذجة المعرفة الحاسوبية.',
                'social_links': {'linkedin': 'https://linkedin.com', 'twitter': 'https://twitter.com'},
            },
            {
                'username': 'eng_tariq@ertiqa.edu',
                'email': 'eng_tariq@ertiqa.edu',
                'first_name': 'م. طارق',
                'last_name': 'الزهراني',
                'role': 'instructor',
                'title': 'استشاري الأمن السيبراني واختبار الاختراق',
                'expertise': 'أمن الشبكات، التحقيق الرقمي، هندسة الحماية الدفاعية، التشفير',
                'bio': 'خبير معتمد في الأمن السيبراني (CISSP, CEH) مع أكثر من 15 عاماً في حماية البنى التحتية للمؤسسات والمصارف.',
                'social_links': {'github': 'https://github.com'},
            },
            {
                'username': 'dr_fatima@ertiqa.edu',
                'email': 'dr_fatima@ertiqa.edu',
                'first_name': 'د. فاطمة',
                'last_name': 'الأندلسي',
                'role': 'instructor',
                'title': 'أستاذة إدارة الأعمال الرقمية والقيادة التنفيذية',
                'expertise': 'التحول الرقمي، إدارة المشروعات الاحترافية PMP، استراتيجيات الابتكار',
                'bio': 'أستاذة إدارة الأعمال ومستشارة التطوير القيادي للمنظمات الرقمية والمصرفية بالمنطقة.',
                'social_links': {'linkedin': 'https://linkedin.com'},
            },
            {
                'username': 'dr_bader@ertiqa.edu',
                'email': 'dr_bader@ertiqa.edu',
                'first_name': 'الشيخ المؤرخ بدر',
                'last_name': 'الهاشمي',
                'role': 'instructor',
                'title': 'أستاذ فلسفة المعرفة وتاريخ العلوم',
                'expertise': 'فلسفة العلوم، المنطق التراثي، مناهج البحث والتحقيق الأكاديمي',
                'bio': 'مؤلف وباحث ومحقق في التراث الفكري وفلسفة العلوم والمنطق عند علماء الحضارة الإسلامية.',
                'social_links': {},
            },
        ]

        instructors = {}
        for item in instructors_data:
            user, created = User.objects.get_or_create(
                email=item['email'],
                defaults={
                    'username': item['username'],
                    'first_name': item['first_name'],
                    'last_name': item['last_name'],
                    'role': item['role'],
                    'bio': item['bio'],
                    'social_links': item['social_links'],
                    'is_verified': True,
                }
            )
            if created or not user.check_password('AdminPass123!'):
                user.set_password('AdminPass123!')
                user.save()

            profile, _ = InstructorProfile.objects.get_or_create(user=user)
            profile.title = item['title']
            profile.expertise = item['expertise']
            profile.save()
            instructors[item['email']] = user
            status_text = "تم إنشاء" if created else "تحديث"
            self.stdout.write(f"  [+] Instructor: {user.email}")

        # -------------------------------------------------------------
        # 2. الطلاب والباحثين (Students)
        # -------------------------------------------------------------
        students_data = [
            {
                'email': 'student1@ertiqa.edu',
                'username': 'student1@ertiqa.edu',
                'first_name': 'محمد',
                'last_name': 'الكندي',
                'bio': 'باحث ماجستير في تقنية المعلومات وشغوف بهندسة البيانات.',
            },
            {
                'email': 'student2@ertiqa.edu',
                'username': 'student2@ertiqa.edu',
                'first_name': 'مريم',
                'last_name': 'القحطاني',
                'bio': 'مهندسة برمجيات تسعى للتخصص المتقدم في الذكاء الاصطناعي.',
            },
            {
                'email': 'student3@ertiqa.edu',
                'username': 'student3@ertiqa.edu',
                'first_name': 'عمر',
                'last_name': 'بن يوسف',
                'bio': 'طالب جامعي شغوف بالبرمجيات الحرة وتاريخ العلوم.',
            },
        ]

        # Check existing student user (aly01emad@gmail.com) and update names
        existing_student = User.objects.filter(email='aly01emad@gmail.com').first()
        if existing_student:
            if not existing_student.first_name:
                existing_student.first_name = 'علي'
                existing_student.last_name = 'عماد'
                existing_student.bio = 'طالب علم باحث في التقنيات الحديثة.'
                existing_student.save()

        students = []
        for s in students_data:
            st, created = User.objects.get_or_create(
                email=s['email'],
                defaults={
                    'username': s['username'],
                    'first_name': s['first_name'],
                    'last_name': s['last_name'],
                    'role': 'student',
                    'bio': s['bio'],
                }
            )
            if created or not st.check_password('StudentPass123!'):
                st.set_password('StudentPass123!')
                st.save()
            students.append(st)

        if existing_student:
            students.append(existing_student)

        self.stdout.write(f"[OK] Prepared {len(students)} student accounts.")

        # -------------------------------------------------------------
        # 3. الأروقة والتصنيفات المعرفية (Categories)
        # -------------------------------------------------------------
        categories_data = [
            {'name': 'هندسة البرمجيات والنظم', 'icon': 'terminal', 'color': '#671120'},
            {'name': 'الذكاء الاصطناعي وعلم البيانات', 'icon': 'psychology', 'color': '#C29B53'},
            {'name': 'الأمن السيبراني وحماية الشبكات', 'icon': 'security', 'color': '#1B5E4B'},
            {'name': 'إدارة الأعمال والقيادة التنفيذية', 'icon': 'analytics', 'color': '#8C6A2E'},
            {'name': 'التصميم وتجربة المستخدم الأكاديمية', 'icon': 'design_services', 'color': '#B91C1C'},
            {'name': 'التراث العلمي وفلسفة المعرفة', 'icon': 'auto_stories', 'color': '#4A0E17'},
        ]

        categories = {}
        for c in categories_data:
            cat, _ = Category.objects.get_or_create(
                name=c['name'],
                defaults={'icon': c['icon'], 'color': c['color']}
            )
            categories[c['name']] = cat
        self.stdout.write(f"[OK] Prepared {len(categories)} categories.")

        # -------------------------------------------------------------
        # 4. المساقات الأكاديمية، الأبواب، والمحاضرات (Courses & Curriculum)
        # -------------------------------------------------------------
        courses_plan = [
            {
                'title': 'الدبلوم العالي في هندسة البرمجيات ومعمارية السحاب المتقدمة',
                'instructor': instructors['dr_saadi@ertiqa.edu'],
                'category': categories['هندسة البرمجيات والنظم'],
                'price': 180.00,
                'discount_price': 120.00,
                'level': 'advanced',
                'language': 'العربية',
                'status': 'published',
                'is_featured': True,
                'preview_video': 'https://www.youtube.com/watch?v=8j0UDiN7my4',
                'description': (
                    'دبلوم أكاديمي رصين يغطي الأسس المعمارية لبناء النظم الموزعة واسعة النطاق، '
                    'من تصميم الواجهات الخلفية وقواعد البيانات الضخمة، وحتى النشر الآمن على البنى السحابية الحديثة.'
                ),
                'sections': [
                    {
                        'title': 'الباب الأول: الأسس النظرية وتصميم المعمارية الموزعة',
                        'order': 1,
                        'lessons': [
                            {
                                'title': 'المحاضرة الأولى: مدخل إلى الأنماط المعمارية (Microservices vs Monolith)',
                                'video_url': 'https://www.youtube.com/watch?v=8j0UDiN7my4',
                                'duration': 1800,
                                'is_preview': True,
                                'content': 'شرح مفاهيم الربط اللامتزامن، ونقاط الاختناق في النظم التقليدية مقارنة بالنظم الموزعة.',
                                'resource_title': 'مذكرة الأنماط المعمارية الحديثة PDF',
                            },
                            {
                                'title': 'المحاضرة الثانية: معايير تصميم واجهات RESTful و gRPC الفائقة',
                                'video_url': 'https://www.youtube.com/watch?v=8j0UDiN7my4',
                                'duration': 2400,
                                'is_preview': False,
                                'content': 'مقارنة بروتوكول HTTP/2 و Protocol Buffers في تقليل زمن استجابة الخدمات المصغرة.',
                                'resource_title': 'كود ومخطط بروتوكول الاتصال ZIP',
                            },
                        ]
                    },
                    {
                        'title': 'الباب الثاني: إدارة البيانات والتناسق الموزع (Distributed Data & Caching)',
                        'order': 2,
                        'lessons': [
                            {
                                'title': 'المحاضرة الثالثة: استراتيجيات التخزين المؤقت وتوزيع الأحمال بواسطة Redis',
                                'video_url': 'https://www.youtube.com/watch?v=8j0UDiN7my4',
                                'duration': 2100,
                                'is_preview': False,
                                'content': 'تطبيقات عملية على نمط Cache-Aside وحل إشكالات تزامن الذاكرة المخفية.',
                            },
                            {
                                'title': 'المحاضرة الرابعة: نمط الأحداث الموزعة عبر Apache Kafka',
                                'video_url': 'https://www.youtube.com/watch?v=8j0UDiN7my4',
                                'duration': 3000,
                                'is_preview': False,
                                'content': 'معالجة تدفق البيانات اللحظي وتأمين تسليم الرسائل بدقة تامة.',
                            },
                        ]
                    }
                ]
            },
            {
                'title': 'المرجع الشامل في الذكاء الاصطناعي والشبكات العصبية العميقة',
                'instructor': instructors['dr_sara@ertiqa.edu'],
                'category': categories['الذكاء الاصطناعي وعلم البيانات'],
                'price': 220.00,
                'discount_price': 150.00,
                'level': 'advanced',
                'language': 'العربية',
                'status': 'published',
                'is_featured': True,
                'preview_video': 'https://www.youtube.com/watch?v=aircAruvnKk',
                'description': (
                    'مساق علمي استقصائي يغوص في الرياضيات الرياضية والخوارزمية العميقة الكامنة وراء الذكاء الاصطناعي الحديث، '
                    'من الانحدار الخطي وشبكات التلافيف وحتى نماذج المحولات (Transformers) والنماذج التوليدية.'
                ),
                'sections': [
                    {
                        'title': 'الباب الأول: أسس الجبر الخطي وحساب التفاضل لشبكات الأعصاب',
                        'order': 1,
                        'lessons': [
                            {
                                'title': 'المحاضرة الأولى: المصفوفات والتفاضل الاتجاهي وانحدار الميل (Gradient Descent)',
                                'video_url': 'https://www.youtube.com/watch?v=aircAruvnKk',
                                'duration': 2400,
                                'is_preview': True,
                                'content': 'فهم كيف تتعلم الخوارزميات عبر حساب المشتقات الجزئية ونظرية الانتشار العكسي (Backpropagation).',
                                'resource_title': 'ملخص المعادلات الرياضية PDF',
                            },
                            {
                                'title': 'المحاضرة الثانية: بناء شبكة عصبية متعددة الطبقات من الصفر ببايثون الخالص',
                                'video_url': 'https://www.youtube.com/watch?v=aircAruvnKk',
                                'duration': 3600,
                                'is_preview': False,
                                'content': 'تطبيق عملي لا يعتمد على أطر جاهزة لتأصيل استيعاب العمليات المصفوفية.',
                            },
                        ]
                    },
                    {
                        'title': 'الباب الثاني: بنية نماذج المحولات (Transformers Architecture)',
                        'order': 2,
                        'lessons': [
                            {
                                'title': 'المحاضرة الثالثة: آلية الانتباه الذاتي (Self-Attention Mechanism)',
                                'video_url': 'https://www.youtube.com/watch?v=aircAruvnKk',
                                'duration': 2700,
                                'is_preview': False,
                                'content': 'شرح ورقة Attention Is All You Need الرائدة وتحليل مصفوفات Q, K, V.',
                            },
                        ]
                    }
                ]
            },
            {
                'title': 'أصول الأمن السيبراني الدفاعي واختبار الاختراق المنهجي',
                'instructor': instructors['eng_tariq@ertiqa.edu'],
                'category': categories['الأمن السيبراني وحماية الشبكات'],
                'price': 150.00,
                'discount_price': 95.00,
                'level': 'intermediate',
                'language': 'العربية',
                'status': 'published',
                'is_featured': True,
                'preview_video': 'https://www.youtube.com/watch?v=inWWhr5tnEA',
                'description': (
                    'دورة منهجية متكاملة تمنح الدارس الخبرة الميدانية اللازمة لكشف الثغرات الأمنية في التطبيقات والشبكات، '
                    'مع تدريبات عملية على بناء جدران الحماية وتحصين الخوادم المؤسسية.'
                ),
                'sections': [
                    {
                        'title': 'الباب الأول: استطلاع وتدقيق منافذ الشبكات والبروتوكولات',
                        'order': 1,
                        'lessons': [
                            {
                                'title': 'المحاضرة الأولى: مبادئ فحص المنافذ واستكشاف الخدمات المفتوحة',
                                'video_url': 'https://www.youtube.com/watch?v=inWWhr5tnEA',
                                'duration': 1800,
                                'is_preview': True,
                                'content': 'تطبيقات على Nmap وتحليل ترويسات حزم TCP/IP لاكتشاف محاولات التسلل.',
                            },
                            {
                                'title': 'المحاضرة الثانية: تحليل الثغرات الشائعة في تطبيقات الويب (OWASP Top 10)',
                                'video_url': 'https://www.youtube.com/watch?v=inWWhr5tnEA',
                                'duration': 2500,
                                'is_preview': False,
                                'content': 'دراسة حقن قواعد البيانات (SQLi) وهجمات تزوير الطلبات وكيفية منعها.',
                            },
                        ]
                    }
                ]
            },
            {
                'title': 'القيادة الاستراتيجية وإدارة المشروعات والتحول الرقمي',
                'instructor': instructors['dr_fatima@ertiqa.edu'],
                'category': categories['إدارة الأعمال والقيادة التنفيذية'],
                'price': 140.00,
                'discount_price': 85.00,
                'level': 'intermediate',
                'language': 'العربية',
                'status': 'published',
                'is_featured': False,
                'preview_video': 'https://www.youtube.com/watch?v=8aGhZQkoFbQ',
                'description': (
                    'برنامج تنفيذي صُمم لإعداد قادة ومديري المشروعات المعاصرة، متبنياً أحدث منهجيات الرشاقة المؤسسية (Agile/Scrum) '
                    'وحوكمة التغيير الرقمي وصنع القرارات المبنية على البيانات.'
                ),
                'sections': [
                    {
                        'title': 'الباب الأول: منهجيات الرشاقة وإدارة أصحاب المصلحة',
                        'order': 1,
                        'lessons': [
                            {
                                'title': 'المحاضرة الأولى: فلسفة الـ Agile وتأسيس فرق العمل عالية الأداء',
                                'video_url': 'https://www.youtube.com/watch?v=8aGhZQkoFbQ',
                                'duration': 2100,
                                'is_preview': True,
                                'content': 'تطبيق عملي لأدوار Product Owner و Scrum Master وإدارة سباقات العمل.',
                            },
                        ]
                    }
                ]
            },
            {
                'title': 'أساسيات البرمجة بلغة بايثون وتراكيب البيانات للباحثين',
                'instructor': instructors['dr_saadi@ertiqa.edu'],
                'category': categories['هندسة البرمجيات والنظم'],
                'price': 0.00,
                'discount_price': None,
                'level': 'beginner',
                'language': 'العربية',
                'status': 'published',
                'is_featured': True,
                'preview_video': 'https://www.youtube.com/watch?v=_uQrJ0TkZlc',
                'description': (
                    'مساق تمهيدي مجاني متاح لوجه الله لجميع طلاب العلم والباحثين، ينطلق من الصفر المطلق لتعليم أسس البرمجة الرصينة '
                    'وهياكل البيانات التأسيسية وحل المسائل المنطقية بلغة بايثون.'
                ),
                'sections': [
                    {
                        'title': 'الباب الأول: المدخل إلى بيئة العمل والمتغيرات والتحكم بالتدفق',
                        'order': 1,
                        'lessons': [
                            {
                                'title': 'المحاضرة الأولى: تنصيب البيئة وأول برنامج بايثوني',
                                'video_url': 'https://www.youtube.com/watch?v=_uQrJ0TkZlc',
                                'duration': 1500,
                                'is_preview': True,
                                'content': 'تثبيت بايثون وأداة VS Code وفهم كيفية ترجمة وتنفيذ الأكواد البرمجية.',
                            },
                            {
                                'title': 'المحاضرة الثانية: القوائم والقواميس والمجموعات (Data Structures)',
                                'video_url': 'https://www.youtube.com/watch?v=_uQrJ0TkZlc',
                                'duration': 1800,
                                'is_preview': True,
                                'content': 'إتقان التعامل مع هياكل التخزين واسترجاع البيانات بكفاءة.',
                            },
                        ]
                    }
                ]
            },
            {
                'title': 'تاريخ العلوم وفلسفة المنطق عند علماء الحضارة الإسلامية',
                'instructor': instructors['dr_bader@ertiqa.edu'],
                'category': categories['التراث العلمي وفلسفة المعرفة'],
                'price': 60.00,
                'discount_price': 40.00,
                'level': 'beginner',
                'language': 'العربية',
                'status': 'published',
                'is_featured': True,
                'preview_video': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
                'description': (
                    'رحلة معرفية أصيلة في تاريخ العلم التجريبي ونشأة المنهج العلمي، ومساهمات ابن الهيثم، الخوارزمي، البيروني، '
                    'وابن النفيس في صياغة الفكر العلمي الإنساني وتطور علوم الرياضيات والفلك والطب.'
                ),
                'sections': [
                    {
                        'title': 'الباب الأول: نشأة المنهج العلمي التجريبي وتأسيس علم المناظر',
                        'order': 1,
                        'lessons': [
                            {
                                'title': 'المحاضرة الأولى: الحسن بن الهيثم وميلاد منهج التجربة والبرهان',
                                'video_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
                                'duration': 2400,
                                'is_preview': True,
                                'content': 'دراسة نقدية لكتاب المناظر وكيف قلب ابن الهيثم نظريات الرؤية القديمة بالتجربة والرياضيات.',
                            },
                        ]
                    }
                ]
            },
        ]

        created_courses = []
        for cdata in courses_plan:
            course, created = Course.objects.get_or_create(
                title=cdata['title'],
                defaults={
                    'instructor': cdata['instructor'],
                    'category': cdata['category'],
                    'price': cdata['price'],
                    'discount_price': cdata['discount_price'],
                    'level': cdata['level'],
                    'language': cdata['language'],
                    'status': cdata['status'],
                    'is_featured': cdata['is_featured'],
                    'preview_video': cdata['preview_video'],
                    'description': cdata['description'],
                }
            )
            created_courses.append(course)

            # Sections and lessons
            for sdata in cdata['sections']:
                sec, _ = Section.objects.get_or_create(
                    course=course,
                    title=sdata['title'],
                    defaults={'order': sdata['order']}
                )
                for idx, ldata in enumerate(sdata['lessons'], 1):
                    lesson, _ = Lesson.objects.get_or_create(
                        section=sec,
                        title=ldata['title'],
                        defaults={
                            'video_url': ldata['video_url'],
                            'duration_seconds': ldata['duration'],
                            'is_preview': ldata['is_preview'],
                            'content': ldata['content'],
                            'order': idx,
                        }
                    )
                    if ldata.get('resource_title'):
                        Resource.objects.get_or_create(
                            lesson=lesson,
                            title=ldata['resource_title'],
                            defaults={'resource_type': 'pdf'}
                        )

            # Update instructor total courses
            inst_profile = cdata['instructor'].instructor_profile
            inst_profile.total_courses = Course.objects.filter(instructor=cdata['instructor']).count()
            inst_profile.save()

            self.stdout.write(f"  [+] Course: {course.id} - lessons: {course.total_lessons_count}")

        self.stdout.write(f"[OK] Successfully seeded {len(created_courses)} courses.")

        # -------------------------------------------------------------
        # 5. الاشتراكات، الإنجاز، والشهادات الأكاديمية (Enrollments & Certificates)
        # -------------------------------------------------------------
        # Enroll students with varying progress
        sample_course = created_courses[0]  # دبلوم هندسة البرمجيات
        python_course = created_courses[4]  # أساسيات بايثون
        ai_course = created_courses[1]      # الذكاء الاصطناعي

        for idx, student in enumerate(students):
            # Enroll in python_course: 100% completed with Certificate
            enr1, _ = Enrollment.objects.get_or_create(
                student=student,
                course=python_course,
                defaults={
                    'progress_percent': 100.0,
                    'is_completed': True,
                    'completed_at': timezone.now(),
                }
            )
            enr1.progress_percent = 100.0
            enr1.is_completed = True
            enr1.save()

            # Mark lessons completed
            for sec in python_course.sections.all():
                for l in sec.lessons.all():
                    LessonProgress.objects.get_or_create(
                        enrollment=enr1,
                        lesson=l,
                        defaults={'is_completed': True, 'watched_seconds': l.duration_seconds}
                    )

            # Certificate
            Certificate.objects.get_or_create(
                enrollment=enr1,
                defaults={
                    'certificate_id': uuid.uuid4(),
                    'issued_at': timezone.now(),
                }
            )

            # Enroll in other courses with progress
            if idx % 2 == 0:
                enr2, _ = Enrollment.objects.get_or_create(
                    student=student,
                    course=sample_course,
                    defaults={'progress_percent': 50.0, 'is_completed': False}
                )
            else:
                enr3, _ = Enrollment.objects.get_or_create(
                    student=student,
                    course=ai_course,
                    defaults={'progress_percent': 33.3, 'is_completed': False}
                )

        self.stdout.write("[OK] Successfully seeded enrollments and certificates.")

        # -------------------------------------------------------------
        # 6. التقييمات وشواهد الطلاب (Reviews & Testimonials)
        # -------------------------------------------------------------
        reviews_data = [
            {
                'course': python_course,
                'student': students[0],
                'rating': 5,
                'comment': 'بارك الله في فضيلة الدكتور عبد الرحمن، دورة تأسيسية جامعة وشرح رصين لم أجد مثله في أي منصة أخرى.',
            },
            {
                'course': python_course,
                'student': students[1],
                'rating': 5,
                'comment': 'منهج منظم يبني المفاهيم بدقة فائقة. أتممت المساق وحصلت على الشهادة الأكاديمية بكل فخر واعتزاز.',
            },
            {
                'course': sample_course,
                'student': students[0],
                'rating': 5,
                'comment': 'دبلوم هندسة النظم السحابية يرتقي بالمهندس إلى مصاف الكفاءات العالمية. المحتوى النظري والعملي شديد العمق.',
            },
            {
                'course': ai_course,
                'student': students[1],
                'rating': 5,
                'comment': 'الدكتورة سارة المنصور تقدم أصول الذكاء الاصطناعي برياضيات واضحة وتطبيقات تبهر العقول. جزاكم الله خيراً.',
            },
            {
                'course': sample_course,
                'student': students[2],
                'rating': 4,
                'comment': 'مساق متميز جداً وثري بالمعلومات، أنصح به كل من يرغب في احتراف بنية الخدمات المصغرة.',
            },
        ]

        for rdata in reviews_data:
            Review.objects.get_or_create(
                student=rdata['student'],
                course=rdata['course'],
                defaults={
                    'rating': rdata['rating'],
                    'comment': rdata['comment'],
                    'is_approved': True,
                }
            )

        # Update instructor student counts & ratings
        for inst in instructors.values():
            profile = inst.instructor_profile
            total_st = Enrollment.objects.filter(course__instructor=inst).values('student').distinct().count()
            profile.total_students = total_st
            profile.save()

        self.stdout.write("[OK] Successfully seeded student reviews and testimonials.")
        self.stdout.write("==================================================")
        self.stdout.write("  Ertiqa Academic Data Seeding Completed 100%!")
        self.stdout.write("==================================================")
