from django.db import models

# Create your models here.

class App(models.Model):
    short_name = models.CharField(max_length=10)
    name = models.CharField(max_length=200)