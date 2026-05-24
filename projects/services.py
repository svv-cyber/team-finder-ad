from projects.models import Project


def is_project_participant(project: Project, user) -> bool:
    if not user or not user.is_authenticated:
        return False
    return project.participants.filter(pk=user.pk).exists()


def add_project_participant(project: Project, user) -> bool:
    if not is_project_participant(project, user):
        project.participants.add(user)
        return True
    return False


def remove_project_participant(project: Project, user) -> bool:
    if is_project_participant(project, user):
        project.participants.remove(user)
        return True
    return False