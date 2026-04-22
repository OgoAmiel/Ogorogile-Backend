from django.shortcuts import render
from django.core.exceptions import ValidationError as DjangoValidationError
from leave_management.api_helpers.leave_helpers import (approve_leave_request_helper, create_leave_request_helper,
                                                        cancel_leave_request_helper,get_pending_leave_requests_helper,
                                                        reject_leave_request_helper)
from leave_management.models import LeaveBalance, LeaveRequest, LeaveRequestStatus
from leave_management.serializers.model_serializer import LeaveBalanceSerializer, LeaveRequestListSerializer
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


from leave_management.serializers.base_serializer import (ApproveLeaveRequestSerializer, CancelLeaveRequestSerializer,
                                                        LeaveRequestCreateSerializer, RejectLeaveRequestSerializer)

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
            "data": LeaveRequestListSerializer(leave_request).data,},
            status=status.HTTP_201_CREATED,
        )

    except DjangoValidationError as error:
        return Response({
            "status": "error",
            "message": error.message_dict if hasattr(error, "message_dict") else error.messages,},
            status=status.HTTP_400_BAD_REQUEST,)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_leave_requests(request):
    try:
        leave_requests = LeaveRequest.objects.filter(
            employee=request.user
            ).select_related("employee", "leave_type", "approved_by", "rejected_by")

        serializer = LeaveRequestListSerializer(leave_requests, many=True)
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

    except DjangoValidationError as error:
        return Response({
            "status": "error",
            "message": error.message_dict if hasattr(error, "message_dict") else error.messages,},
            status=status.HTTP_400_BAD_REQUEST,)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_pending_leave_requests(request):
    try:
        pending_requests = get_pending_leave_requests_helper(request.user)
        serializer = LeaveRequestListSerializer(pending_requests, many=True)

        return Response({
            "status": "success",
            "message": "Pending leave requests retrieved successfully",
            "data": serializer.data,},
            status=status.HTTP_200_OK,
        )

    except DjangoValidationError as error:
        return Response({
            "status": "error",
            "message": error.message_dict if hasattr(error, "message_dict") else error.messages,},
            status=status.HTTP_400_BAD_REQUEST,)

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
            "data": LeaveRequestListSerializer(leave_request).data,},
            status=status.HTTP_200_OK,
        )
    except DjangoValidationError as error:
        return Response({
            "status": "error",
            "message": error.message_dict if hasattr(error, "message_dict") else error.messages,},
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
            "data": LeaveRequestListSerializer(leave_request).data,},
            status=status.HTTP_200_OK,
        )
    except DjangoValidationError as error:
        return Response({
            "status": "error",
            "message": error.message_dict if hasattr(error, "message_dict") else error.messages,},
            status=status.HTTP_400_BAD_REQUEST,)

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

        serializer = LeaveRequestListSerializer(approved_requests, many=True)
        return Response({
            "status": "success",
            "message": "Approved leave requests retrieved successfully",
            "data": serializer.data,},
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return Response({
            "status": "error",
            "message": str(e)},
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

        serializer = LeaveRequestListSerializer(rejected_requests, many=True)
        return Response({
            "status": "success",
            "message": "Rejected leave requests retrieved successfully",
            "data": serializer.data,},
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return Response({
            "status": "error",
            "message": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )