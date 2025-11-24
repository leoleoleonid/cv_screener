from celery import Celery

from app.core.config import AppSettings

settings = AppSettings()
settings.ensure_directories()

celery_app = Celery("cv_screener")
celery_app.conf.broker_url = settings.celery_broker_url
celery_app.conf.result_backend = settings.celery_result_backend
celery_app.conf.accept_content = ["json"]
celery_app.conf.result_serializer = "json"
celery_app.conf.task_serializer = "json"
celery_app.conf.imports = ("app.tasks.cv_tasks",)
celery_app.autodiscover_tasks(["app.tasks"])
