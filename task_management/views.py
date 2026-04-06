from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from task_management.models import Task
from task_management.serializers.base_serializer import TaskBaseSerializer
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

    validated_data = serializer.validated_data

    try:
        task = Task.objects.create(
            title=validated_data['title'],
            description=validated_data['description'],
            completed=validated_data['completed']
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