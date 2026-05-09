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

    class Meta:
        model = ProgramEnrollment
        fields = '__all__'

    def get_student_name(self, obj):
        return obj.student.get_full_name()
    def get_program_name(self, obj):
        return obj.program.name
    def get_program_type(self, obj):
        return obj.program.get_program_type_display()


class ThesisSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()

    class Meta:
        model = Thesis
        fields = '__all__'
        read_only_fields = ['student', 'created_at', 'updated_at']

    def get_student_name(self, obj):
        return obj.student.get_full_name()


class SupervisionSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    supervisor_name = serializers.SerializerMethodField()
    thesis_title = serializers.SerializerMethodField()

    class Meta:
        model = SupervisionRelation
        fields = '__all__'

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
        read_only_fields = ['submitted_by']

    def get_submitted_by_name(self, obj):
        return obj.submitted_by.get_full_name()
    def get_thesis_title(self, obj):
        return obj.thesis.title_ar
