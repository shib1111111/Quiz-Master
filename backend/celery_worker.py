# /celery_worker.py
from celery import Celery
from app import app

def make_celery(app):
    celery = Celery(
        app.import_name,
        broker=app.config["CELERY_BROKER_URL"],
        backend=app.config["CELERY_RESULT_BACKEND"]
    )
    celery.conf.update(app.config)
    
    # Ensuring tasks have application context
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery

celery_app = make_celery(app)
import celery_tasks
# print(celery_app.tasks)  # Should include 'send_reset_email'

# celery -A celery_worker.celery_app worker --pool=threads --loglevel=info