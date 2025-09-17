from django.db import models
from apps.core.models import TimeStampedModel, OwnedModel

class Good(TimeStampedModel, OwnedModel):
    title = models.CharField(max_length=200)

    def __str__(self) -> str:
        return f"{self.id}:{self.title}"

class Order(TimeStampedModel, OwnedModel):
    number = models.CharField(max_length=50)

    def __str__(self) -> str:
        return f"{self.id}:{self.number}"
