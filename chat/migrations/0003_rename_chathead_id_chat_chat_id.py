# Generated by Django 5.1.6 on 2025-04-18 10:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0002_alter_chat_unique_together_chat_participants_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='chat',
            old_name='chathead_id',
            new_name='chat_id',
        ),
    ]
