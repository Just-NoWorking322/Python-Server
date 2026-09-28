from decimal import Decimal
from rest_framework import serializers
from .models import Service


class ServiceSerializer(serializers.ModelSerializer):
    """
    Сериализатор карточки услуги с готовой ценой со скидкой и валидацией.
    """
    author_id = serializers.ReadOnlyField(source='author.id')
    author_username = serializers.ReadOnlyField(source='author.username')
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    # Сервер сам сразу отдает клиенту готовую итоговую цену с учетом скидки!
    final_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
        help_text="Итоговая цена для клиента со скидкой (рассчитана сервером)"
    )

    class Meta:
        model = Service
        fields = [
            'id',
            'title',
            'description',
            'category',
            'category_display',
            'price',
            'discount',
            'final_price',
            'is_active',
            'author_id',
            'author_username',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'author_id',
            'author_username',
            'final_price',
            'category_display',
            'created_at',
            'updated_at',
        ]

    def validate_title(self, value: str) -> str:
        """
        Проверка: название услуги не слишком короткое (минимум 5 символов).
        """
        if len(value.strip()) < 5:
            raise serializers.ValidationError("Название услуги должно содержать минимум 5 символов (например, «Установка стиральной машины»)")
        return value.strip()

    def validate_discount(self, value: int) -> int:
        """
        Проверка: скидка от 0 до 90%.
        """
        if value < 0 or value > 90:
            raise serializers.ValidationError("Скидка может быть только в диапазоне от 0% до 90%!")
        return value

    def validate_price(self, value: Decimal) -> Decimal:
        """
        Проверка: цена должна быть строго больше нуля.
        """
        if value <= Decimal('0'):
            raise serializers.ValidationError("Базовая цена услуги должна быть больше 0!")
        return value
