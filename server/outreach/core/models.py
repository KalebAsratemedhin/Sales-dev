from django.db import models

# Create your models here.
from django.db import models


class Persona(models.Model):
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Lead(models.Model):
    email = models.EmailField()
    name = models.CharField(max_length=255, blank=True)
    company_name = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=64, default="new")
    source = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email