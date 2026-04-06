from django.urls import path
from task_management.views import create_task, get_tasks

urlpatterns = [
    path("create_task/", view=create_task, name="create_task"),
    path("get_tasks/", view=get_tasks, name="get_tasks"),
]