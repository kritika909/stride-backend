from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WorkflowViewset, WorkspaceViewset, MeetingViewset, TaskViewset

router = DefaultRouter()

router.register(r'workspace', WorkspaceViewset, basename='workspace')
router.register(r'workflow', WorkflowViewset, basename='workflow')
router.register(r'task', TaskViewset, basename='task')
router.register(r'meeting', MeetingViewset, basename='meeting')

urlpatterns = router.urls