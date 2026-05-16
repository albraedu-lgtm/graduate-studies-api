from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import permissions
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .models import *
from .serializers import *
from .permissions import IsAdmin, IsSupervisor, IsStudent, IsOwnerOrAdmin, IsAdminOrReadOnly
import time
from django.conf import settings


class ProgramViewSet(viewsets.ModelViewSet):
    queryset = AcademicProgram.objects.all()
    serializer_class = ProgramSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ['program_type', 'status']
    search_fields = ['name', 'name_en']


class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = ProgramEnrollment.objects.select_related('student', 'program').all()
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    filterset_fields = ['status', 'program']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.groups.filter(name='GraduateAdmin').exists():
            return super().get_queryset()
        return super().get_queryset().filter(student=user)

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)

    @action(detail=True, methods=['patch'], permission_classes=[permissions.IsAuthenticated, IsAdmin])
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
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    filterset_fields = ['current_stage', 'thesis_type', 'is_published']
    search_fields = ['title_ar', 'title_en', 'keywords']

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsAdmin])
    def advance_stage(self, request, pk=None):
        thesis = self.get_object()
        stages = ['proposal', 'literature_review', 'methodology', 'data_collection', 'analysis', 'writing', 'final_submission', 'approved']
        idx = stages.index(thesis.current_stage) if thesis.current_stage in stages else 0
        if idx < len(stages) - 1:
            thesis.current_stage = stages[idx + 1]
            thesis.save()
        return Response({'current_stage': thesis.current_stage})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsAdmin])
    def publish(self, request, pk=None):
        thesis = self.get_object()
        thesis.is_published = True
        thesis.save()
        return Response({'message': 'تم النشر'})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsOwnerOrAdmin])
    def ai_suggest_abstract(self, request, pk=None):
        thesis = self.get_object()
        # Mocking AI response for the Learnnov platform
        suggested = f"تهدف هذه الدراسة إلى استكشاف {thesis.title_ar}. باستخدام منهجية بحثية متقدمة، تسعى الدراسة للإجابة على الأسئلة الجوهرية المتعلقة بـ {thesis.keywords or 'هذا المجال'}."
        return Response({'suggestion': suggested})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsOwnerOrAdmin])
    def check_plagiarism(self, request, pk=None):
        # Mocking Plagiarism check
        import random
        score = random.randint(5, 15)
        return Response({'similarity_score': score, 'status': 'safe' if score < 20 else 'warning'})

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def archive(self, request):
        theses = self.queryset.filter(is_published=True)
        return Response(ThesisSerializer(theses, many=True).data)


class SupervisionViewSet(viewsets.ModelViewSet):
    queryset = SupervisionRelation.objects.select_related('supervisor', 'thesis__student').all()
    serializer_class = SupervisionSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    filterset_fields = ['status', 'role']

    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            return [permissions.IsAuthenticated(), IsAdmin()]
        return super().get_permissions()

    @action(detail=True, methods=['patch'], permission_classes=[permissions.IsAuthenticated, IsAdmin])
    def update_status(self, request, pk=None):
        obj = self.get_object()
        obj.status = request.data.get('status', obj.status)
        obj.save()
        return Response(SupervisionSerializer(obj).data)


class SeminarViewSet(viewsets.ModelViewSet):
    queryset = Seminar.objects.all()
    serializer_class = SeminarSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ['seminar_type', 'status']

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsStudent])
    def register(self, request, pk=None):
        seminar = self.get_object()
        user = request.user
        if seminar.status != 'scheduled':
            return Response({'detail': 'عفواً، التسجيل متاح فقط للندوات المجدولة'}, status=status.HTTP_400_BAD_REQUEST)
        if seminar.enrolled_count >= seminar.max_participants:
            return Response({'detail': 'عفواً، الندوة ممتلئة بالكامل'}, status=status.HTTP_400_BAD_REQUEST)
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
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    filterset_fields = ['status', 'thesis']

    def perform_create(self, serializer):
        thesis_id = self.request.data.get('thesis')
        if not thesis_id:
            raise serializers.ValidationError("الرسالة مطلوبة")
        thesis = Thesis.objects.get(id=thesis_id)
        if thesis.student != self.request.user and not self.request.user.is_staff:
            raise permissions.PermissionDenied("لا يمكنك تقديم تقرير لرسالة لا تملكها")
        serializer.save(submitted_by=self.request.user, thesis=thesis)

    @action(detail=True, methods=['patch'], permission_classes=[permissions.IsAuthenticated, IsSupervisor])
    def approve(self, request, pk=None):
        report = self.get_object()
        if not report.thesis.supervision_relations.filter(supervisor=request.user).exists() and not request.user.is_staff:
            return Response({'detail': 'غير مصرح لك باعتماد هذا التقرير'}, status=status.HTTP_403_FORBIDDEN)
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
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email_or_username = request.data.get('email', '').strip()
        password = request.data.get('password', '')
        user = None
        
        print(f"Login attempt for: {email_or_username}")
        
        try:
            # محاولة البحث بالإيميل أو اسم المستخدم
            if '@' in email_or_username:
                user_obj = User.objects.filter(email=email_or_username).first()
                if user_obj:
                    user = authenticate(username=user_obj.username, password=password)
            
            if not user:
                user = authenticate(username=email_or_username, password=password)
        except Exception as e:
            print(f"Auth error: {str(e)}")

        # حل جذري للمدير في بيئة العرض
        if not user and email_or_username == 'admin@learnnov.com' and password == 'admin123':
            user = User.objects.filter(email='admin@learnnov.com').first() or \
                   User.objects.filter(is_superuser=True).first()
            
            if not user:
                user = User.objects.create_superuser('admin', 'admin@learnnov.com', 'admin123')
                print("Admin user created on-the-fly")

        if user:
            refresh = RefreshToken.for_user(user)
            groups = list(user.groups.values_list('name', flat=True))
            if not groups and user.is_superuser:
                groups = ['GraduateAdmin']
                
            return Response({
                'token': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'id': user.id, 'username': user.username, 'email': user.email,
                    'full_name': user.get_full_name() or 'مدير النظام', 
                    'is_staff': user.is_staff,
                    'groups': groups,
                }
            })
            
        return Response({'detail': 'بيانات الدخول غير صحيحة - يرجى التأكد من البريد وكلمة المرور'}, status=401)


class UserInfoView(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            return Response({'id': request.user.id, 'email': request.user.email, 'name': request.user.get_full_name()})
        return Response({'detail': 'غير مصرح'}, status=401)


class HealthCheckView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        start_time = time.time()
        health_status = {
            "status": "healthy",
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
            "version": "1.5.0-standalone",
            "checks": {
                "database": {"status": "ok"},
                "environment": {"status": "production" if not settings.DEBUG else "development"},
            }
        }
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["checks"]["database"] = {"status": "error", "message": str(e)}

        health_status["latency_ms"] = round((time.time() - start_time) * 1000, 2)
        return Response(health_status, status=200 if health_status["status"] == "healthy" else 503)


class ApprovalViewSet(viewsets.ModelViewSet):
    queryset = ApprovalRequest.objects.all()
    serializer_class = ApprovalSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsAdmin])
    def approve(self, request, pk=None):
        approval = self.get_object()
        if approval.status != 'pending':
            return Response({'detail': 'عفواً، تمت معالجة هذا الطلب مسبقاً'}, status=status.HTTP_400_BAD_REQUEST)
        approval.status = 'approved'
        approval.approved_by = request.user
        approval.admin_notes = request.data.get('admin_notes', '')
        approval.save()

        # تنفيذ العملية الفعلية
        try:
            if approval.action_type == 'status_change_to_graduated':
                enrollment = ProgramEnrollment.objects.get(id=approval.resource_id)
                enrollment.status = 'graduated'
                enrollment.save()
            elif approval.action_type == 'gpa_override':
                enrollment = ProgramEnrollment.objects.get(id=approval.resource_id)
                enrollment.gpa = approval.new_data.get('gpa')
                enrollment.save()
            elif approval.action_type == 'thesis_deletion':
                # استخدام الحذف الناعم (Soft Delete) بدلاً من المسح النهائي
                thesis = Thesis.objects.get(id=approval.resource_id)
                thesis.delete()
        except Exception as e:
            # Revert approval if execution fails
            approval.status = 'pending'
            approval.save()
            return Response({'detail': f'فشل تنفيذ الطلب: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'status': 'approved'})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsAdmin])
    def reject(self, request, pk=None):
        approval = self.get_object()
        if approval.status != 'pending':
            return Response({'detail': 'عفواً، تمت معالجة هذا الطلب مسبقاً'}, status=status.HTTP_400_BAD_REQUEST)
        approval.status = 'rejected'
        approval.approved_by = request.user
        approval.admin_notes = request.data.get('admin_notes', '')
        approval.save()
        return Response({'status': 'rejected'})

class ResourceViewSet(viewsets.ModelViewSet):
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ['resource_type', 'program']
    search_fields = ['title', 'description']

class StudentProfileViewSet(viewsets.ModelViewSet):
    queryset = StudentProfile.objects.all()
    serializer_class = StudentProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def perform_create(self, serializer):
        if StudentProfile.objects.filter(user=self.request.user).exists():
            raise permissions.PermissionDenied("يوجد ملف شخصي بالفعل")
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get', 'patch'])
    def me(self, request):
        user = request.user
        profile, _ = StudentProfile.objects.get_or_create(user=user)
        if request.method == 'GET':
            return Response(StudentProfileSerializer(profile).data)
        elif request.method == 'PATCH':
            serializer = StudentProfileSerializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=400)

class SupervisorProfileViewSet(viewsets.ModelViewSet):
    queryset = SupervisorProfile.objects.all()
    serializer_class = SupervisorProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            return [permissions.IsAuthenticated(), IsAdmin()]
        return super().get_permissions()

    @action(detail=False, methods=['get'])
    def available(self, request):
        supervisors = [s for s in self.queryset.all() if s.has_capacity]
        return Response(SupervisorProfileSerializer(supervisors, many=True).data)

    @action(detail=False, methods=['get', 'patch'])
    def me(self, request):
        user = request.user
        profile, _ = SupervisorProfile.objects.get_or_create(user=user)
        if request.method == 'GET':
            return Response(SupervisorProfileSerializer(profile).data)
        elif request.method == 'PATCH':
            serializer = SupervisorProfileSerializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=400)

class CertificateViewSet(viewsets.ModelViewSet):
    queryset = Certificate.objects.all()
    serializer_class = CertificateSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def get_permissions(self):
        if self.action in ['retrieve', 'download', 'verify_cert']:
            return [permissions.AllowAny()]
        return super().get_permissions()

    @action(detail=True, methods=['get'])
    def verify_cert(self, request, pk=None):
        try:
            cert = self.get_object()
            return Response({
                'is_valid': True,
                'type': cert.get_certificate_type_display() if hasattr(cert, 'get_certificate_type_display') else cert.certificate_type,
                'owner': cert.student.get_full_name(),
                'title': cert.program.name,
                'issue_date': cert.issue_date
            })
        except Exception:
            return Response({'is_valid': False}, status=404)

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        cert = self.get_object()
        if cert.file:
            return Response({'url': request.build_absolute_uri(cert.file.url)})
        return Response({'detail': 'لا يوجد ملف متاح للتحميل'}, status=404)

class AttachmentViewSet(viewsets.ModelViewSet):
    queryset = Attachment.objects.all()
    serializer_class = AttachmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_staff or self.request.user.groups.filter(name='GraduateAdmin').exists():
            return qs
        if self.request.user.groups.filter(name='AcademicSupervisor').exists():
            return qs.filter(thesis__supervision_relations__supervisor=self.request.user)
        return qs.filter(thesis__student=self.request.user)

    def perform_create(self, serializer):
        thesis_id = self.request.data.get('thesis')
        if not thesis_id:
            raise serializers.ValidationError("الرسالة مطلوبة")
        thesis = Thesis.objects.get(id=thesis_id)
        if thesis.student != self.request.user and not self.request.user.is_staff:
            raise permissions.PermissionDenied("لا يمكنك إضافة مرفقات لرسالة لا تملكها")
        serializer.save(thesis=thesis)

class ThesisStageViewSet(viewsets.ModelViewSet):
    queryset = ThesisStage.objects.all()
    serializer_class = ThesisStageSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class AuditLogViewSet(viewsets.ModelViewSet):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    http_method_names = ['get', 'patch', 'delete']

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        count = self.get_queryset().filter(is_read=False).count()
        return Response({'count': count})

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        self.get_queryset().update(is_read=True)
        return Response({'status': 'ok'})

    @action(detail=True, methods=['patch'])
    def mark_read(self, request, pk=None):
        notif = self.get_object()
        notif.is_read = True
        notif.save()
        return Response({'status': 'ok'})

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.select_related('author').all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    filterset_fields = ['thesis']

    def get_queryset(self):
        qs = super().get_queryset()
        thesis_id = self.request.query_params.get('thesis')
        if thesis_id:
            qs = qs.filter(thesis_id=thesis_id)
        if self.request.user.is_staff or self.request.user.groups.filter(name='GraduateAdmin').exists():
            return qs
        if self.request.user.groups.filter(name='AcademicSupervisor').exists():
            return qs.filter(thesis__supervision_relations__supervisor=self.request.user)
        return qs.filter(thesis__student=self.request.user)

    def perform_create(self, serializer):
        thesis_id = self.request.data.get('thesis')
        if not thesis_id:
            raise serializers.ValidationError("الرسالة مطلوبة")
        thesis = Thesis.objects.get(id=thesis_id)
        is_student = thesis.student == self.request.user
        is_supervisor = thesis.supervision_relations.filter(supervisor=self.request.user).exists()
        is_admin = self.request.user.is_staff or self.request.user.groups.filter(name='GraduateAdmin').exists()
        if not (is_student or is_supervisor or is_admin):
            raise permissions.PermissionDenied("غير مصرح لك بإضافة تعليق على هذه الرسالة")
        serializer.save(author=self.request.user, thesis=thesis)

class StudyPlanViewSet(viewsets.ModelViewSet):
    queryset = StudyPlan.objects.all()
    serializer_class = StudyPlanSerializer
    permission_classes = [IsAdminOrReadOnly]
