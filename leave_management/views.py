from django.shortcuts import render
from django.core.exceptions import ValidationError as DjangoValidationError
from leave_management.api_helpers.leave_helpers import (approve_leave_request_helper, create_leave_request_helper,
                                                        cancel_leave_request_helper, create_leave_type_helper,get_pending_leave_requests_helper,
                                                        reject_leave_request_helper, update_leave_type_helper)
from leave_management.models import LeaveBalance, LeaveRequest, LeaveRequestStatus, LeaveType
from leave_management.serializers.model_serializer import LeaveBalanceSerializer, LeaveRequestListSerializer, LeaveTypeAdminSerializer
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


from leave_management.serializers.base_serializer import (ApproveLeaveRequestSerializer, CancelLeaveRequestSerializer, CreateLeaveTypeSerializer, DeleteLeaveTypeSerializer,
                                                        LeaveRequestCreateSerializer, RejectLeaveRequestSerializer, UpdateLeaveTypeSerializer)
from user_management.models import UserRole

# Create your views here.
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_leave_request(request):
    serializer = LeaveRequestCreateSerializer(data=request.data)

    if not serializer.is_valid():
        return Response({
            "status": "error",
            "message": serializer.errors,},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        leave_request = create_leave_request_helper(
            user=request.user,
            validated_data=serializer.validated_data,
        )

        return Response({
            "status": "success",
            "message": "Leave request created successfully",
            "data": LeaveRequestListSerializer(leave_request, context={"request": request}).data,},
            status=status.HTTP_201_CREATED,
        )

    except Exception as e:
        return Response({
            "status": "error",
            "message": str(e),},
            status=status.HTTP_400_BAD_REQUEST,)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_leave_requests(request):
    try:
        leave_requests = LeaveRequest.objects.filter(
            employee=request.user
            ).select_related("employee", "leave_type", "approved_by", "rejected_by")

        serializer = LeaveRequestListSerializer(leave_requests, many=True, context={"request": request})
        return Response({
            "status": "success",
            "message": "Leave requests retrieved successfully",
            "data": serializer.data,},
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return Response({
            "status": "error",
            "message": str(e),},
            status=status.HTTP_400_BAD_REQUEST,)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_leave_balances(request):
    try:
        leave_balances = LeaveBalance.objects.filter(
            employee=request.user
            ).select_related("leave_type")

        serializer = LeaveBalanceSerializer(leave_balances, many=True)
        return Response({
            "status": "success",
            "message": "Leave balances retrieved successfully",
            "data": serializer.data,},
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return Response({
            "status": "error",
            "message": str(e),},
            status=status.HTTP_400_BAD_REQUEST,)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def cancel_leave_request(request):
    serializer = CancelLeaveRequestSerializer(data=request.data)

    if not serializer.is_valid():
        return Response({
            "status": "error",
            "message": serializer.errors,},
            status=status.HTTP_400_BAD_REQUEST,
        )

    leave_request_id = serializer.validated_data.get("leave_request_id")
    cancellation_reason = serializer.validated_data.get("cancellation_reason", "")

    try:
        leave_request = cancel_leave_request_helper(
            user=request.user,
            leave_request_id=leave_request_id,
            cancellation_reason=cancellation_reason,
        )

        return Response({
            "status": "success",
            "message": "Leave request cancelled successfully",
            "data": LeaveRequestListSerializer(leave_request).data,},
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        return Response({
            "status": "error",
            "message": str(e),},
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_pending_leave_requests(request):
    try:
        pending_requests = get_pending_leave_requests_helper(request.user)
        serializer = LeaveRequestListSerializer(pending_requests, many=True, context={"request": request})

        return Response({
            "status": "success",
            "message": "Pending leave requests retrieved successfully",
            "data": serializer.data,},
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        return Response({
            "status": "error",
            "message": str(e),},
            status=status.HTTP_400_BAD_REQUEST,
        )

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def approve_leave_request(request):
    serializer = ApproveLeaveRequestSerializer(data=request.data)

    if not serializer.is_valid():
        return Response({
            "status": "error",
            "message": serializer.errors,},
            status=status.HTTP_400_BAD_REQUEST,
        )

    leave_request_id = serializer.validated_data.get("leave_request_id")

    try:
        leave_request = approve_leave_request_helper(
            user=request.user,
            leave_request_id=leave_request_id,
        )

        return Response({
            "status": "success",
            "message": "Leave request approved successfully",
            "data": LeaveRequestListSerializer(leave_request, context={"request": request}).data,},
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return Response({
            "status": "error",
            "message": str(e),},
            status=status.HTTP_400_BAD_REQUEST,)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def reject_leave_request(request):
    serializer = RejectLeaveRequestSerializer(data=request.data)

    if not serializer.is_valid():
        return Response({
            "status": "error",
            "message": serializer.errors,},
            status=status.HTTP_400_BAD_REQUEST,
        )

    leave_request_id = serializer.validated_data.get("leave_request_id")
    rejection_reason = serializer.validated_data.get("rejection_reason")

    try:
        leave_request = reject_leave_request_helper(
            user=request.user,
            leave_request_id=leave_request_id,
            rejection_reason=rejection_reason,
        )

        return Response({
            "status": "success",
            "message": "Leave request rejected successfully",
            "data": LeaveRequestListSerializer(leave_request, context={"request": request}).data,},
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return Response({
            "status": "error",
            "message": str(e),},
            status=status.HTTP_400_BAD_REQUEST,
        )

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_approved_leave_requests(request):
    try:
        approved_requests = LeaveRequest.objects.filter(
            employee__manager=request.user,
            status=LeaveRequestStatus.APPROVED,
        ).select_related(
            "employee",
            "leave_type",
            "approved_by",
        )

        serializer = LeaveRequestListSerializer(approved_requests, many=True, context={"request": request})
        return Response({
            "status": "success",
            "message": "Approved leave requests retrieved successfully",
            "data": serializer.data,},
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return Response({
            "status": "error",
            "message": str(e),},
            status=status.HTTP_400_BAD_REQUEST,
        )

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_rejected_leave_requests(request):
    try:
        rejected_requests = LeaveRequest.objects.filter(
            employee__manager=request.user,
            status=LeaveRequestStatus.REJECTED,
        ).select_related(
            "employee",
            "leave_type",
            "rejected_by",
        )

        serializer = LeaveRequestListSerializer(rejected_requests, many=True, context={"request": request})
        return Response({
            "status": "success",
            "message": "Rejected leave requests retrieved successfully",
            "data": serializer.data,},
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return Response({
            "status": "error",
            "message": str(e),},
            status=status.HTTP_400_BAD_REQUEST,
        )

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_leave_types(request):
    if request.user.role != UserRole.ADMIN:
        return Response({
            "status": "error",
            "message": ["Only admins can view leave types."],
            },status=status.HTTP_403_FORBIDDEN,)

    leave_types = LeaveType.objects.all()
    serializer = LeaveTypeAdminSerializer(leave_types, many=True)

    return Response({
        "status": "success",
        "message": "Leave types retrieved successfully",
        "data": serializer.data,
        },status=status.HTTP_200_OK,)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_leave_type(request):
    serializer = CreateLeaveTypeSerializer(data=request.data)

    if not serializer.is_valid():
        return Response({
            "status": "error",
            "message": serializer.errors,
            },status=status.HTTP_400_BAD_REQUEST,)

    name = serializer.validated_data.get("name")
    default_days = serializer.validated_data.get("default_days")
    requires_attachment = serializer.validated_data.get("requires_attachment", False)
    is_active = serializer.validated_data.get("is_active", True)

    try:
        leave_type = create_leave_type_helper(
            request_user=request.user,
            name=name,
            default_days=default_days,
            requires_attachment=requires_attachment,
            is_active=is_active,
        )

        return Response({
            "status": "success",
            "message": "Leave type created successfully",
            "data": LeaveTypeAdminSerializer(leave_type).data,
            },status=status.HTTP_201_CREATED,
            )
    except Exception as e:
        return Response({
            "status": "error",
            "message": str(e),},
            status=status.HTTP_400_BAD_REQUEST,)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def update_leave_type(request):
    serializer = UpdateLeaveTypeSerializer(data=request.data)

    if not serializer.is_valid():
        return Response({
            "status": "error",
            "message": serializer.errors,
            },status=status.HTTP_400_BAD_REQUEST,)

    target_leave_type = serializer.validated_data.get("target_leave_type")
    name = serializer.validated_data.get("name")
    default_days = serializer.validated_data.get("default_days")
    requires_attachment = serializer.validated_data.get("requires_attachment", target_leave_type.requires_attachment)
    is_active = serializer.validated_data.get("is_active", target_leave_type.is_active)

    try:
        leave_type = update_leave_type_helper(
            request_user=request.user,
            target_leave_type=target_leave_type,
            name=name,
            default_days=default_days,
            requires_attachment=requires_attachment,
            is_active=is_active,
        )

        return Response(
            {
                "status": "success",
                "message": "Leave type updated successfully",
                "data": LeaveTypeAdminSerializer(leave_type).data,
            },
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return Response({
            "status": "error",
            "message": str(e),},
            status=status.HTTP_400_BAD_REQUEST,)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def delete_leave_type(request):
    serializer = DeleteLeaveTypeSerializer(data=request.data)

    if not serializer.is_valid():
        return Response({
            "status": "error",
            "message": serializer.errors,
            },status=status.HTTP_400_BAD_REQUEST,)

    leave_type_id = serializer.validated_data.get("leave_type_id")

    leave_type_exists = LeaveType.objects.filter(id=leave_type_id).exists()
    if not leave_type_exists:
        return Response({
            "status": "error",
            "message": "Selected leave type does not exist.",
            },status=status.HTTP_400_BAD_REQUEST,)

    try:
        leave_type = LeaveType.objects.get(id=leave_type_id)
        leave_type.delete()

        return Response({
            "status": "success",
            "message": "Leave type deleted successfully",
            },status=status.HTTP_200_OK,
            )
    except Exception as e:
        return Response({
            "status": "error",
            "message": str(e),
            },status=status.HTTP_400_BAD_REQUEST,)