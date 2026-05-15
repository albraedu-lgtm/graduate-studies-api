from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *


class ProgramSerializer(serializers.ModelSerializer):
    enrolled_count = serializers.ReadOnlyField()
    class Meta:
        model = AcademicProgram
        fields = '__all__'


class EnrollmentSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    program_name = serializers.SerializerMethodField()
    program_type = serializers.SerializerMethodField()
    has_pending_approval = serializers.SerializerMethodField()

    class Meta:
        model = ProgramEnrollment
        fields = '__all__'
        read_only_fields = ['student', 'status', 'gpa', 'enrollment_date']

    def get_student_name(self, obj):
        return obj.student.get_full_name()
    def get_program_name(self, obj):
        return obj.program.name
    def get_program_type(self, obj):
        return obj.program.get_program_type_display()
    def get_has_pending_approval(self, obj):
        return ApprovalRequest.objects.filter(resource_type='ProgramEnrollment', resource_id=str(obj.id), status='pending').exists()


class ThesisSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()

    class Meta:
        model = Thesis
        fields = '__all__'
        read_only_fields = ['student', 'current_stage', 'is_published', 'created_at', 'updated_at', 'program_enrollment', 'thesis_type']

    def get_student_name(self, obj):
        return obj.student.get_full_name()


class SupervisionSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    supervisor_name = serializers.SerializerMethodField()
    thesis_title = serializers.SerializerMethodField()

    class Meta:
        model = SupervisionRelation
        fields = '__all__'
        read_only_fields = ['supervisor', 'status', 'start_date']

    def get_student_name(self, obj):
        return obj.thesis.student.get_full_name()
    def get_supervisor_name(self, obj):
        return obj.supervisor.get_full_name()
    def get_thesis_title(self, obj):
        return obj.thesis.title_ar


class SeminarSerializer(serializers.ModelSerializer):
    enrolled_count = serializers.ReadOnlyField()

    class Meta:
        model = Seminar
        fields = '__all__'


class ReportSerializer(serializers.ModelSerializer):
    submitted_by_name = serializers.SerializerMethodField()
    thesis_title = serializers.SerializerMethodField()

    class Meta:
        model = ProgressReport
        fields = '__all__'
        read_only_fields = ['submitted_by', 'status', 'supervisor_feedback', 'thesis']

    def get_submitted_by_name(self, obj):
        return obj.submitted_by.get_full_name()
    def get_thesis_title(self, obj):
        return obj.thesis.title_ar


class ApprovalSerializer(serializers.ModelSerializer):
    requested_by_name = serializers.SerializerMethodField()
    approved_by_name = serializers.SerializerMethodField()

    class Meta:
        model = ApprovalRequest
        fields = '__all__'

    def get_requested_by_name(self, obj):
        return obj.requested_by.get_full_name()
    def get_approved_by_name(self, obj):
        return obj.approved_by.get_full_name() if obj.approved_by else None

class ResourceSerializer(serializers.ModelSerializer):
    program_name = serializers.SerializerMethodField()

    class Meta:
        model = Resource
        fields = '__all__'

    def get_program_name(self, obj):
        return obj.program.name if obj.program else 'عام'

    def validate_file(self, value):
        if not value: return value
        allowed = ['.pdf', '.doc', '.docx', '.ppt', '.pptx', '.mp4']
        import os
        ext = os.path.splitext(value.name)[1].lower()
        if ext not in allowed:
            raise serializers.ValidationError('صيغة المورد غير مسموح بها.')
        return value

class StudentProfileSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = StudentProfile
        fields = '__all__'
        read_only_fields = ['user', 'gpa', 'graduation_year']

    def get_user_name(self, obj):
        return obj.user.get_full_name()

    def validate_cv_file(self, value):
        if not value: return value
        allowed = ['.pdf', '.doc', '.docx']
        import os
        ext = os.path.splitext(value.name)[1].lower()
        if ext not in allowed:
            raise serializers.ValidationError('صيغة السيرة الذاتية غير مسموح بها. المسموح: PDF, DOC, DOCX')
        return value

    def validate_profile_photo(self, value):
        if not value: return value
        allowed = ['.jpg', '.jpeg', '.png']
        import os
        ext = os.path.splitext(value.name)[1].lower()
        if ext not in allowed:
            raise serializers.ValidationError('صيغة الصورة غير مسموح بها.')
        return value

class SupervisorProfileSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    has_capacity = serializers.ReadOnlyField()
    current_students_count = serializers.ReadOnlyField()

    class Meta:
        model = SupervisorProfile
        fields = '__all__'
        read_only_fields = ['user', 'department', 'academic_rank', 'max_students']

    def get_user_name(self, obj):
        return obj.user.get_full_name()

    def validate_profile_photo(self, value):
        if not value: return value
        allowed = ['.jpg', '.jpeg', '.png']
        import os
        ext = os.path.splitext(value.name)[1].lower()
        if ext not in allowed:
            raise serializers.ValidationError('صيغة الصورة غير مسموح بها.')
        return value

class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = '__all__'

class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = '__all__'
        read_only_fields = ['thesis']
    
    def validate_file(self, value):
        allowed_extensions = ['.pdf', '.doc', '.docx', '.png', '.jpg', '.jpeg']
        import os
        ext = os.path.splitext(value.name)[1].lower()
        if ext not in allowed_extensions:
            raise serializers.ValidationError('صيغة الملف غير مسموح بها. المسموح فقط: PDF, DOCX, PNG, JPG')
        return value

class ThesisStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThesisStage
        fields = '__all__'

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__'
        read_only_fields = ['user']

class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = '__all__'

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ['user']

class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()
    is_mine = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ['author', 'thesis']

    def get_author_name(self, obj):
        return obj.author.get_full_name() if obj.author else 'Unknown'
    
    def get_is_mine(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return obj.author == request.user
        return False

class StudyPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudyPlan
        fields = '__all__'
