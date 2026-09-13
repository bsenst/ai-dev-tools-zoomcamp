from django.urls import path

from . import views

app_name = "chores"

urlpatterns = [
    path("", views.index, name="index"),
    path("create/", views.create_chore, name="create"),
    path("toggle/<int:chore_id>/", views.toggle_chore, name="toggle"),
]
