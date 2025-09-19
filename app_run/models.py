from django.contrib.auth.models import User
from django.db import models

# Create your models here.


class Run(models.Model):
    athlete = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    comment = models.TextField()
