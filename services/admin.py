from django.contrib import admin
from .models import Service


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    """
    Настройка отображения услуг в панели администратора.
    """
    list_display = (
        'id',
        'title',
        'category',
        'price',
        'discount',
        'final_price_display',
        'is_active',
        'author',
        'created_at',
    )
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('title', 'description', 'author__username', 'author__email')
    list_editable = ('is_active', 'discount')
    readonly_fields = ('created_at', 'updated_at', 'final_price_display')
    list_per_page = 20

    @admin.display(description="Итоговая цена (со скидкой)")
    def final_price_display(self, obj):
        return f"{obj.final_price} сом/руб"
