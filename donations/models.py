from django.db import models

# Create your models here.

from django.db import models

class Donation(models.Model):
    CATEGORY_CHOICES = [
        ('Cooked', 'Cooked'),
        ('Packaged', 'Packaged'),
        ('Raw', 'Raw'),
    ]

    donor = models.CharField(max_length=100)
    contact = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    food_item = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()
    expiry_date = models.DateField()
    location = models.CharField(max_length=200)
    status = models.CharField(max_length=20, default="Available")
    latitude = models.FloatField(null=True, blank=True)      # NEW: Latitude field
    longitude = models.FloatField(null=True, blank=True)     # NEW: Longitude field

    def __str__(self):
        return f"{self.donor} - {self.food_item}"

