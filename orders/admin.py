from django.contrib import admin
from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Управление заявками клиентов в панели администратора.
    Администратор может видеть все заявки и удалять неактуальные.
    """
    list_display = (
        'id',
        'client_name',
        'client_phone',
        'service',
        'get_master_name',
        'created_at',
    )
    list_filter = ('created_at', 'service__category')
    search_fields = (
        'client_name',
        'client_phone',
        'comment',
        'service__title',
        'service__author__username'
    )
    readonly_fields = ('created_at',)
    list_per_page = 20

    @admin.display(description="Мастер")
    def get_master_name(self, obj):
        return obj.service.author.username
