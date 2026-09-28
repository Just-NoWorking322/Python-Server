from rest_framework import serializers
from services.models import Service
from .models import Order


class OrderSerializer(serializers.ModelSerializer):
    """
    Сериализатор заявки клиента на услугу.
    """
    service_id = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.all(),
        source='service',
        write_only=True,
        help_text="ID услуги, которую заказывает клиент"
    )
    service_title = serializers.ReadOnlyField(source='service.title')
    service_category = serializers.ReadOnlyField(source='service.get_category_display')
    service_final_price = serializers.ReadOnlyField(source='service.final_price')
    master_name = serializers.ReadOnlyField(source='service.author.username')

    class Meta:
        model = Order
        fields = [
            'id',
            'service_id',
            'service_title',
            'service_category',
            'service_final_price',
            'master_name',
            'client_name',
            'client_phone',
            'comment',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'service_title',
            'service_category',
            'service_final_price',
            'master_name',
            'created_at',
        ]

    def validate(self, attrs):
        service = attrs.get('service')
        if service and not service.is_active:
            raise serializers.ValidationError(
                {"service_id": "К сожалению, мастер сейчас не принимает заказы на эту услугу."}
            )
        return attrs
