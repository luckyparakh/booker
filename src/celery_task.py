from celery import Celery
from src.email import mail, create_message
from asgiref.sync import async_to_sync

c_app = Celery()
c_app.config_from_object('src.config')


@c_app.task()
def send_email(emails: list[str], subject: str, body: str):
    try:
        message = create_message(emails, subject, body)
        async_to_sync(mail.send_message)(message)
        print("Email Sent")
    except Exception as e:
        raise send_email.retry(exc=e, retry_kwargs={'max_retries': 5, 'default_retry_delay': 20})
