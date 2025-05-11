from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Workspace(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_workspaces')
    members = models.ManyToManyField(User, through='WorkspaceMembership', related_name='workspaces')

    def __str__(self):
        return self.name

class WorkspaceMembership(models.Model):
    ROLE_CHOICES = (
        ('manager', 'Manager'),
        ('lead', 'Lead'),
        ('contributor', 'Contributor'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    class Meta:
        unique_together = ('user', 'workspace')

class Workflow(models.Model):
    name = models.CharField(max_length=100)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='workflows')
    lead = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='led_workflows')
    members = models.ManyToManyField(User, related_name='workflow_memberships')

    def __str__(self):
        return self.name

class Task(models.Model):
    STATUS_CHOICES = (
        ('todo', 'To-Do'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    )
    title = models.CharField(max_length=100)
    description = models.TextField()
    due_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name='tasks')
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')

    def __str__(self):
        return self.title

class Meeting(models.Model):
    title = models.CharField(max_length=100)
    datetime = models.DateTimeField()
    agenda = models.TextField()
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name='meetings')
    attendees = models.ManyToManyField(User, related_name='meetings')
    meet_link = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.title


