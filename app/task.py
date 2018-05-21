from celery import Celery
from flask import Flask
import time

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


app1 = Flask(__name__)

app1.config.update(
    CELERY_BROKER_URL='redis://redis:6379/0',
    CELERY_RESULT_BACKEND='redis://redis:6379/0'
)

celery = make_celery(app1)

@celery.task(bind=True)
def long_task(self):
    time.sleep(5)
    self.update_state(state='PROGRESS', meta={'current': 25, 'total': 100, 'status': 'task 1 complete'})
    time.sleep(5)
    self.update_state(state='PROGRESS', meta={'current': 50, 'total': 100, 'status': 'task 2 complete'})
    time.sleep(5)
    self.update_state(state='PROGRESS', meta={'current': 75, 'total': 100, 'status': 'task 3 complete'})
    time.sleep(5)
    self.update_state(state='PROGRESS', meta={'current': 90, 'total': 100, 'status': 'task 4 complete'})

    return {'current': 100, 'total': 100, 'status': 'Task completed!',
            'result': 'Task completed'}


