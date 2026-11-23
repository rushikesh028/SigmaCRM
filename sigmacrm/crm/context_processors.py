from django.db.models import Sum, Count, Q
from .models import Lead, Deal, Task


def crm_stats(request):
    if not request.user.is_authenticated:
        return {}
    return {
        'sidebar_open_tasks': Task.objects.filter(
            status__in=['pending', 'in_progress'],
            assigned_to=request.user
        ).count() if request.user.is_authenticated else 0,
    }
