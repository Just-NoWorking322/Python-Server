from django_filters import rest_framework as filters
from .models import Service, ServiceCategory


class ServiceFilter(filters.FilterSet):
    """
    Набор фильтров для каталога услуг:
    • category: фильтрация по категории (например, 'repair', 'cleaning', 'education', 'beauty', 'it', 'other')
    • is_active: фильтр по статусу «Принимаю заказы сейчас» (true/false)
    • min_price / max_price: фильтр по диапазону цен
    """
    category = filters.ChoiceFilter(
        choices=ServiceCategory.choices,
        help_text="Фильтр по категории (repair, cleaning, education, beauty, it, other)"
    )
    is_active = filters.BooleanFilter(
        field_name='is_active',
        help_text="Фильтр по признаку «Принимаю заказы сейчас» (true/false)"
    )
    min_price = filters.NumberFilter(
        field_name='price',
        lookup_expr='gte',
        help_text="Минимальная цена"
    )
    max_price = filters.NumberFilter(
        field_name='price',
        lookup_expr='lte',
        help_text="Максимальная цена"
    )

    class Meta:
        model = Service
        fields = ['category', 'is_active', 'min_price', 'max_price']
