from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib import messages
from django import forms


from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import CustomUserCreationForm, ProjectForm, TaskForm, CommentForm
from django.contrib.auth.models import User, Group
from .models import Project, Task, Comment
# Create your views here.


@login_required
def home(request):
    return render(request, 'management/home.html')


def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'management/register.html', {'form': form})


# setting  permission
def is_admin(user):
    return user.groups.filter(name="Admin").exists()


def is_manager(user):
    return user.groups.filter(name="Manager").exists()


def is_team_member(user):
    return user.groups.filter(name="Team Member").exists()


# admin
@user_passes_test(is_admin)
def admin_dashboard(request):
    users = User.objects.all()
    groups = Group.objects.all()
    projects = Project.objects.all()

    # context = {
    #     'users': users,
    #     'groups': groups,
    #     'projects': projects

    # }

    return render(request, 'management/admin_dashboard.html', {'users': users,
                                                               'groups': groups,
                                                               'projects': projects})


# Assign Roles
@login_required
@user_passes_test(is_admin)
def assign_role(request, user_id):
    user = get_object_or_404(User, id=user_id)  # Fetch the user or return 404
    groups = Group.objects.all()  # Fetch all groups (roles)

    if request.method == 'POST':
        role_name = request.POST.get('role')  # Get the role from the form
        try:
            group = Group.objects.get(name=role_name)  # Find the group
            user.groups.clear()  # Clear any existing roles
            user.groups.add(group)  # Assign the new role
            # Redirect back to admin dashboard
            return redirect('admin_dashboard')
        except Group.DoesNotExist:
            # If the group name doesn't exist, show an error message
            return render(
                request,
                'assign_role.html',
                {'user': user, 'groups': groups,
                    'error': f'Role "{role_name}" not found!'},
            )

    # Render the role assignment page
    return render(request, 'management/assign_role.html', {'user': user, 'groups': groups})


@login_required
@user_passes_test(is_admin)
def create_project(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Project created successfully!")
            return redirect('admin_dashboard')
    else:
        form = ProjectForm()
        return render(request, 'management/create_project.html', {'form': form})


@login_required
@user_passes_test(is_admin)
def edit_project(request, id):
    project = get_object_or_404(Project, id=id)

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, "Project updated successfully!")
            # Redirect to the admin dashboard
            return redirect('admin_dashboard')
    else:
        form = ProjectForm(instance=project)

    return render(request, 'management/edit_project.html', {'form': form, 'project': project})


@login_required
@user_passes_test(is_admin)
def delete_project(request, id):
    project = get_object_or_404(Project, id=id)

    if request.method == 'POST':
        project.delete()
        messages.success(request, "Project deleted successfully!")
        return redirect('admin_dashboard')  # Redirect to the admin dashboard

    return render(request, 'management/confirm_delete_project.html', {'project': project})


#  manager
@user_passes_test(is_manager)
@login_required
def manager_dashboard(request):
    user = request.user  # Get the current logged-in user
    # Get projects where this user is the manager
    projects = Project.objects.filter(manager=user)

    return render(request, 'management/manager_dashboard.html', {'projects': projects})


# Create Task: Manager can create tasks for assigned projects
@user_passes_test(is_manager)
def create_task(request, project_id):
    project = Project.objects.get(id=project_id)

    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.project = project  # Link the task to the selected project
            task.save()
            # Redirect back to the manager's dashboard
            return redirect('manager_dashboard')
    else:
        form = TaskForm()

    return render(request, 'management/create_task.html', {'form': form, 'project': project})


@login_required
def update_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    # Restrict team members to only update the status
    if request.user.groups.filter(name="Team Member").exists():
        class TeamMemberTaskUpdateForm(forms.ModelForm):
            class Meta:
                model = Task
                fields = ['status']
                widgets = {
                    'status': forms.Select(attrs={'class': 'form-control'}),
                }
                labels = {
                    'status': 'Task Status',
                }
        form_class = TeamMemberTaskUpdateForm
    elif request.user.groups.filter(name="Manager").exists():
        # Managers can update all fields
        class ManagerTaskUpdateForm(forms.ModelForm):
            class Meta:
                model = Task
                fields = ['name', 'description',
                          'priority', 'status', 'deadline']
                widgets = {
                    'name': forms.TextInput(attrs={'class': 'form-control'}),
                    'description': forms.Textarea(attrs={'class': 'form-control'}),
                    'priority': forms.Select(attrs={'class': 'form-control'}),
                    'status': forms.Select(attrs={'class': 'form-control'}),
                    'deadline': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
                }
                labels = {
                    'name': 'Task Name',
                    'description': 'Task Description',
                    'priority': 'Priority',
                    'status': 'Status',
                    'deadline': 'Deadline',
                }
        form_class = ManagerTaskUpdateForm
    else:
        # If the user is not authorized, redirect
        return redirect('team_dashboard')

    # Handle form submission
    if request.method == 'POST':
        form = form_class(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('team_dashboard' if request.user.groups.filter(name="Team Member").exists() else 'manager_dashboard')
    else:
        form = form_class(instance=task)

    return render(request, 'management/update_task.html', {'form': form, 'task': task})


@login_required
def project_detail(request, id):
    project = get_object_or_404(Project, id=id)
    tasks = project.tasks.all()  # Get tasks related to the project

    return render(request, 'management/task_project_details.html', {'project': project, 'tasks': tasks})


# team members
@user_passes_test(is_team_member)
def team_dashboard(request):
    assigned_task = Task.objects.filter(assigned_to=request.user)
    print(assigned_task)
    return render(request, 'management/team_dashboard.html', {'tasks': assigned_task})

# task_details


@login_required
def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    # Allow access to the assigned team member or the manager of the project
    if task.assigned_to != request.user and task.project.manager != request.user:
        return HttpResponseForbidden("You do not have permission to view this task.")

    return render(request, 'management/task_detail.html', {'task': task})


# comments to project
def comment_to_project(request, project_id):
    project = Project.objects.get(id=project_id)
    comments = project.comments.all()
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.project = project
            comment.save()
            return redirect('comment_to_project', project_id=project.id)
    else:
        form = CommentForm()
    return render(request, 'management/comment_page.html', {'form': form, 'project': project, 'comments': comments, })


# Add comment to task
def comment_to_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    comments = task.comments.all()  # Fetch all comments related to the task

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.task = task  # Link the comment to the task
            comment.save()
            return redirect('comment_to_task', task_id=task.id)
    else:
        form = CommentForm()

    return render(request, 'management/comment_page.html', {
        'task': task,
        'comments': comments,
        'form': form
    })
