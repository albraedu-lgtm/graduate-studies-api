from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .models import *
from .serializers import *


class ProgramViewSet(viewsets.ModelViewSet):
    queryset = AcademicProgram.objects.all()
    serializer_class = ProgramSerializer
    filterset_fields = ['program_type', 'status']
    search_fields = ['name', 'name_en']


class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = ProgramEnrollment.objects.select_related('student', 'program').all()
    serializer_class = EnrollmentSerializer
    filterset_fields = ['status', 'program']

    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        enrollment = self.get_object()
        new_status = request.data.get('status')
        if new_status:
            enrollment.status = new_status
            enrollment.save()
        return Response(EnrollmentSerializer(enrollment).data)


class ThesisViewSet(viewsets.ModelViewSet):
    queryset = Thesis.objects.all()
    serializer_class = ThesisSerializer
    filterset_fields = ['current_stage', 'thesis_type', 'is_published']
    search_fields = ['title_ar', 'title_en', 'keywords']

    def perform_create(self, serializer):
        serializer.save(student=self.request.user if self.request.user.is_authenticated else User.objects.first())

    @action(detail=True, methods=['post'])
    def advance_stage(self, request, pk=None):
        thesis = self.get_object()
        stages = ['proposal', 'literature_review', 'methodology', 'data_collection', 'analysis', 'writing', 'final_submission', 'approved']
        idx = stages.index(thesis.current_stage) if thesis.current_stage in stages else 0
        if idx < len(stages) - 1:
            thesis.current_stage = stages[idx + 1]
            thesis.save()
        return Response({'current_stage': thesis.current_stage})

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        thesis = self.get_object()
        thesis.is_published = True
        thesis.save()
        return Response({'message': 'تم النشر'})

    @action(detail=False, methods=['get'])
    def archive(self, request):
        theses = self.queryset.filter(is_published=True)
        return Response(ThesisSerializer(theses, many=True).data)


class SupervisionViewSet(viewsets.ModelViewSet):
    queryset = SupervisionRelation.objects.select_related('supervisor', 'thesis__student').all()
    serializer_class = SupervisionSerializer
    filterset_fields = ['status', 'role']

    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        obj = self.get_object()
        obj.status = request.data.get('status', obj.status)
        obj.save()
        return Response(SupervisionSerializer(obj).data)


class SeminarViewSet(viewsets.ModelViewSet):
    queryset = Seminar.objects.all()
    serializer_class = SeminarSerializer
    filterset_fields = ['seminar_type', 'status']

    @action(detail=True, methods=['post'])
    def register(self, request, pk=None):
        seminar = self.get_object()
        user = request.user if request.user.is_authenticated else User.objects.first()
        SeminarRegistration.objects.get_or_create(seminar=seminar, student=user)
        return Response({'message': 'تم التسجيل', 'enrolled_count': seminar.enrolled_count})

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        from django.utils import timezone
        seminars = self.queryset.filter(date__gte=timezone.now())
        return Response(SeminarSerializer(seminars, many=True).data)


class ReportViewSet(viewsets.ModelViewSet):
    queryset = ProgressReport.objects.select_related('thesis', 'submitted_by').all()
    serializer_class = ReportSerializer
    filterset_fields = ['status', 'thesis']

    def perform_create(self, serializer):
        serializer.save(submitted_by=self.request.user if self.request.user.is_authenticated else User.objects.first())

    @action(detail=True, methods=['patch'])
    def approve(self, request, pk=None):
        report = self.get_object()
        report.status = 'approved'
        report.supervisor_feedback = request.data.get('feedback', '')
        report.save()
        return Response(ReportSerializer(report).data)


class DashboardView(APIView):
    def get(self, request):
        return Response({
            'summary': {
                'total_programs': AcademicProgram.objects.count(),
                'active_programs': AcademicProgram.objects.filter(status='active').count(),
                'total_students': ProgramEnrollment.objects.filter(status='active').count(),
                'total_supervisors': SupervisionRelation.objects.values('supervisor').distinct().count(),
                'total_theses': Thesis.objects.count(),
                'upcoming_seminars': Seminar.objects.filter(status='scheduled').count(),
                'pending_reports': ProgressReport.objects.filter(status='submitted').count(),
                'theses_by_stage': {s[0]: Thesis.objects.filter(current_stage=s[0]).count() for s in Thesis.STAGES},
            },
            'programs_overview': [
                {'name': p.name, 'type': p.get_program_type_display(), 'enrolled': p.enrolled_count, 'capacity': p.max_students}
                for p in AcademicProgram.objects.filter(status='active')
            ]
        })


class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email', '')
        password = request.data.get('password', '')
        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(username=user_obj.username, password=password)
        except User.DoesNotExist:
            user = None
        if user:
            groups = list(user.groups.values_list('name', flat=True))
            return Response({
                'token': 'real-jwt-token',
                'user': {
                    'id': user.id, 'username': user.username, 'email': user.email,
                    'first_name': user.first_name, 'last_name': user.last_name,
                    'full_name': user.get_full_name(), 'is_staff': user.is_staff,
                    'groups': groups,
                }
            })
        return Response({'detail': 'بيانات الدخول غير صحيحة'}, status=401)


class UserInfoView(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            return Response({'id': request.user.id, 'email': request.user.email, 'name': request.user.get_full_name()})
        return Response({'detail': 'غير مصرح'}, status=401)
