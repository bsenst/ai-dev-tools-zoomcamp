from django.shortcuts import redirect, render

from .forms import ChoreForm
from .models import Chore


def index(request):
    chores = Chore.objects.all()
    return render(request, "chores/index.html", {"chores": chores})


def create_chore(request):
    if request.method == "POST":
        form = ChoreForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("chores:index")
    else:
        form = ChoreForm()

    return render(request, "chores/create.html", {"form": form})


def toggle_chore(request, chore_id):
    chore = Chore.objects.get(pk=chore_id)
    chore.completed = not chore.completed
    chore.save()
    return redirect("chores:index")
