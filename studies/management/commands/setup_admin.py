from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'إعداد حساب المدير والمجموعات الأساسية'

    def handle(self, *args, **options):
        # 1. إنشاء المجموعات
        groups = ['GraduateAdmin', 'AcademicSupervisor', 'GraduateStudent']
        for group_name in groups:
            Group.objects.get_or_create(name=group_name)
            self.stdout.write(self.style.SUCCESS(f'تم التأكد من وجود مجموعة: {group_name}'))

        # 2. إنشاء المدير (admin@learnnov.com)
        admin_email = 'admin@learnnov.com'
        if not User.objects.filter(username=admin_email).exists() and not User.objects.filter(email=admin_email).exists():
            admin = User.objects.create_superuser(
                username=admin_email,
                email=admin_email,
                password='admin123',
                first_name='مدير',
                last_name='النظام'
            )
            # إضافة للمجموعة
            admin_group = Group.objects.get(name='GraduateAdmin')
            admin.groups.add(admin_group)
            self.stdout.write(self.style.SUCCESS(f'تم إنشاء حساب المدير بنجاح: {admin_email}'))
        else:
            self.stdout.write(self.style.WARNING(f'حساب المدير {admin_email} موجود مسبقاً.'))

        # 3. إنشاء مشرف تجريبي (supervisor@learnnov.com)
        sup_email = 'supervisor@learnnov.com'
        if not User.objects.filter(username=sup_email).exists():
            sup = User.objects.create_user(
                username=sup_email,
                email=sup_email,
                password='admin123',
                first_name='مشرف',
                last_name='تجريبي'
            )
            sup_group = Group.objects.get(name='AcademicSupervisor')
            sup.groups.add(sup_group)
            self.stdout.write(self.style.SUCCESS(f'تم إنشاء حساب المشرف بنجاح: {sup_email}'))

        # 4. إنشاء طالب تجريبي (student@learnnov.com)
        std_email = 'student@learnnov.com'
        if not User.objects.filter(username=std_email).exists():
            std = User.objects.create_user(
                username=std_email,
                email=std_email,
                password='admin123',
                first_name='طالب',
                last_name='تجريبي'
            )
            std_group = Group.objects.get(name='GraduateStudent')
            std.groups.add(std_group)
            self.stdout.write(self.style.SUCCESS(f'تم إنشاء حساب الطالب بنجاح: {std_email}'))
