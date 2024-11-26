from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages


from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import CustomUserCreationForm, ProjectForm, TaskForm
from django.contrib.auth.models import User, Group
from .models import Project, Task
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


@user_passes_test(is_manager)
def update_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            # Redirect back to the manager's dashboard
            return redirect('manager_dashboard')
    else:
        form = TaskForm(instance=task)

    return render(request, 'management/update_task.html', {'form': form, 'task': task})


def project_detail(request, id):
    project = get_object_or_404(Project, id=id)
    tasks = project.tasks.all()  # Get tasks related to the project

    return render(request, 'management/task_project_details.html', {'project': project, 'tasks': tasks})


# team members
def team_member_dashboard(request):
    context = ""
    return render(request, 'management/team_member_dashboard.html', {'context': context})
