from decimal import Decimal
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator, MinLengthValidator

User = get_user_model()


class ServiceCategory(models.TextChoices):
    """
    Категории услуг по ТЗ:
    Ремонт, Уборка, Обучение, Красота, IT, Другое
    """
    REPAIR = 'repair', 'Ремонт'
    CLEANING = 'cleaning', 'Уборка'
    EDUCATION = 'education', 'Обучение'
    BEAUTY = 'beauty', 'Красота'
    IT = 'it', 'IT'
    OTHER = 'other', 'Другое'


class Service(models.Model):
    """
    Модель карточки услуги мастера.
    
    Требования ТЗ:
    • Название услуги: минимум от 5 символов.
    • Описание: что конкретно входит в работу.
    • Категория: выбор из фиксированного списка.
    • Цена и Скидка: базовая цена + скидка от 0 до 90%.
    • Итоговая цена: вычисляется сервером автоматически.
    • Статус: галочка «Принимаю заказы сейчас» (is_active).
    • Автор: мастер, создавший услугу.
    """
    title = models.CharField(
        max_length=200,
        validators=[MinLengthValidator(5, message="Название услуги должно содержать минимум 5 символов!")],
        verbose_name="Название услуги",
        help_text="Например: 'Установка стиральной машины' (минимум 5 символов)"
    )
    description = models.TextField(
        verbose_name="Описание услуги",
        help_text="Что конкретно входит в работу"
    )
    category = models.CharField(
        max_length=20,
        choices=ServiceCategory.choices,
        default=ServiceCategory.OTHER,
        verbose_name="Категория"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'), message="Базовая цена должна быть больше нуля!")],
        verbose_name="Базовая цена (сом/руб)"
    )
    discount = models.PositiveIntegerField(
        default=0,
        validators=[
            MinValueValidator(0, message="Скидка не может быть меньше 0%"),
            MaxValueValidator(90, message="Скидка не может превышать 90%!")
        ],
        verbose_name="Скидка (%)",
        help_text="Скидка для клиентов от 0% до 90%"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Принимаю заказы сейчас",
        help_text="Статус доступности услуги: принимает ли мастер заказы сейчас"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='services',
        verbose_name="Автор (мастер)"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата добавления"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )

    class Meta:
        verbose_name = "Услуга"
        verbose_name_plural = "Каталог услуг"
        ordering = ['-created_at']

    @property
    def final_price(self) -> Decimal:
        """
        Сервер сам считает готовую итоговую цену с учетом скидки:
        Итоговая цена = price * (100 - discount) / 100
        """
        discount_factor = Decimal(100 - self.discount) / Decimal(100)
        return (self.price * discount_factor).quantize(Decimal('0.01'))

    def __str__(self):
        return f"{self.title} [{self.get_category_display()}] — {self.final_price}"
