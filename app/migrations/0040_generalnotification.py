# Generated by Django 4.2.21 on 2025-05-19 05:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0039_studymaterial"),
    ]

    operations = [
        migrations.CreateModel(
            name="GeneralNotification",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "target_type",
                    models.CharField(
                        choices=[
                            ("ALL", "All Users"),
                            ("STAFF", "All Staff"),
                            ("STUDENT", "All Students"),
                            ("BOTH", "Staff and Students"),
                        ],
                        default="ALL",
                        max_length=10,
                    ),
                ),
                ("message", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="sent_notifications",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
