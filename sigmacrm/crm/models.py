from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator
from decimal import Decimal


class Profile(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('employee', 'Employee'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employee')
    phone = models.CharField(max_length=20, blank=True)
    department = models.CharField(max_length=100, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.role})"

    @property
    def is_admin(self):
        return self.role == 'admin' or self.user.is_superuser


class Lead(models.Model):
    STATUS_CHOICES = (
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('in_progress', 'In Progress'),
        ('qualified', 'Qualified'),
        ('converted', 'Converted'),
        ('lost', 'Lost'),
    )
    SOURCE_CHOICES = (
        ('website', 'Website'),
        ('referral', 'Referral'),
        ('social', 'Social Media'),
        ('email', 'Email Campaign'),
        ('cold_call', 'Cold Call'),
        ('event', 'Event'),
        ('other', 'Other'),
    )

    full_name = models.CharField(max_length=200)
    company = models.CharField(max_length=200, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    industry = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=200, blank=True)
    source = models.CharField(max_length=50, choices=SOURCE_CHOICES, default='website')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    assigned_to = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_leads'
    )
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='created_leads'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['source']),
            models.Index(fields=['assigned_to']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return self.full_name


class Contact(models.Model):
    full_name = models.CharField(max_length=200)
    company = models.CharField(max_length=200, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    job_title = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=200, blank=True)
    lead = models.ForeignKey(
        Lead, on_delete=models.SET_NULL, null=True, blank=True, related_name='contacts'
    )
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='created_contacts'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.full_name


class Deal(models.Model):
    STAGE_CHOICES = (
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('proposal', 'Proposal'),
        ('negotiation', 'Negotiation'),
        ('won', 'Won'),
        ('lost', 'Lost'),
    )

    title = models.CharField(max_length=200)
    lead = models.ForeignKey(
        Lead, on_delete=models.SET_NULL, null=True, blank=True, related_name='deals'
    )
    contact = models.ForeignKey(
        Contact, on_delete=models.SET_NULL, null=True, blank=True, related_name='deals'
    )
    value = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES, default='new')
    expected_close_date = models.DateField(null=True, blank=True)
    assigned_to = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_deals'
    )
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='created_deals'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['stage']),
            models.Index(fields=['assigned_to']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.title} (${self.value})"

    def save(self, *args, **kwargs):
        if self.stage in ('won', 'lost') and not self.closed_at:
            self.closed_at = timezone.now()
        elif self.stage not in ('won', 'lost'):
            self.closed_at = None
        super().save(*args, **kwargs)


class Task(models.Model):
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    )
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    assigned_to = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks'
    )
    lead = models.ForeignKey(
        Lead, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks'
    )
    deal = models.ForeignKey(
        Deal, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks'
    )
    due_date = models.DateTimeField(null=True, blank=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='created_tasks'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['due_date', '-priority']

    def __str__(self):
        return self.title

    @property
    def is_overdue(self):
        if self.status != 'completed' and self.due_date:
            return timezone.now() > self.due_date
        return False

    def save(self, *args, **kwargs):
        if self.status == 'completed' and not self.completed_at:
            self.completed_at = timezone.now()
        elif self.status != 'completed':
            self.completed_at = None
        super().save(*args, **kwargs)


class Activity(models.Model):
    TYPE_CHOICES = (
        ('call', 'Call'),
        ('email', 'Email'),
        ('meeting', 'Meeting'),
        ('note', 'Note'),
        ('task', 'Task'),
        ('status_change', 'Status Change'),
        ('other', 'Other'),
    )

    lead = models.ForeignKey(
        Lead, on_delete=models.CASCADE, null=True, blank=True, related_name='activities'
    )
    deal = models.ForeignKey(
        Deal, on_delete=models.CASCADE, null=True, blank=True, related_name='activities'
    )
    contact = models.ForeignKey(
        Contact, on_delete=models.CASCADE, null=True, blank=True, related_name='activities'
    )
    activity_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='note')
    subject = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    performed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='activities'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'activities'

    def __str__(self):
        return f"{self.activity_type}: {self.subject}"


class Note(models.Model):
    lead = models.ForeignKey(
        Lead, on_delete=models.CASCADE, null=True, blank=True, related_name='lead_notes'
    )
    deal = models.ForeignKey(
        Deal, on_delete=models.CASCADE, null=True, blank=True, related_name='deal_notes'
    )
    contact = models.ForeignKey(
        Contact, on_delete=models.CASCADE, null=True, blank=True, related_name='contact_notes'
    )
    content = models.TextField()
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='notes'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Note by {self.created_by} at {self.created_at}"
