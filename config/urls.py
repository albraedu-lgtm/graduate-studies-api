from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from studies.views import (
    ProgramViewSet, EnrollmentViewSet, ThesisViewSet,
    SupervisionViewSet, SeminarViewSet, ReportViewSet,
    DashboardView, LoginView, UserInfoView
)

router = DefaultRouter()
router.register('programs', ProgramViewSet)
router.register('enrollments', EnrollmentViewSet)
router.register('theses', ThesisViewSet)
router.register('supervision', SupervisionViewSet)
router.register('seminars', SeminarViewSet)
router.register('progress-reports', ReportViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/graduate/', include(router.urls)),
    path('api/graduate/dashboard/', DashboardView.as_view()),
    path('api/user/v1/account/login_session/', LoginView.as_view()),
    path('api/user/v1/me/', UserInfoView.as_view()),
]
