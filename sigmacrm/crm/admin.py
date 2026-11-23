from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile, Lead, Contact, Deal, Task, Activity, Note


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'


class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'company', 'email', 'status', 'source', 'assigned_to', 'created_at']
    list_filter = ['status', 'source', 'created_at']
    search_fields = ['full_name', 'company', 'email', 'phone']
    raw_id_fields = ['assigned_to', 'created_by']


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'company', 'email', 'phone', 'job_title', 'created_at']
    search_fields = ['full_name', 'company', 'email']
    raw_id_fields = ['lead', 'created_by']


@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    list_display = ['title', 'value', 'stage', 'assigned_to', 'expected_close_date', 'created_at']
    list_filter = ['stage', 'created_at']
    search_fields = ['title']
    raw_id_fields = ['lead', 'contact', 'assigned_to', 'created_by']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'priority', 'status', 'assigned_to', 'due_date', 'is_overdue']
    list_filter = ['status', 'priority']
    search_fields = ['title']
    raw_id_fields = ['assigned_to', 'lead', 'deal', 'created_by']


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ['subject', 'activity_type', 'lead', 'performed_by', 'created_at']
    list_filter = ['activity_type']
    search_fields = ['subject']


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ['content', 'created_by', 'created_at']
    search_fields = ['content']
