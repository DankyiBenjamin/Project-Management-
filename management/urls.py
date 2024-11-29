from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='management/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    # admin
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('create-project/', views.create_project, name='create_project'),
    path('assign-role/<int:user_id>/', views.assign_role, name='assign_role'),
    path('create-project/', views.create_project, name='create_project'),
    path('edit-project/<int:id>/', views.edit_project,
         name='edit_project'),  # Edit project URL
    path('delete-project/<int:id>/', views.delete_project,
         name='delete_project'),  # Delete project URL
    #     manager
    path('manager_dashboard/', views.manager_dashboard, name='manager_dashboard'),
    path('project/<int:id>/', views.project_detail, name='project_detail'),
    path('project/<int:project_id>/create-task/',
         views.create_task, name='create_task'),
    path('update_task/<int:task_id>/',
         views.update_task, name='update_task'),
    #     Team member
    path('team_dashboard/', views.team_dashboard, name="team_dashboard"),
    path('task/<int:task_id>/', views.task_detail, name='task_detail'),

]
