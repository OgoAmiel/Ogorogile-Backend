from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from user_management.serializers.model_serializers import CurrentUserSerializer

# Create your views here.
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user(request):
    serializer = CurrentUserSerializer(request.user)

    return Response({
        "status": "success",
        "message": "Current user retrieved successfully",
        "data": serializer.data,},
        status=status.HTTP_200_OK,)