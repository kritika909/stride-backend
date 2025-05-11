from django.shortcuts import render
from .permissions import IsWorkflowLead, IsWorkflowMember, IsWorkspaceAdmin
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from .serializers import WorkflowSerializer, WorkspaceMembershipSerializer, WorkspaceSerializer, TaskSerializer, MeetingSerializer
from .models import Workflow, Workspace, WorkspaceMembership, Task, Meeting

from googleapiclient.discovery import build
from google.oauth2 import service_account
from datetime import timedelta

SCOPES = ['https://www.googleapis.com/auth.calender']
SERVICE_ACCOUNT_FILE = 'service_acc/manifest-grin-456713-g5-1ec0d361fcda.json'
CALENDAR_ID = 'primary'

def create_google_meet_event(title, description, start_time, attendees_emails):
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    service = build('calendar', 'v3', credentials=credentials)

    event = {
        'summary': title,
        'description': description,
        'start': {'dateTime': start_time.isoformat(), 'timeZone': 'UTC'},
        'end': {'dateTime': (start_time + timedelta(hours=1)).isoformat(), 'timeZone': 'UTC'},
        'attendees': [{'email': email} for email in attendees_emails],
        'conferenceData': {
            'createRequest': {
                'requestId': f"{title}-{start_time.isoformat()}",
                'conferenceSolutionKey': {'type': 'hangoutsMeet'},
            }
        }
    }

    created_event = service.events().insert(
        calendarId=CALENDAR_ID,
        body=event,
        conferenceDataVersion=1
    ).execute()

    return created_event.get('hangoutLink')


# Create your views here.
class WorkspaceViewset(viewsets.ModelViewSet):
    queryset = Workspace.objects.all()
    serializer_class = WorkspaceSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        workspace = serializer.save(owner=self.request.user)
        WorkspaceMembership.objects.create(user=self.request.user, workspace=workspace, role='manager')

    @action(detail=True, methods=['post'], url_path='add-member', permission_classes=[IsAuthenticated, IsWorkspaceAdmin])
    def add_memeber(self, request, pk=None):
        workspace = self.get_object()
        user_id = request.data.get('user_id')
        role = request.data.get('role')

        if not user_id or not role:
            return Response({'detail': 'user_id and role required'}, status=status.HTTP_400_BAD_REQUEST)
        
        WorkspaceMembership.objects.create(user_id=user_id, workspace=workspace, role=role)

        return Response({'detail': 'member added successfully'})
    
class WorkflowViewset(viewsets.ModelViewSet):
    queryset = Workflow.objects.all()
    serializer_class = WorkflowSerializer
    permission_classes = [IsAuthenticated, IsWorkspaceAdmin]

    def perform_create(self, serializer):
        workflow = serializer.save()

    @action(detail=True, methods=['post'], url_path='add-menber', permission_classes=[IsAuthenticated, IsWorkflowLead])
    def add_member(self, request, pk=None):
        workflow = self.get_object()
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'detail': 'user id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.get(id=user_id)
        workflow.members.add(user)
        return Response({'detail': 'member added'})
    
class TaskViewset(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsWorkflowLead]

    def perform_create(self, serializer):
        workflow = serializer.validated_data['workflow']
        assignee = serializer.validated_data.get('assignee')
        if assignee and assignee not in workflow.member.all():
            raise serializer.ValidationError("Assignee must be a workflow member")
        serializer.save()

class MeetingViewset(viewsets.ModelViewSet):
    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer
    permission_classes = [IsAuthenticated, IsWorkflowLead]

    def perform_create(self, serializer):
        meeting = serializer.save()
        attendees = meeting.attendees.all()
        attendee_emails = [user.email for user in attendees]

        meet_link = create_google_meet_event(
            title = meeting.title,
            description = meeting.agenda,
            start_time= meeting.datetime,
            attendees_emails = attendee_emails
        )

        meeting.meet_link = meet_link
        meeting.save()
    



