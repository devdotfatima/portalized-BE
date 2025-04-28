from django.contrib import admin
from .models import SessionRequest

@admin.register(SessionRequest)
class SessionRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'athlete', 'coach', 'session_date', 'session_time', 'status', 'created_at')
    list_filter = ('status', 'session_date', 'coach')
    search_fields = ('athlete__email', 'coach__email', 'notes')
    ordering = ('-created_at',)

    # Optional: make it readonly after creation if you want
    readonly_fields = ('created_at',)

    # Optional: customize fields displayed when you click on a session
    fieldsets = (
        (None, {
            'fields': ('athlete', 'coach', 'session_date', 'session_time', 'notes', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
        }),
    )