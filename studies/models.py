from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class SoftDeleteQuerySet(models.QuerySet):
    def delete(self):
        return self.update(is_deleted=True, deleted_at=timezone.now())

    def alive(self):
        return self.filter(is_deleted=False)

class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).alive()

class SoftDeleteMixin(models.Model):
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_deleted', 'deleted_at'])

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=['is_deleted', 'deleted_at'])



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


class Thesis(SoftDeleteMixin, models.Model):
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


class ProgressReport(SoftDeleteMixin, models.Model):
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


class ApprovalRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'قيد الانتظار'),
        ('approved', 'تمت الموافقة'),
        ('rejected', 'مرفوض'),
    ]
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_approvals')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='received_approvals')
    resource_type = models.CharField(max_length=50)
    resource_id = models.CharField(max_length=100)
    action_type = models.CharField(max_length=50)
    old_data = models.JSONField(null=True, blank=True)
    new_data = models.JSONField()
    reason = models.TextField()
    admin_notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Request: {self.action_type} by {self.requested_by}"

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new:
            try:
                from .utils import notify_admins
                notify_admins(
                    title=f"طلب موافقة جديد: {self.action_type}",
                    message=f"قام {self.requested_by.get_full_name()} بطلب {self.action_type}. يرجى المراجعة.",
                    link="/approvals"
                )
            except Exception:
                pass

class Resource(models.Model):
    TYPES = [('lecture', 'محاضرة'), ('book', 'كتاب'), ('slides', 'شرائح'), ('other', 'أخرى')]
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    resource_type = models.CharField(max_length=20, choices=TYPES, default='other')
    program = models.ForeignKey(AcademicProgram, on_delete=models.SET_NULL, null=True, blank=True)
    file = models.FileField(upload_to='resources/', null=True, blank=True)
    external_url = models.URLField(blank=True)
    download_count = models.PositiveIntegerField(default=0)
    week_number = models.PositiveIntegerField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    nationality = models.CharField(max_length=100, blank=True)
    national_id = models.CharField(max_length=50, blank=True)
    previous_university = models.CharField(max_length=200, blank=True)
    previous_degree = models.CharField(max_length=100, blank=True)
    graduation_year = models.PositiveIntegerField(null=True, blank=True)
    gpa = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    research_interests = models.TextField(blank=True)
    bio = models.TextField(blank=True)
    profile_photo = models.ImageField(upload_to='profiles/students/', null=True, blank=True)
    cv_file = models.FileField(upload_to='cvs/', null=True, blank=True)

    def __str__(self):
        return self.user.get_full_name()


class SupervisorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='supervisor_profile')
    department = models.CharField(max_length=200)
    specialization = models.CharField(max_length=200)
    academic_rank = models.CharField(max_length=100)
    max_students = models.PositiveIntegerField(default=5)
    bio = models.TextField(blank=True)
    profile_photo = models.ImageField(upload_to='profiles/supervisors/', null=True, blank=True)

    @property
    def current_students_count(self):
        return self.user.supervised_theses.filter(status='active').count()

    @property
    def has_capacity(self):
        return self.current_students_count < self.max_students

    def __str__(self):
        return self.user.get_full_name()

import uuid

class Certificate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    program = models.ForeignKey(AcademicProgram, on_delete=models.CASCADE)
    issue_date = models.DateField(auto_now_add=True)
    certificate_type = models.CharField(max_length=50, default='graduation')
    file = models.FileField(upload_to='certificates/', null=True, blank=True)

    def __str__(self):
        return f"Certificate for {self.student.get_full_name()}"

class Attachment(SoftDeleteMixin, models.Model):
    thesis = models.ForeignKey('Thesis', on_delete=models.CASCADE, related_name='attachments', null=True, blank=True)
    title = models.CharField(max_length=200)
    attachment_type = models.CharField(max_length=50)
    file = models.FileField(upload_to='attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class ThesisStage(models.Model):
    thesis = models.ForeignKey('Thesis', on_delete=models.CASCADE, related_name='stage_history')
    stage = models.CharField(max_length=50)
    status = models.CharField(max_length=50, default='pending')
    description = models.TextField(blank=True)
    supervisor_notes = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=200)
    details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class Comment(models.Model):
    thesis = models.ForeignKey('Thesis', on_delete=models.CASCADE, related_name='comments', null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class StudyPlan(models.Model):
    program = models.ForeignKey(AcademicProgram, on_delete=models.CASCADE, related_name='study_plans')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

