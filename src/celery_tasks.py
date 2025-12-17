from typing import List

from asgiref.sync import async_to_sync
from celery import Celery

from src.mail import create_message, mail

app = Celery()

app.config_from_object("src.config")

# Run the Celery worker with the following command:
#   celery -A src.celery_tasks.app worker --loglevel=info
# Running the Celery flower (GUI) with the following command:
#   celery -A src.celery_tasks.app flower --port=5555


@app.task()
def send_email(recipients: List[str], subject: str, body: str):
    """Sends an email asynchronously using Celery."""
    message = create_message(
        recipients=recipients,
        subject=subject,
        body=body,
    )

    async_to_sync(mail.send_message)(message)
