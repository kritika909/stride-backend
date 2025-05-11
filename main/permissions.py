from rest_framework.permissions import BasePermission
from .models import WorkspaceMembership, Workflow

class IsWorkspaceAdmin(BasePermission):
    def has_permission(self, request, view):
        workspace_id = request.data.get('workspace') or view.kwargs.get('pk')
        if not workspace_id:
            return False
        try:
            return WorkspaceMembership.objects.get(user=request.user, workspace_id=workspace_id, role='manager')
        except WorkspaceMembership.DoesNotExist:
            return False
        
class IsWorkflowLead(BasePermission):
    def has_permission(self, request, view):
        workflow_id = request.data.get('workflow') or view.kwargs.get('pk')
        if not workflow_id:
            return False
        try:
            workflow = Workflow.objects.get(id=workflow_id)
            return workflow.lead == request.user
        except Workflow.DoesNotExist:
            return False
        
class IsWorkflowMember(BasePermission):
    def has_permission(self, request, view):
        workflow_id = request.data.get('workflow') or view.kwargs.get('pk')
        if not workflow_id:
            return False
        try:
            workflow = Workflow.objects.get(id=workflow_id)
            return request.user in workflow.members.all() or workflow.lead == request.user
        except Workflow.DoesNotExist:
            return False