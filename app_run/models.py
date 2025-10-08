from django.contrib.auth.models import User
from django.db import models

# Create your models here.


class Run(models.Model):
    INIT = "init"
    START = "in_progress"
    STOP = "finished"
    RUN_STATUS_CHOICES = [(INIT, "Инициализация"), (START, "Старт"), (STOP, "Стоп")]

    athlete = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    comment = models.TextField()
    status = models.CharField(choices=RUN_STATUS_CHOICES, default=INIT)


class AthleteInfo(models.Model):
    weight = models.IntegerField(null=True)
    goals = models.TextField(null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class Challenge(models.Model):
    full_name = models.TextField(null=True)
    athlete = models.OneToOneField(User, on_delete=models.CASCADE)
