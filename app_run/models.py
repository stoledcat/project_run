from django.db import models


# Create your models here.
class User(models.Model):
    name = models.CharField(max_length=50, blank=False)


class Run(models.Model):
    athlete = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(blank=True)
