from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Project, Task

# custom user form


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class ProjectForm(forms.ModelForm):

    # custom field

    manager = forms.ModelChoiceField(
        queryset=User.objects.filter(groups__name="Manager"),
        empty_label="Select a Manager",
        required=True
    )

    class Meta:
        model = Project
        fields = ['name', 'description', 'start_date', 'deadline', 'manager']

        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'deadline': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'name': 'Project Name',
            'description': 'Project Description',
            'start_date': 'Start Date',
            'deadline': 'Deadline',
            'manager': 'Manager',
        }


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['name', 'description', 'assigned_to',
                  'priority', 'status', 'deadline', 'project']

    assigned_to = forms.ModelChoiceField(
        queryset=User.objects.filter(groups__name="Team Member"),
        empty_label="Select a Team Member",
        required=True
    )
    priority = forms.ChoiceField(choices=Task.PRIORITY_CHOICES)
    status = forms.ChoiceField(choices=Task.STATUS_CHOICES)
    project = forms.ModelChoiceField(
        queryset=Project.objects.all(), required=True)
    deadline = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
