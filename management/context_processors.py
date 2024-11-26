from django.contrib.auth.models import Group


def base_context(request):
    """Adds group membership checks to the context."""
    if request.user.is_authenticated:
        return {
            'is_admin': request.user.groups.filter(name="Admin").exists(),
            'is_manager': request.user.groups.filter(name="Manager").exists(),
            'is_team_member': request.user.groups.filter(name="Team Member").exists(),
        }
    return {
        'is_admin': False,
        'is_manager': False,
        'is_team_member': False,
    }
