from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from user_management.api_helpers.user_helpers import create_user_helper, update_user_helper
from user_management.models import UserRole
from user_management.serializers.base_serilaizers import CreateUserSerializer, UpdateUserSerializer, User
from user_management.serializers.model_serializers import CurrentUserSerializer, UserReadSerializer

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

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_user(request):
    serializer = CreateUserSerializer(data=request.data)

    if not serializer.is_valid():
        return Response({
            "status": "error",
            "message": serializer.errors,},
            status=status.HTTP_400_BAD_REQUEST,
        )

    username = serializer.validated_data.get("username")
    first_name = serializer.validated_data.get("first_name")
    last_name = serializer.validated_data.get("last_name")
    email = serializer.validated_data.get("email", "").strip()
    password = serializer.validated_data.get("password")
    role = serializer.validated_data.get("role")
    employee_number = serializer.validated_data.get("employee_number")
    department = serializer.validated_data.get("department", "").strip()
    manager = serializer.validated_data.get("manager")
    is_active = serializer.validated_data.get("is_active", True)

    try:
        user = create_user_helper(
            request_user=request.user,
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            role=role,
            employee_number=employee_number,
            department=department,
            manager=manager,
            is_active=is_active,
        )

        return Response({
            "status": "success",
            "message": "User created successfully",
            "data": UserReadSerializer(user).data,},
            status=status.HTTP_201_CREATED,
        )
    except Exception as e:
        return Response({
            "status": "error",
            "message": str(e),},
            status=status.HTTP_400_BAD_REQUEST,
        )

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_users(request):
    if request.user.role != UserRole.ADMIN:
        return Response({
            "status": "error",
            "message": ["Only admins can view users."],
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    users = User.objects.select_related("manager").all()
    serializer = UserReadSerializer(users, many=True)

    return Response({
        "status": "success",
        "message": "Users retrieved successfully",
        "data": serializer.data,},
        status=status.HTTP_200_OK,)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def update_user(request):
    serializer = UpdateUserSerializer(data=request.data)

    if not serializer.is_valid():
        return Response({
            "status": "error",
            "message": serializer.errors,},
            status=status.HTTP_400_BAD_REQUEST,)

    target_user = serializer.validated_data.get("target_user")
    first_name = serializer.validated_data.get("first_name")
    last_name = serializer.validated_data.get("last_name")
    email = serializer.validated_data.get("email", "")
    role = serializer.validated_data.get("role")
    employee_number = serializer.validated_data.get("employee_number")
    department = serializer.validated_data.get("department", "").strip()
    manager = serializer.validated_data.get("manager")
    is_active = serializer.validated_data.get("is_active", target_user.is_active)

    try:
        updated_user = update_user_helper(
            request_user=request.user,
            target_user=target_user,
            first_name=first_name,
            last_name=last_name,
            email=email,
            role=role,
            employee_number=employee_number,
            department=department,
            manager=manager,
            is_active=is_active,
        )

        return Response({
            "status": "success",
            "message": "User updated successfully",
            "data": UserReadSerializer(updated_user).data,},
            status=status.HTTP_200_OK,
            )
    except Exception as e:
        return Response({
            "status": "error",
            "message": str(e),},
            status=status.HTTP_400_BAD_REQUEST,)