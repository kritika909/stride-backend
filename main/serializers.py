from rest_framework import serializers
from .models import Workspace, WorkspaceMembership, Workflow, Task, Meeting

class WorkspaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workspace
        fields = '__all__'

class WorkspaceMembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkspaceMembership
        fields = '__all__'

class WorkflowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workflow
        fields = '__all__'

    def validate(self, data):
        workspace = data.get("workspace")
        lead = data.get("lead")

        if lead not in workspace.members.all():
            raise serializers.ValidationError("The lead must be a member of the workspace.")
        return data

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'

class MeetingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields = '__all__'