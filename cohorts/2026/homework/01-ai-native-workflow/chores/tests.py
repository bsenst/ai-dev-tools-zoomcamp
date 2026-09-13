from datetime import date, timedelta

from django.test import TestCase
from django.urls import reverse

from .models import Chore


class ChoreModelTests(TestCase):
    def test_chore_defaults_to_incomplete(self):
        chore = Chore.objects.create(
            title="Wash dishes",
            assignee="Alice",
            due_date=date.today() + timedelta(days=1),
        )

        self.assertFalse(chore.completed)
        self.assertEqual(str(chore), "Wash dishes")

    def test_overdue_chore_is_detected_when_unfinished(self):
        overdue = Chore.objects.create(
            title="Vacuum living room",
            assignee="Bob",
            due_date=date.today() - timedelta(days=1),
        )

        self.assertTrue(overdue.is_overdue())

    def test_completed_chore_is_not_overdue(self):
        completed = Chore.objects.create(
            title="Take out trash",
            assignee="Carol",
            due_date=date.today() - timedelta(days=2),
            completed=True,
        )

        self.assertFalse(completed.is_overdue())


class ChoreViewTests(TestCase):
    def test_dashboard_lists_chores(self):
        Chore.objects.create(
            title="Clean bathroom",
            assignee="Dana",
            due_date=date.today() + timedelta(days=3),
        )

        response = self.client.get(reverse("chores:index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Clean bathroom")
        self.assertContains(response, "Dana")

    def test_dashboard_can_create_chore(self):
        response = self.client.post(
            reverse("chores:create"),
            {
                "title": "Water plants",
                "description": "Water the house plants in the living room.",
                "assignee": "Ethan",
                "due_date": (date.today() + timedelta(days=2)).isoformat(),
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Chore.objects.filter(title="Water plants").exists())
