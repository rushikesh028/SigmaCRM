from django.contrib.auth.models import User
from crm.models import Profile, Lead, Contact, Deal, Task, Activity
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import random

if not User.objects.filter(username='admin').exists():
    u = User.objects.create_superuser('admin', 'admin@sigmacrm.com', 'admin123')
    u.first_name, u.last_name = 'Admin', 'User'
    u.save()
    Profile.objects.update_or_create(user=u, defaults={'role': 'admin', 'department': 'Management'})
    print('Created admin / admin123')

if not User.objects.filter(username='employee').exists():
    e = User.objects.create_user('employee', 'employee@sigmacrm.com', 'employee123')
    e.first_name, e.last_name = 'Sarah', 'Johnson'
    e.save()
    Profile.objects.update_or_create(user=e, defaults={'role': 'employee', 'department': 'Sales'})
    print('Created employee / employee123')

admin = User.objects.get(username='admin')
emp = User.objects.filter(username='employee').first() or admin
sources = ['website', 'referral', 'social', 'email', 'cold_call', 'event']
statuses = ['new', 'contacted', 'in_progress', 'qualified', 'converted', 'lost']
industries = ['Technology', 'Healthcare', 'Finance', 'Retail', 'Manufacturing']
names = [
    ('John Smith', 'Acme Corp'), ('Emily Davis', 'TechNova'), ('Michael Brown', 'GlobalSoft'),
    ('Jessica Wilson', 'HealthPlus'), ('David Martinez', 'FinanceFirst'), ('Amanda Taylor', 'RetailMax'),
    ('Chris Anderson', 'BuildRight'), ('Lauren Thomas', 'EduLearn'), ('James Jackson', 'CloudNine'),
    ('Megan White', 'DataDrive'),
]

if Lead.objects.count() == 0:
    for i, (name, company) in enumerate(names):
        lead = Lead.objects.create(
            full_name=name, company=company,
            email=name.lower().replace(' ', '.') + '@example.com',
            phone=f'+1-555-{1000+i:04d}',
            industry=random.choice(industries),
            location=random.choice(['New York', 'San Francisco', 'Chicago', 'Austin']),
            source=random.choice(sources), status=random.choice(statuses),
            assigned_to=random.choice([admin, emp]), created_by=admin,
            notes=f'Initial contact with {name}',
        )
        Lead.objects.filter(pk=lead.pk).update(created_at=timezone.now() - timedelta(days=random.randint(0, 25)))
        Activity.objects.create(lead=lead, activity_type='note', subject='Lead created', performed_by=admin)
    for lead in Lead.objects.filter(status='converted')[:2]:
        Contact.objects.create(full_name=lead.full_name, company=lead.company, email=lead.email, lead=lead, created_by=admin)
    stages = ['new', 'in_progress', 'proposal', 'negotiation', 'won', 'lost']
    for i, lead in enumerate(Lead.objects.all()[:8]):
        Deal.objects.create(
            title=f'{lead.company} - Deal', lead=lead,
            value=Decimal(random.randint(5000, 120000)),
            stage=stages[i % len(stages)],
            expected_close_date=(timezone.now() + timedelta(days=random.randint(10, 60))).date(),
            assigned_to=lead.assigned_to, created_by=admin,
        )
    for i in range(6):
        Task.objects.create(
            title=f'Follow-up task #{i+1}', assigned_to=random.choice([admin, emp]),
            lead=random.choice(list(Lead.objects.all()[:5])),
            due_date=timezone.now() + timedelta(days=random.randint(-2, 10)),
            priority=random.choice(['low', 'medium', 'high']), status='pending', created_by=admin,
        )
    print('Sample data created')
else:
    print('Data already exists')
