from django.contrib import admin
from .models import *

admin.site.register(AcademicProgram)
admin.site.register(ProgramEnrollment)
admin.site.register(Thesis)
admin.site.register(SupervisionRelation)
admin.site.register(Seminar)
admin.site.register(SeminarRegistration)
admin.site.register(ProgressReport)
