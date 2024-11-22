from django.db import models

# Create your models here.
from django.db import models

class Email(models.Model):
    sender = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    snippet = models.TextField()
    date_received = models.DateTimeField()

    def __str__(self):
        return self.subject
