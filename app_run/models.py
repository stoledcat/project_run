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
    distance = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True)


class AthleteInfo(models.Model):
    weight = models.IntegerField(null=True)
    goals = models.TextField(null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class Challenge(models.Model):
    full_name = models.CharField(max_length=255)
    athlete = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("athlete", "full_name")


class Position(models.Model):
    run = models.ForeignKey(Run, on_delete=models.CASCADE, null=True, blank=True, related_name="positions")
    latitude = models.DecimalField(max_digits=7, decimal_places=4, null=True, blank=True)
    longitude = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)

    def __str__(self):
        return f"Position {self.id} for Run {self.run.id}"