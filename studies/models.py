from django.db import models
from django.contrib.auth.models import User


class AcademicProgram(models.Model):
    TYPES = [('master', 'ماجستير'), ('phd', 'دكتوراه'), ('diploma', 'دبلوم')]
    name = models.CharField(max_length=255)
    name_en = models.CharField(max_length=255, blank=True)
    program_type = models.CharField(max_length=20, choices=TYPES, default='master')
    department = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    duration_years = models.PositiveIntegerField(default=2)
    credit_hours = models.PositiveIntegerField(default=36)
    max_students = models.PositiveIntegerField(default=30)
    status = models.CharField(max_length=20, default='active')
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def enrolled_count(self):
        return self.enrollments.filter(status='active').count()


class ProgramEnrollment(models.Model):
    STATUSES = [('pending', 'معلق'), ('active', 'نشط'), ('on_leave', 'إجازة'),
                ('graduated', 'متخرج'), ('withdrawn', 'منسحب'), ('suspended', 'موقوف')]
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    program = models.ForeignKey(AcademicProgram, on_delete=models.CASCADE, related_name='enrollments')
    student_id_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=STATUSES, default='pending')
    enrollment_date = models.DateField(auto_now_add=True)
    expected_graduation = models.DateField(null=True, blank=True)
    gpa = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.program.name}"


class Thesis(models.Model):
    STAGES = [('proposal', 'مقترح'), ('literature_review', 'مراجعة أدبيات'),
              ('methodology', 'منهجية'), ('data_collection', 'جمع بيانات'),
              ('analysis', 'تحليل'), ('writing', 'كتابة'), ('final_submission', 'تقديم نهائي'),
              ('approved', 'معتمد')]
    TYPES = [('master', 'ماجستير'), ('phd', 'دكتوراه')]
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='theses')
    program_enrollment = models.ForeignKey(ProgramEnrollment, on_delete=models.SET_NULL, null=True, blank=True)
    title_ar = models.CharField(max_length=500)
    title_en = models.CharField(max_length=500, blank=True)
    thesis_type = models.CharField(max_length=20, choices=TYPES, default='master')
    current_stage = models.CharField(max_length=30, choices=STAGES, default='proposal')
    abstract_ar = models.TextField(blank=True)
    keywords = models.CharField(max_length=500, blank=True)
    field_of_study = models.CharField(max_length=200, blank=True)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title_ar


class SupervisionRelation(models.Model):
    ROLES = [('main', 'رئيسي'), ('co', 'مشارك')]
    STATUSES = [('pending', 'معلق'), ('active', 'نشط'), ('completed', 'مكتمل'), ('withdrawn', 'منسحب')]
    supervisor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='supervised_theses')
    thesis = models.ForeignKey(Thesis, on_delete=models.CASCADE, related_name='supervision_relations')
    role = models.CharField(max_length=10, choices=ROLES, default='main')
    status = models.CharField(max_length=20, choices=STATUSES, default='pending')
    start_date = models.DateField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.supervisor.get_full_name()} → {self.thesis.title_ar[:50]}"


class Seminar(models.Model):
    TYPES = [('seminar', 'ندوة'), ('workshop', 'ورشة'), ('lecture', 'محاضرة'), ('webinar', 'عن بعد')]
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    speaker_name = models.CharField(max_length=200)
    date = models.DateTimeField()
    location = models.CharField(max_length=300, blank=True)
    meeting_link = models.URLField(blank=True)
    seminar_type = models.CharField(max_length=20, choices=TYPES, default='seminar')
    max_participants = models.PositiveIntegerField(default=50)
    status = models.CharField(max_length=20, default='scheduled')
    is_online = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    @property
    def enrolled_count(self):
        return self.registrations.count()


class SeminarRegistration(models.Model):
    seminar = models.ForeignKey(Seminar, on_delete=models.CASCADE, related_name='registrations')
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['seminar', 'student']


class ProgressReport(models.Model):
    STATUSES = [('submitted', 'مقدم'), ('approved', 'معتمد'), ('revision', 'يحتاج مراجعة')]
    thesis = models.ForeignKey(Thesis, on_delete=models.CASCADE, related_name='reports')
    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    report_date = models.DateField(auto_now_add=True)
    progress_percentage = models.PositiveIntegerField(default=0)
    summary = models.TextField()
    achievements = models.TextField(blank=True)
    challenges = models.TextField(blank=True)
    next_steps = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUSES, default='submitted')
    supervisor_feedback = models.TextField(blank=True)

    def __str__(self):
        return f"Report: {self.thesis.title_ar[:40]} ({self.report_date})"
