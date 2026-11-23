from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Leads
    path('leads/', views.leads_list, name='leads'),
    path('leads/add/', views.lead_create, name='lead_create'),
    path('leads/<int:pk>/', views.lead_detail, name='lead_detail'),
    path('leads/<int:pk>/edit/', views.lead_edit, name='lead_edit'),
    path('leads/<int:pk>/delete/', views.lead_delete, name='lead_delete'),
    path('leads/<int:pk>/note/', views.lead_add_note, name='lead_add_note'),
    path('leads/<int:pk>/activity/', views.lead_add_activity, name='lead_add_activity'),

    # Contacts
    path('contacts/', views.contacts_list, name='contacts'),
    path('contacts/add/', views.contact_create, name='contact_create'),
    path('contacts/<int:pk>/edit/', views.contact_edit, name='contact_edit'),
    path('contacts/<int:pk>/delete/', views.contact_delete, name='contact_delete'),

    # Deals
    path('deals/', views.deals_list, name='deals'),
    path('deals/add/', views.deal_create, name='deal_create'),
    path('deals/<int:pk>/edit/', views.deal_edit, name='deal_edit'),
    path('deals/<int:pk>/stage/', views.deal_update_stage, name='deal_update_stage'),
    path('deals/<int:pk>/delete/', views.deal_delete, name='deal_delete'),

    # Tasks
    path('tasks/', views.tasks_list, name='tasks'),
    path('tasks/add/', views.task_create, name='task_create'),
    path('tasks/<int:pk>/edit/', views.task_edit, name='task_edit'),
    path('tasks/<int:pk>/delete/', views.task_delete, name='task_delete'),
    path('tasks/<int:pk>/toggle/', views.task_toggle, name='task_toggle'),

    # Reports & Users & Settings
    path('reports/', views.reports, name='reports'),
    path('users/', views.users_list, name='users'),
    path('users/add/', views.user_create, name='user_create'),
    path('users/<int:pk>/toggle/', views.user_toggle_active, name='user_toggle'),
    path('settings/', views.settings_view, name='settings'),
]
