from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import viewsets
from .serializers import PageSerializer
from .models import orders
from django.db.models import Count
# Create your views here.

class OrdersView(viewsets.ModelViewSet):
    serializer_class = PageSerializer
    def get_queryset(self):
        """
        This view should filter orders base on removed value in query or all element if no parameters in query
        """
        try:
            return orders.objects.filter(removed=self.request.query_params['removed']).values('date_of_supply').order_by('date_of_supply').annotate(day_orders=Count('date_of_supply'))
        except:
            return orders.objects.all().values('date_of_supply').order_by('date_of_supply').annotate(day_orders=Count('date_of_supply'))
