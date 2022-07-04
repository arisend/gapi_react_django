from rest_framework import serializers
from .models import orders

class PageSerializer(serializers.ModelSerializer):
    day_orders = serializers.IntegerField()
    class Meta:
        model = orders
        fields = ('date_of_supply', 'day_orders')