@echo off
echo Starting Celery Worker...
cd backend
celery -A config worker -l info
pause

