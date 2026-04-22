from django.core.exceptions import ValidationError
from django.db import transaction
from datetime import date
from django.utils import timezone

from leave_management.models import LeaveBalance, LeaveRequest, LeaveRequestStatus, LeaveType
from leave_management.serializers.base_serializer import LeaveRequestCreateSerializer
from user_management.models import UserRole


@transaction.atomic
def create_leave_request_helper(user, validated_data):
    leave_type_id = validated_data["leave_type_id"]
    start_date = validated_data["start_date"]
    end_date = validated_data["end_date"]
    reason = validated_data.get("reason", "")
    attachment = validated_data.get("attachment")

    try:
        leave_type = LeaveType.objects.get(id=leave_type_id, is_active=True)
    except LeaveType.DoesNotExist:
        raise ValidationError("Selected leave type does not exist or is inactive.")

    if leave_type.requires_attachment and not attachment:
        raise ValidationError({"attachment": ["This leave type requires an attachment."]})

    days_requested = LeaveRequestCreateSerializer.calculate_leave_days(
        start_date=start_date,
        end_date=end_date,
    )

    if days_requested <= 0:
        raise ValidationError("Days requested must be greater than zero.")

    balance = LeaveBalance.objects.select_for_update().filter(
        employee=user,
        leave_type=leave_type,
    ).first()

    if balance is None:
        raise ValidationError("Leave balance does not exist for this user and leave type.")

    if balance.remaining_days < days_requested:
        raise ValidationError("Insufficient leave balance.")

    overlapping_requests = LeaveRequest.objects.filter(
        employee=user,
        start_date__lte=end_date,
        end_date__gte=start_date,
        status__in=[
            LeaveRequestStatus.PENDING,
            LeaveRequestStatus.APPROVED,
        ],
    )

    if overlapping_requests.exists():
        raise ValidationError("This leave request overlaps with an existing request.")

    leave_request = LeaveRequest(
        employee=user,
        leave_type=leave_type,
        start_date=start_date,
        end_date=end_date,
        days_requested=days_requested,
        reason=reason,
        attachment=attachment,
        status=LeaveRequestStatus.PENDING,
    )

    leave_request.full_clean()
    leave_request.save()

    return leave_request


@transaction.atomic
def cancel_leave_request_helper(user, leave_request_id, cancellation_reason=""):
    try:
        leave_request = LeaveRequest.objects.select_for_update().get(
            id=leave_request_id,
            employee=user
        )
    except LeaveRequest.DoesNotExist:
        raise ValidationError("Leave request not found or does not belong to the user.")

    if leave_request.status == LeaveRequestStatus.CANCELLED:
        raise ValidationError("This leave request is already cancelled.")

    if leave_request.status == LeaveRequestStatus.REJECTED:
        raise ValidationError("Rejected leave requests cannot be cancelled.")

    today = date.today()
    if leave_request.start_date <= today:
        raise ValidationError("Cannot cancel a leave request that has already started.")

    cancellation_reason = (cancellation_reason or "").strip()

    # Optional for PENDING
    if leave_request.status == LeaveRequestStatus.PENDING:
        leave_request.status = LeaveRequestStatus.CANCELLED
        leave_request.cancellation_reason = cancellation_reason
        leave_request.save(update_fields=["status", "cancellation_reason", "updated_at"])
        return leave_request

    # Required for APPROVED
    if leave_request.status == LeaveRequestStatus.APPROVED:
        if not cancellation_reason:
            raise ValidationError("Cancellation reason is required for approved leave requests.")

        balance = LeaveBalance.objects.select_for_update().get(
            employee=user,
            leave_type=leave_request.leave_type
        )
        balance.used_days -= leave_request.days_requested
        balance.full_clean()
        balance.save()

        leave_request.status = LeaveRequestStatus.CANCELLED
        leave_request.cancellation_reason = cancellation_reason
        leave_request.approved_by = None
        leave_request.approved_at = None
        leave_request.save(
            update_fields=[
                "status",
                "cancellation_reason",
                "approved_by",
                "approved_at",
                "updated_at",
            ]
        )
        return leave_request

    raise ValidationError("This leave request cannot be cancelled.")

def get_pending_leave_requests_helper(user):
    if user.role != UserRole.MANAGER:
        raise ValidationError("Only managers can view pending leave requests.")

    pending_requests = LeaveRequest.objects.filter(
        employee__manager=user,
        status=LeaveRequestStatus.PENDING,
    ).select_related(
        "employee",
        "leave_type",
    )

    return pending_requests

@transaction.atomic
def approve_leave_request_helper(user, leave_request_id):
    if user.role != UserRole.MANAGER:
        raise ValidationError("Only managers can approve leave requests.")

    try:
        leave_request = LeaveRequest.objects.select_for_update().select_related(
            "employee",
            "leave_type",
        ).get(id=leave_request_id)
    except LeaveRequest.DoesNotExist:
        raise ValidationError("Leave request not found.")

    if leave_request.employee.manager_id != user.id:
        raise ValidationError("You can only approve leave requests for employees assigned to you.")

    if leave_request.status != LeaveRequestStatus.PENDING:
        raise ValidationError("Only pending leave requests can be approved.")

    balance = LeaveBalance.objects.select_for_update().filter(
        employee=leave_request.employee,
        leave_type=leave_request.leave_type,
    ).first()

    if balance is None:
        raise ValidationError("Leave balance does not exist for this employee and leave type.")

    if balance.remaining_days < leave_request.days_requested:
        raise ValidationError("Insufficient leave balance.")

    balance.used_days += leave_request.days_requested
    balance.full_clean()
    balance.save()

    leave_request.status = LeaveRequestStatus.APPROVED
    leave_request.approved_by = user
    leave_request.approved_at = timezone.now()
    leave_request.rejection_reason = ""
    leave_request.save()

    return leave_request

@transaction.atomic
def reject_leave_request_helper(user, leave_request_id, rejection_reason):
    if user.role != UserRole.MANAGER:
        raise ValidationError("Only managers can reject leave requests.")

    try:
        leave_request = LeaveRequest.objects.select_for_update().select_related(
            "employee",
            "leave_type",
        ).get(id=leave_request_id)
    except LeaveRequest.DoesNotExist:
        raise ValidationError("Leave request not found.")

    if leave_request.employee.manager_id != user.id:
        raise ValidationError("You can only reject leave requests for employees assigned to you.")

    if leave_request.status != LeaveRequestStatus.PENDING:
        raise ValidationError("Only pending leave requests can be rejected.")

    rejection_reason = (rejection_reason or "").strip()
    if not rejection_reason:
        raise ValidationError("Rejection reason is required.")

    leave_request.status = LeaveRequestStatus.REJECTED
    leave_request.rejection_reason = rejection_reason
    leave_request.rejected_by = user
    leave_request.rejected_at = timezone.now()
    leave_request.save()

    return leave_request