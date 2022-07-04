from django.db import models

# Create your models here.
class orders(models.Model):
    id = models.IntegerField()
    order_number=models.CharField(max_length=120, primary_key=True)
    price=models.FloatField()
    price_rub=models.FloatField()
    date_of_supply=models.DateField()
    removed=models.BooleanField(default=False)
    notification=models.BooleanField(default=False)
    def _str_(self):
        return self.order_number