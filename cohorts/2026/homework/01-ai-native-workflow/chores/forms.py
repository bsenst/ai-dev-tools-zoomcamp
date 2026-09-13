from django import forms

from .models import Chore


class ChoreForm(forms.ModelForm):
    class Meta:
        model = Chore
        fields = ["title", "description", "assignee", "due_date"]
        widgets = {
            "due_date": forms.DateInput(attrs={"type": "date"}),
        }
