from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from management.models import Project, Task


class Command(BaseCommand):
    help = "Sets up roles and permissions for the app"

    def handle(self, *args, **kwargs):
        # Create groups
        admin_group, _ = Group.objects.get_or_create(name="Admin")
        manager_group, _ = Group.objects.get_or_create(name="Manager")
        team_member_group, _ = Group.objects.get_or_create(name="Team Member")

        # Get permissions
        project_ct = ContentType.objects.get_for_model(Project)
        task_ct = ContentType.objects.get_for_model(Task)

        # Admin permissions
        admin_permissions = Permission.objects.filter(
            content_type__in=[project_ct, task_ct])
        admin_group.permissions.set(admin_permissions)

        # Manager permissions
        manager_permissions = Permission.objects.filter(
            content_type__in=[project_ct, task_ct],
            codename__in=["view_project", "change_project",
                          "add_task", "change_task"]
        )
        manager_group.permissions.set(manager_permissions)

        # Team Member permissions
        team_member_permissions = Permission.objects.filter(
            content_type=task_ct, codename__in=["view_task", "change_task"]
        )
        team_member_group.permissions.set(team_member_permissions)

        self.stdout.write(self.style.SUCCESS(
            "Roles and permissions set up successfully!"))
