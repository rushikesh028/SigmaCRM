from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from .models import Lead, Contact, Deal, Task, Activity, Note, Profile


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control form-control-lg',
        'placeholder': 'Username',
        'autocomplete': 'username',
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control form-control-lg',
        'placeholder': 'Password',
        'autocomplete': 'current-password',
    }))


class LeadForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = [
            'full_name', 'company', 'email', 'phone', 'industry',
            'location', 'source', 'status', 'assigned_to', 'notes'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'company': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone'}),
            'industry': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Industry'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Location'}),
            'source': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Notes'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_to'].queryset = User.objects.filter(is_active=True).order_by('username')
        self.fields['assigned_to'].required = False


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = [
            'full_name', 'company', 'email', 'phone', 'job_title',
            'location', 'lead', 'notes'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'company': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'job_title': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'lead': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['lead'].queryset = Lead.objects.all().order_by('full_name')
        self.fields['lead'].required = False


class DealForm(forms.ModelForm):
    class Meta:
        model = Deal
        fields = [
            'title', 'lead', 'contact', 'value', 'stage',
            'expected_close_date', 'assigned_to', 'description'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'lead': forms.Select(attrs={'class': 'form-select'}),
            'contact': forms.Select(attrs={'class': 'form-select'}),
            'value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'stage': forms.Select(attrs={'class': 'form-select'}),
            'expected_close_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['lead'].queryset = Lead.objects.all().order_by('full_name')
        self.fields['contact'].queryset = Contact.objects.all().order_by('full_name')
        self.fields['assigned_to'].queryset = User.objects.filter(is_active=True)
        self.fields['lead'].required = False
        self.fields['contact'].required = False
        self.fields['assigned_to'].required = False


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            'title', 'description', 'assigned_to', 'lead', 'deal',
            'due_date', 'priority', 'status'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'lead': forms.Select(attrs={'class': 'form-select'}),
            'deal': forms.Select(attrs={'class': 'form-select'}),
            'due_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_to'].queryset = User.objects.filter(is_active=True)
        self.fields['lead'].queryset = Lead.objects.all()
        self.fields['deal'].queryset = Deal.objects.all()
        for f in ['assigned_to', 'lead', 'deal', 'due_date']:
            self.fields[f].required = False


class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ['activity_type', 'subject', 'description']
        widgets = {
            'activity_type': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Add a note...'}),
        }


class UserCreateForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    role = forms.ChoiceField(choices=Profile.ROLE_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    phone = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    department = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in ['username', 'password1', 'password2']:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        if commit:
            user.save()
            Profile.objects.update_or_create(
                user=user,
                defaults={
                    'role': self.cleaned_data['role'],
                    'phone': self.cleaned_data.get('phone', ''),
                    'department': self.cleaned_data.get('department', ''),
                }
            )
        return user
