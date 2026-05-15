import logging
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)

def notify_admins(title, message, notification_type='warning', link=None):
    """
    نسخة مبسطة من نظام التنبيهات للواجهة الخلفية المستقلة.
    في الإنتاج، يمكن ربطها بنظام Firebase أو البريد الإلكتروني.
    """
    print(f"NOTIFICATION [To Admins]: {title} - {message}")
    logger.info(f"Admin Notification: {title} | {message}")
    
    # يمكن إضافة منطق إرسال بريد هنا مستقبلاً
