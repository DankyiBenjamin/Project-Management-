from django.db import models

# Create your models here.
from django.contrib.auth.models import User

# Project Model


class Project(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateField()
    deadline = models.DateField()
    manager = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='projects')

    # Related tasks
    # tasks = models.ManyToManyField('Task', related_name='project_tasks')

    @property
    def progress(self):
        total_tasks = self.tasks.count()
        if total_tasks == 0:
            return 0
        completed_tasks = self.tasks.filter(status='completed').count()
        return int((completed_tasks / total_tasks) * 100)

    def __str__(self):
        return self.name


# Task model

class Task(models.Model):
    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]
    STATUS_CHOICES = [
        ('Not Started', 'Not Started'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    ]

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name='tasks')
    name = models.CharField(max_length=255)
    description = models.TextField()
    assigned_to = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='assigned_tasks')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='Not Started')
    deadline = models.DateField()

    def __str__(self):
        return self.name


# Comment Model
class Comment(models.Model):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name='comments', null=True, blank=True)
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, related_name='comments', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.created_at}"


# Notification Model
class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('Task Assigned', 'Task Assigned'),
        ('Deadline Approaching', 'Deadline Approaching'),
        ('Comment Added', 'Comment Added'),
        ('Task Updated', 'Task Updated'),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='notifications')
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    task = models.ForeignKey(Task, on_delete=models.CASCADE,
                             null=True, blank=True, related_name='notifications')
    notification_type = models.CharField(
        max_length=50, choices=NOTIFICATION_TYPES)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.notification_type} for {self.user.username}"


# defining roles
