from django.db import models

class Product(models.Model):
    full_name = models.CharField(max_length=512, null=True, blank=True)
    product_code = models.CharField(max_length=128, unique=True, null=True, blank=True)
    price = models.CharField(max_length=128, null=True, blank=True)
    special_price = models.CharField(max_length=128, null=True, blank=True)
    seller = models.CharField(max_length=256, null=True, blank=True)
    reviews_count = models.IntegerField(null=True, blank=True)
    color = models.CharField(max_length=128, null=True, blank=True)
    memory = models.CharField(max_length=128, null=True, blank=True)
    series = models.CharField(max_length=256, null=True, blank=True)
    screen_diagonal = models.CharField(max_length=128, null=True, blank=True)
    display_resolution = models.CharField(max_length=128, null=True, blank=True)
    photos = models.JSONField(null=True, blank=True)
    specifications = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.full_name or 'Unnamed Product'