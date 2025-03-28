from django.contrib import admin
from .models import ContactMessage

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "created_at")  # Columns displayed in the admin list view
    search_fields = ("name", "email", "message")  # Enable search by name, email, and message
    list_filter = ("created_at",)  # Filter messages by creation date
    ordering = ("-created_at",)  # Show the latest messages first
    readonly_fields = ("created_at",)  # Make the created_at field read-only