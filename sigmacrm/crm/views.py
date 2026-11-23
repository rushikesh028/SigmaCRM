from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count, Avg
from django.db.models.functions import TruncMonth, TruncDate
from django.http import JsonResponse, HttpResponseForbidden
from django.utils import timezone
from django.views.decorators.http import require_POST, require_http_methods
from datetime import timedelta, datetime
from decimal import Decimal
import json
from .models import Lead, Contact, Deal, Task, Activity, Note, Profile
from .forms import (
    LoginForm, LeadForm, ContactForm, DealForm, TaskForm,
    ActivityForm, NoteForm, UserCreateForm
)


def is_admin(user):
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    try:
        return user.profile.role == 'admin'
    except Profile.DoesNotExist:
        return False


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
        next_url = request.GET.get('next', 'dashboard')
        return redirect(next_url)
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


@login_required
def dashboard(request):
    today = timezone.now().date()
    thirty_days_ago = today - timedelta(days=30)

    total_leads = Lead.objects.count()
    new_leads = Lead.objects.filter(status='new').count()
    open_deals = Deal.objects.exclude(stage__in=['won', 'lost']).count()
    won_deals = Deal.objects.filter(stage='won').count()
    lost_deals = Deal.objects.filter(stage='lost').count()
    total_revenue = Deal.objects.filter(stage='won').aggregate(
        total=Sum('value')
    )['total'] or Decimal('0')
    converted = Lead.objects.filter(status='converted').count()
    conversion_rate = round((converted / total_leads * 100), 1) if total_leads else 0

    # Leads over time (last 30 days)
    leads_over_time = (
        Lead.objects.filter(created_at__date__gte=thirty_days_ago)
        .annotate(day=TruncDate('created_at'))
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )
    leads_labels = [item['day'].strftime('%b %d') for item in leads_over_time]
    leads_data = [item['count'] for item in leads_over_time]

    # Leads by source
    leads_by_source = (
        Lead.objects.values('source')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    source_labels = [dict(Lead.SOURCE_CHOICES).get(i['source'], i['source']) for i in leads_by_source]
    source_data = [i['count'] for i in leads_by_source]

    # Deals by stage
    deals_by_stage = (
        Deal.objects.values('stage')
        .annotate(count=Count('id'), value=Sum('value'))
        .order_by('stage')
    )
    stage_labels = [dict(Deal.STAGE_CHOICES).get(i['stage'], i['stage']) for i in deals_by_stage]
    stage_counts = [i['count'] for i in deals_by_stage]

    recent_activities = Activity.objects.select_related(
        'performed_by', 'lead', 'deal'
    )[:10]
    upcoming_tasks = Task.objects.filter(
        status__in=['pending', 'in_progress'],
        due_date__gte=timezone.now()
    ).select_related('assigned_to').order_by('due_date')[:8]
    overdue_tasks = Task.objects.filter(
        status__in=['pending', 'in_progress'],
        due_date__lt=timezone.now()
    ).count()

    context = {
        'total_leads': total_leads,
        'new_leads': new_leads,
        'open_deals': open_deals,
        'won_deals': won_deals,
        'lost_deals': lost_deals,
        'total_revenue': total_revenue,
        'conversion_rate': conversion_rate,
        'leads_labels': json.dumps(leads_labels),
        'leads_data': json.dumps(leads_data),
        'source_labels': json.dumps(source_labels),
        'source_data': json.dumps(source_data),
        'stage_labels': json.dumps(stage_labels),
        'stage_counts': json.dumps(stage_counts),
        'recent_activities': recent_activities,
        'upcoming_tasks': upcoming_tasks,
        'overdue_tasks': overdue_tasks,
    }
    return render(request, 'dashboard.html', context)


# ---------- LEADS ----------
@login_required
def leads_list(request):
    qs = Lead.objects.select_related('assigned_to').all()
    q = request.GET.get('q', '').strip()
    status = request.GET.get('status', '')
    source = request.GET.get('source', '')
    assigned = request.GET.get('assigned', '')

    if q:
        qs = qs.filter(
            Q(full_name__icontains=q) |
            Q(company__icontains=q) |
            Q(email__icontains=q) |
            Q(phone__icontains=q)
        )
    if status:
        qs = qs.filter(status=status)
    if source:
        qs = qs.filter(source=source)
    if assigned:
        qs = qs.filter(assigned_to_id=assigned)

    paginator = Paginator(qs, 15)
    page = request.GET.get('page')
    leads = paginator.get_page(page)
    employees = User.objects.filter(is_active=True).order_by('username')

    return render(request, 'leads.html', {
        'leads': leads,
        'employees': employees,
        'status_choices': Lead.STATUS_CHOICES,
        'source_choices': Lead.SOURCE_CHOICES,
        'q': q,
        'status_filter': status,
        'source_filter': source,
        'assigned_filter': assigned,
    })


@login_required
def lead_create(request):
    form = LeadForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        lead = form.save(commit=False)
        lead.created_by = request.user
        lead.save()
        Activity.objects.create(
            lead=lead,
            activity_type='status_change',
            subject=f'Lead created with status {lead.get_status_display()}',
            performed_by=request.user,
        )
        messages.success(request, 'Lead created successfully.')
        return redirect('lead_detail', pk=lead.pk)
    return render(request, 'add_lead.html', {'form': form, 'title': 'Add Lead'})


@login_required
def lead_edit(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    old_status = lead.status
    form = LeadForm(request.POST or None, instance=lead)
    if request.method == 'POST' and form.is_valid():
        lead = form.save()
        if old_status != lead.status:
            Activity.objects.create(
                lead=lead,
                activity_type='status_change',
                subject=f'Status changed from {dict(Lead.STATUS_CHOICES).get(old_status)} to {lead.get_status_display()}',
                performed_by=request.user,
            )
        messages.success(request, 'Lead updated successfully.')
        return redirect('lead_detail', pk=lead.pk)
    return render(request, 'add_lead.html', {'form': form, 'title': 'Edit Lead', 'lead': lead})


@login_required
def lead_detail(request, pk):
    lead = get_object_or_404(Lead.objects.select_related('assigned_to', 'created_by'), pk=pk)
    activities = lead.activities.select_related('performed_by').all()[:30]
    notes = lead.lead_notes.select_related('created_by').all()
    tasks = lead.tasks.all()[:10]
    deals = lead.deals.all()
    note_form = NoteForm()
    activity_form = ActivityForm()
    return render(request, 'lead_details.html', {
        'lead': lead,
        'activities': activities,
        'notes': notes,
        'tasks': tasks,
        'deals': deals,
        'note_form': note_form,
        'activity_form': activity_form,
    })


@login_required
@require_POST
def lead_delete(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    name = lead.full_name
    lead.delete()
    messages.success(request, f'Lead "{name}" deleted.')
    return redirect('leads')


@login_required
@require_POST
def lead_add_note(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    form = NoteForm(request.POST)
    if form.is_valid():
        note = form.save(commit=False)
        note.lead = lead
        note.created_by = request.user
        note.save()
        messages.success(request, 'Note added.')
    return redirect('lead_detail', pk=pk)


@login_required
@require_POST
def lead_add_activity(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    form = ActivityForm(request.POST)
    if form.is_valid():
        act = form.save(commit=False)
        act.lead = lead
        act.performed_by = request.user
        act.save()
        messages.success(request, 'Activity logged.')
    return redirect('lead_detail', pk=pk)


# ---------- CONTACTS ----------
@login_required
def contacts_list(request):
    qs = Contact.objects.select_related('lead', 'created_by').all()
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(full_name__icontains=q) |
            Q(company__icontains=q) |
            Q(email__icontains=q)
        )
    paginator = Paginator(qs, 15)
    contacts = paginator.get_page(request.GET.get('page'))
    return render(request, 'contacts.html', {'contacts': contacts, 'q': q})


@login_required
def contact_create(request):
    form = ContactForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        contact = form.save(commit=False)
        contact.created_by = request.user
        contact.save()
        messages.success(request, 'Contact created.')
        return redirect('contacts')
    return render(request, 'contact_form.html', {'form': form, 'title': 'Add Contact'})


@login_required
def contact_edit(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    form = ContactForm(request.POST or None, instance=contact)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Contact updated.')
        return redirect('contacts')
    return render(request, 'contact_form.html', {'form': form, 'title': 'Edit Contact', 'contact': contact})


@login_required
@require_POST
def contact_delete(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    contact.delete()
    messages.success(request, 'Contact deleted.')
    return redirect('contacts')


# ---------- DEALS ----------
@login_required
def deals_list(request):
    stages = [s[0] for s in Deal.STAGE_CHOICES]
    deals_by_stage = {stage: Deal.objects.filter(stage=stage).select_related('assigned_to', 'lead') for stage in stages}
    form = DealForm()
    return render(request, 'deals.html', {
        'deals_by_stage': deals_by_stage,
        'stage_choices': Deal.STAGE_CHOICES,
        'form': form,
    })


@login_required
def deal_create(request):
    form = DealForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        deal = form.save(commit=False)
        deal.created_by = request.user
        deal.save()
        Activity.objects.create(
            deal=deal,
            activity_type='status_change',
            subject=f'Deal created in stage {deal.get_stage_display()}',
            performed_by=request.user,
        )
        messages.success(request, 'Deal created.')
        return redirect('deals')
    return render(request, 'deal_form.html', {'form': form, 'title': 'Add Deal'})


@login_required
def deal_edit(request, pk):
    deal = get_object_or_404(Deal, pk=pk)
    form = DealForm(request.POST or None, instance=deal)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Deal updated.')
        return redirect('deals')
    return render(request, 'deal_form.html', {'form': form, 'title': 'Edit Deal', 'deal': deal})


@login_required
@require_POST
def deal_update_stage(request, pk):
    deal = get_object_or_404(Deal, pk=pk)
    new_stage = request.POST.get('stage')
    if new_stage in dict(Deal.STAGE_CHOICES):
        old = deal.get_stage_display()
        deal.stage = new_stage
        deal.save()
        Activity.objects.create(
            deal=deal,
            activity_type='status_change',
            subject=f'Stage moved from {old} to {deal.get_stage_display()}',
            performed_by=request.user,
        )
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'ok': True, 'stage': new_stage})
        messages.success(request, 'Deal stage updated.')
    return redirect('deals')


@login_required
@require_POST
def deal_delete(request, pk):
    deal = get_object_or_404(Deal, pk=pk)
    deal.delete()
    messages.success(request, 'Deal deleted.')
    return redirect('deals')


# ---------- TASKS ----------
@login_required
def tasks_list(request):
    qs = Task.objects.select_related('assigned_to', 'lead', 'deal').all()
    status = request.GET.get('status', '')
    priority = request.GET.get('priority', '')
    if status:
        qs = qs.filter(status=status)
    if priority:
        qs = qs.filter(priority=priority)
    show = request.GET.get('show', 'all')
    if show == 'mine':
        qs = qs.filter(assigned_to=request.user)
    elif show == 'overdue':
        qs = qs.filter(status__in=['pending', 'in_progress'], due_date__lt=timezone.now())
    paginator = Paginator(qs, 20)
    tasks = paginator.get_page(request.GET.get('page'))
    return render(request, 'tasks.html', {
        'tasks': tasks,
        'status_choices': Task.STATUS_CHOICES,
        'priority_choices': Task.PRIORITY_CHOICES,
        'status_filter': status,
        'priority_filter': priority,
        'show': show,
    })


@login_required
def task_create(request):
    form = TaskForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        task = form.save(commit=False)
        task.created_by = request.user
        task.save()
        messages.success(request, 'Task created.')
        return redirect('tasks')
    return render(request, 'task_form.html', {'form': form, 'title': 'Add Task'})


@login_required
def task_edit(request, pk):
    task = get_object_or_404(Task, pk=pk)
    form = TaskForm(request.POST or None, instance=task)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Task updated.')
        return redirect('tasks')
    return render(request, 'task_form.html', {'form': form, 'title': 'Edit Task', 'task': task})


@login_required
@require_POST
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    task.delete()
    messages.success(request, 'Task deleted.')
    return redirect('tasks')


@login_required
@require_POST
def task_toggle(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if task.status == 'completed':
        task.status = 'pending'
    else:
        task.status = 'completed'
    task.save()
    messages.success(request, f'Task marked as {task.get_status_display()}.')
    return redirect('tasks')


# ---------- REPORTS ----------
@login_required
def reports(request):
    total_leads = Lead.objects.count()
    converted = Lead.objects.filter(status='converted').count()
    conversion_rate = round((converted / total_leads * 100), 1) if total_leads else 0

    revenue = Deal.objects.filter(stage='won').aggregate(total=Sum('value'))['total'] or 0
    won = Deal.objects.filter(stage='won').count()
    lost = Deal.objects.filter(stage='lost').count()

    # Lead sources
    sources = list(
        Lead.objects.values('source').annotate(count=Count('id')).order_by('-count')
    )
    source_labels = [dict(Lead.SOURCE_CHOICES).get(s['source'], s['source']) for s in sources]
    source_data = [s['count'] for s in sources]

    # Employee performance (leads assigned + deals won value)
    employees = User.objects.filter(is_active=True)
    emp_labels = []
    emp_leads = []
    emp_revenue = []
    for u in employees:
        emp_labels.append(u.get_full_name() or u.username)
        emp_leads.append(Lead.objects.filter(assigned_to=u).count())
        emp_revenue.append(float(
            Deal.objects.filter(assigned_to=u, stage='won').aggregate(t=Sum('value'))['t'] or 0
        ))

    # Monthly sales (won deals last 12 months)
    twelve_ago = timezone.now() - timedelta(days=365)
    monthly = (
        Deal.objects.filter(stage='won', closed_at__gte=twelve_ago)
        .annotate(month=TruncMonth('closed_at'))
        .values('month')
        .annotate(total=Sum('value'), count=Count('id'))
        .order_by('month')
    )
    month_labels = [m['month'].strftime('%b %Y') if m['month'] else '' for m in monthly]
    month_revenue = [float(m['total'] or 0) for m in monthly]
    month_count = [m['count'] for m in monthly]

    # Conversion funnel
    funnel_stages = ['new', 'contacted', 'in_progress', 'qualified', 'converted']
    funnel_labels = [dict(Lead.STATUS_CHOICES).get(s) for s in funnel_stages]
    funnel_data = [Lead.objects.filter(status=s).count() for s in funnel_stages]

    return render(request, 'reports.html', {
        'total_leads': total_leads,
        'converted': converted,
        'conversion_rate': conversion_rate,
        'revenue': revenue,
        'won': won,
        'lost': lost,
        'source_labels': json.dumps(source_labels),
        'source_data': json.dumps(source_data),
        'emp_labels': json.dumps(emp_labels),
        'emp_leads': json.dumps(emp_leads),
        'emp_revenue': json.dumps(emp_revenue),
        'month_labels': json.dumps(month_labels),
        'month_revenue': json.dumps(month_revenue),
        'month_count': json.dumps(month_count),
        'funnel_labels': json.dumps(funnel_labels),
        'funnel_data': json.dumps(funnel_data),
    })


# ---------- USERS ----------
@login_required
@user_passes_test(is_admin)
def users_list(request):
    users = User.objects.select_related('profile').all().order_by('-date_joined')
    return render(request, 'users.html', {'users': users})


@login_required
@user_passes_test(is_admin)
def user_create(request):
    form = UserCreateForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'User created successfully.')
        return redirect('users')
    return render(request, 'user_form.html', {'form': form, 'title': 'Add User'})


@login_required
@user_passes_test(is_admin)
@require_POST
def user_toggle_active(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user == request.user:
        messages.error(request, 'You cannot deactivate yourself.')
        return redirect('users')
    user.is_active = not user.is_active
    user.save()
    messages.success(request, f'User {"activated" if user.is_active else "deactivated"}.')
    return redirect('users')


@login_required
def settings_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.email = request.POST.get('email', '')
        request.user.save()
        profile.phone = request.POST.get('phone', '')
        profile.department = request.POST.get('department', '')
        profile.save()
        messages.success(request, 'Profile updated.')
        return redirect('settings')
    return render(request, 'settings.html', {'profile': profile})
