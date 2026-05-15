# Graduate Studies API - Backend
# ================================

## Deployment on Render.com

### Quick Deploy
1. Push this folder to a GitHub repository
2. Go to https://render.com and create a new "Web Service"
3. Connect your GitHub repo
4. Render will auto-detect the configuration

### Manual Configuration (if needed)
- **Build Command:** `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
- **Start Command:** `gunicorn config.wsgi --bind 0.0.0.0:$PORT`
- **Environment:** Python 3.11

### After First Deploy
Run this command in Render Shell to seed demo data:
```
python manage.py seed_data
```

### API Endpoints
- `/api/graduate/programs/`
- `/api/graduate/enrollments/`
- `/api/graduate/theses/`
- `/api/graduate/supervision/`
- `/api/graduate/seminars/`
- `/api/graduate/progress-reports/`
- `/api/graduate/approvals/`
- `/api/graduate/dashboard/`
- `/api/user/v1/account/login_session/`
- `/admin/` (Django Admin Panel)
