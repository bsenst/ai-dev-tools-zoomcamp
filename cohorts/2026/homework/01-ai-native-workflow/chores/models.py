from datetime import date

from django.db import models


class Chore(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    assignee = models.CharField(max_length=100)
    due_date = models.DateField()
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["due_date", "title"]

    def __str__(self):
        return self.title

    def is_overdue(self):
        return (not self.completed) and self.due_date < date.today()
