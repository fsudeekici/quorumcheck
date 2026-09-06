from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "quorumcheck",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks.validator_tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    # Sonuclarin backend'de ne kadar tutulacagi. Aggregator zaten
    # sonuclari alir almaz DB'ye yazdigi icin uzun tutmaya gerek yok.
    result_expires=3600,
)
