# Generated by Django 5.1.6 on 2025-04-15 08:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0009_user_performance_statistics'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='year_left_to_play',
            field=models.DateField(blank=True, max_length=10, null=True),
        ),
    ]
