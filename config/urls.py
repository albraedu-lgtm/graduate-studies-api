from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from rest_framework.routers import DefaultRouter
from studies.views import (
    ProgramViewSet, EnrollmentViewSet, ThesisViewSet,
    SupervisionViewSet, SeminarViewSet, ReportViewSet,
    DashboardView, LoginView, UserInfoView, ApprovalViewSet,
    ResourceViewSet, StudentProfileViewSet, SupervisorProfileViewSet,
    CertificateViewSet, AttachmentViewSet, ThesisStageViewSet,
    FeedbackViewSet, AuditLogViewSet, NotificationViewSet,
    CommentViewSet, StudyPlanViewSet, HealthCheckView
)

router = DefaultRouter()
router.register('programs', ProgramViewSet)
router.register('enrollments', EnrollmentViewSet)
router.register('theses', ThesisViewSet)
router.register('supervision', SupervisionViewSet)
router.register('seminars', SeminarViewSet)
router.register('progress-reports', ReportViewSet)
router.register('approvals', ApprovalViewSet)
router.register('resources', ResourceViewSet)
router.register('student-profiles', StudentProfileViewSet)
router.register('supervisor-profiles', SupervisorProfileViewSet)
router.register('certificates', CertificateViewSet)
router.register('attachments', AttachmentViewSet)
router.register('thesis-stages', ThesisStageViewSet)
router.register('feedback', FeedbackViewSet)
router.register('audit-logs', AuditLogViewSet)
router.register('notifications', NotificationViewSet)
router.register('comments', CommentViewSet)
router.register('study-plans', StudyPlanViewSet)

urlpatterns = [
    path('', lambda r: HttpResponse("Learnnov Backend is Running"), name='root'),
    path('admin/', admin.site.urls),
    path('api/graduate/', include(router.urls)),
    path('api/graduate/dashboard/', DashboardView.as_view()),
    path('api/graduate/verify-certificate/<uuid:pk>/', CertificateViewSet.as_view({'get': 'verify_cert'})),
    path('api/login/', LoginView.as_view()),
    path('api/user/v1/account/login_session/', LoginView.as_view()), # Keep as fallback
    path('api/user/v1/me/', UserInfoView.as_view()),
    path('health/', HealthCheckView.as_view()),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
