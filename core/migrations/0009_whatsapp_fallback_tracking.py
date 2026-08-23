# Generated manually for WhatsApp multi-recipient delivery tracking.

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0008_remove_parent_info_fields"),
    ]

    operations = [
        migrations.AlterField(
            model_name="whatsappmessageanalytics",
            name="parent_type",
            field=models.CharField(
                choices=[
                    ("Father", "Father"),
                    ("Mother", "Mother"),
                    ("Father, Mother", "Father, Mother"),
                ],
                max_length=20,
                verbose_name="Parent Type",
            ),
        ),
        migrations.AddField(
            model_name="whatsappmessageanalytics",
            name="attempted_numbers",
            field=models.JSONField(
                blank=True,
                default=list,
                verbose_name="Attempted Numbers",
            ),
        ),
        migrations.AddField(
            model_name="whatsappmessageanalytics",
            name="successful_numbers",
            field=models.JSONField(
                blank=True,
                default=list,
                verbose_name="Successful Numbers",
            ),
        ),
        migrations.AddField(
            model_name="whatsappmessageanalytics",
            name="failed_numbers",
            field=models.JSONField(
                blank=True,
                default=list,
                verbose_name="Failed Numbers",
            ),
        ),
        migrations.AddField(
            model_name="whatsappmessageanalytics",
            name="status",
            field=models.CharField(
                choices=[
                    ("sent", "Sent"),
                    ("failed", "Failed"),
                ],
                default="sent",
                max_length=20,
                verbose_name="Send Status",
            ),
        ),
        migrations.AddField(
            model_name="whatsappmessageanalytics",
            name="failure_reason",
            field=models.TextField(
                blank=True,
                null=True,
                verbose_name="Failure Reason",
            ),
        ),
        migrations.AddField(
            model_name="whatsappmessageanalytics",
            name="timestamp",
            field=models.DateTimeField(
                auto_now_add=True,
                default=django.utils.timezone.now,
                verbose_name="Status Timestamp",
            ),
            preserve_default=False,
        ),
    ]
