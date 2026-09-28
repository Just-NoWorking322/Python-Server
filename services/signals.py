from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Service

TOP_5_SERVICES_CACHE_KEY = 'top_5_popular_services'


def invalidate_top_5_cache():
    """
    Очистка кэша блока «Топ-5 популярных услуг».
    Вызывается сразу, как только мастер добавляет, обновляет или удаляет услугу!
    """
    cache.delete(TOP_5_SERVICES_CACHE_KEY)


@receiver([post_save, post_delete], sender=Service)
def service_cache_invalidation_handler(sender, instance, **kwargs):
    """
    Сигнал: если любая услуга добавлена, отредактирована или удалена,
    кэш на главной странице мгновенно сбрасывается.
    """
    invalidate_top_5_cache()
