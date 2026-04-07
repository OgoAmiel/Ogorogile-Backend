from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from task_management.models import Task
from task_management.serializers.base_serializer import (TaskBaseSerializer, TaskDeleteSerializer,
                                                        TaskUpdateSerializer)
from task_management.serializers.model_serializer import TaskModelSerializer

# Create your views here.
@api_view(['POST'])
def create_task(request):
    serializer = TaskBaseSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(
            {"status": "error", "message": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    title = serializer.validated_data.get('title')
    description = serializer.validated_data.get('description')
    completed = serializer.validated_data.get('completed')

    try:
        task = Task.objects.create(
            title=title,
            description=description,
            completed=completed
        )
        return Response({
            "status": "success",
            "message": "Task created successfully",
            "data": TaskModelSerializer(task).data
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response(
            {"status": "error", "message": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['GET'])
def get_tasks(request):
    try:
        qs = Task.objects.all()
        serializer = TaskModelSerializer(qs, many=True)
        return Response({
            "status": "success",
            "message": "Tasks retrieved successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {"status": "error", "message": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['POST'])
def update_task(request):
    serializer = TaskUpdateSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(
            {"status": "error", "message": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    task_id = serializer.validated_data.get('task_id')
    title = serializer.validated_data.get('title')
    description = serializer.validated_data.get('description')
    completed = serializer.validated_data.get('completed')

    task_exists = Task.objects.filter(id=task_id).exists()
    if not task_exists:
        return Response(
            {"status": "error", "message": "Task not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    task = Task.objects.get(id=task_id)
    task.title = title
    task.description = description
    task.completed = completed
    task.save()

    return Response({
        "status": "success",
        "message": "Task updated successfully",
        "data": TaskModelSerializer(task).data
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
def delete_task(request):
    serializer = TaskDeleteSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(
            {"status": "error", "message": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    task_id = serializer.validated_data.get('task_id')

    task_exists = Task.objects.filter(id=task_id).exists()
    if not task_exists:
        return Response(
            {"status": "error", "message": "Task not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    task = Task.objects.get(id=task_id)
    task.delete()

    return Response({
        "status": "success",
        "message": "Task deleted successfully"
    }, status=status.HTTP_200_OK)