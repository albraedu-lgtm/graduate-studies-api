"""
Seed script - يملأ قاعدة البيانات ببيانات تجريبية
Run: python manage.py seed_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from studies.models import *
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Seed database with demo data'

    def handle(self, *args, **options):
        # Groups
        admin_group, _ = Group.objects.get_or_create(name='GraduateAdmin')
        supervisor_group, _ = Group.objects.get_or_create(name='AcademicSupervisor')
        student_group, _ = Group.objects.get_or_create(name='GraduateStudent')

        # Users
        admin = User.objects.create_user('admin', 'admin@marketplace.com', 'admin123',
                                          first_name='مدير', last_name='النظام', is_staff=True, is_superuser=True)
        admin.groups.add(admin_group)

        supervisor = User.objects.create_user('dr_ahmed', 'supervisor@learnnov.com', 'admin123',
                                              first_name='أحمد', last_name='محمد علي')
        supervisor_group.user_set.add(supervisor)

        student1 = User.objects.create_user('student1', 'student@learnnov.com', 'admin123',
                                            first_name='محمد', last_name='عبدالله')
        student_group.user_set.add(student1)

        student2 = User.objects.create_user('student2', 'fatima@learnnov.com', 'admin123',
                                            first_name='فاطمة', last_name='أحمد')
        student2.groups.add(student_group)

        # Programs
        p1 = AcademicProgram.objects.create(name='ماجستير علوم الحاسوب', name_en='MSc Computer Science',
                                             program_type='master', department='علوم الحاسوب', max_students=30, credit_hours=36)
        p2 = AcademicProgram.objects.create(name='دكتوراه هندسة البرمجيات', name_en='PhD Software Engineering',
                                             program_type='phd', department='هندسة البرمجيات', max_students=15, credit_hours=54)
        p3 = AcademicProgram.objects.create(name='ماجستير نظم المعلومات', name_en='MSc Information Systems',
                                             program_type='master', department='نظم المعلومات', max_students=25, credit_hours=33)
        p4 = AcademicProgram.objects.create(name='ماجستير الأمن السيبراني', name_en='MSc Cybersecurity',
                                             program_type='master', department='أمن المعلومات', max_students=20, credit_hours=36)

        # Enrollments
        e1 = ProgramEnrollment.objects.create(student=student1, program=p1, student_id_number='GRAD-2025-001', status='active', gpa=3.75)
        e2 = ProgramEnrollment.objects.create(student=student2, program=p4, student_id_number='GRAD-2025-002', status='active', gpa=3.90)

        # Theses
        t1 = Thesis.objects.create(student=student1, program_enrollment=e1, title_ar='تطبيق تقنيات التعلم العميق في تحليل الصور الطبية',
                                    title_en='Deep Learning for Medical Image Analysis', thesis_type='master',
                                    current_stage='writing', field_of_study='علوم الحاسوب',
                                    abstract_ar='يهدف هذا البحث إلى تطوير نماذج تعلم عميق لتحليل الصور الطبية',
                                    keywords='تعلم عميق، صور طبية، ذكاء اصطناعي')
        t2 = Thesis.objects.create(student=student2, program_enrollment=e2, title_ar='إطار عمل لتأمين إنترنت الأشياء باستخدام البلوك تشين',
                                    title_en='IoT Security Framework using Blockchain', thesis_type='master',
                                    current_stage='methodology', field_of_study='الأمن السيبراني',
                                    keywords='إنترنت الأشياء، بلوك تشين، أمن سيبراني')

        # Supervision
        SupervisionRelation.objects.create(supervisor=supervisor, thesis=t1, role='main', status='active')
        SupervisionRelation.objects.create(supervisor=supervisor, thesis=t2, role='main', status='active')

        # Seminars
        Seminar.objects.create(title='مقدمة في التعلم العميق وتطبيقاته', speaker_name='د. أحمد محمد علي',
                                date=timezone.now() + timedelta(days=7), location='القاعة الرئيسية',
                                seminar_type='workshop', max_participants=50)
        Seminar.objects.create(title='منهجيات البحث العلمي المتقدمة', speaker_name='أ.د. سارة إبراهيم',
                                date=timezone.now() + timedelta(days=14), location='معمل الحاسوب',
                                seminar_type='seminar', max_participants=30)

        # Reports
        ProgressReport.objects.create(thesis=t1, submitted_by=student1, progress_percentage=65,
                                       summary='تم تدريب النموذج الأولي بدقة 92%', status='approved')

        # Approvals (New System)
        ApprovalRequest.objects.create(
            requested_by=supervisor,
            resource_type='ProgramEnrollment',
            resource_id=str(e1.id),
            action_type='status_change_to_graduated',
            old_data={'status': e1.status},
            new_data={'status': 'graduated'},
            reason='إكمال جميع متطلبات التخرج بنجاح ومناقشة الرسالة.',
            status='pending'
        )
        ApprovalRequest.objects.create(
            requested_by=admin,
            resource_type='ProgramEnrollment',
            resource_id=str(e2.id),
            action_type='gpa_override',
            old_data={'gpa': float(e2.gpa)},
            new_data={'gpa': 4.00},
            reason='تصحيح خطأ في رصد الدرجة النهائية لمادة البحث.',
            status='pending'
        )

        self.stdout.write(self.style.SUCCESS('✅ Database seeded successfully!'))
