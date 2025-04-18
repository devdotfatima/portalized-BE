# Generated by Django 5.1.6 on 2025-04-16 11:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sports', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='sport',
            name='gender',
            field=models.CharField(choices=[('male', 'Male'), ('female', 'Female')], default='male', max_length=10),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='sport',
            name='name',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterUniqueTogether(
            name='sport',
            unique_together={('name', 'gender')},
        ),
    ]
