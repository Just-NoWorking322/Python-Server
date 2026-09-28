from django.db import models
from django.core.validators import RegexValidator
from services.models import Service


class Order(models.Model):
    """
    Модель заявки клиента на услугу («Заказать»).
    
    ТЗ:
    • Клиент указывает свое имя, контактный телефон и комментарий (адрес или удобное время).
    • Мастер в своем личном кабинете должен видеть только те заявки,
      которые оставили на его услуги (чужие заявки скрыты).
    • Удалять заявки из базы может только администратор сервиса.
    """
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name="Выбранная услуга"
    )
    client_name = models.CharField(
        max_length=150,
        verbose_name="Имя клиента",
        help_text="Как обращаться к клиенту"
    )
    phone_validator = RegexValidator(
        regex=r'^\+?[0-9\s\-\(\)]{7,20}$',
        message="Введите корректный номер телефона (например, +996 555 123456)."
    )
    client_phone = models.CharField(
        max_length=30,
        validators=[phone_validator],
        verbose_name="Контактный телефон",
        help_text="Номер телефона для связи"
    )
    comment = models.TextField(
        blank=True,
        verbose_name="Комментарий",
        help_text="Адрес вызова мастера или удобное время"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата и время заявки"
    )

    class Meta:
        verbose_name = "Заявка клиента"
        verbose_name_plural = "Заявки клиентов"
        ordering = ['-created_at']

    def __str__(self):
        return f"Заявка #{self.id} от {self.client_name} на '{self.service.title}'"
