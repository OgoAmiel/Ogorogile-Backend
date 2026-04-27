from decimal import Decimal
import os
from rest_framework import serializers
from leave_management.models import LeaveType

class LeaveRequestCreateSerializer(serializers.Serializer):
    leave_type_id = serializers.IntegerField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    reason = serializers.CharField(required=False, allow_blank=True)
    attachment = serializers.FileField(required=False, allow_null=True)

    def validate_leave_type_id(self, value):
        try:
            LeaveType.objects.get(id=value, is_active=True)
        except LeaveType.DoesNotExist:
            raise serializers.ValidationError("Selected leave type does not exist or is inactive.")
        return value

    def validate_attachment(self, value):
        if not value:
            return value

        allowed_extensions = {".pdf", ".jpg", ".jpeg", ".png"}
        extension = os.path.splitext(value.name)[1].lower()

        if extension not in allowed_extensions:
            raise serializers.ValidationError(
                "Only PDF, JPG, JPEG, and PNG files are allowed."
            )

        max_size_mb = 5
        if value.size > max_size_mb * 1024 * 1024:
            raise serializers.ValidationError(
                f"File size must not exceed {max_size_mb}MB."
            )

        return value

    def validate(self, attrs):
        start_date = attrs.get("start_date")
        end_date = attrs.get("end_date")
        leave_type_id = attrs.get("leave_type_id")
        attachment = attrs.get("attachment")

        if start_date > end_date:
            raise serializers.ValidationError(
                {"end_date": "End date must be on or after start date."}
            )

        leave_type = LeaveType.objects.get(id=leave_type_id, is_active=True)

        if leave_type.requires_attachment and not attachment:
            raise serializers.ValidationError(
                {"attachment": "A supporting document is required for this leave type."}
            )

        return attrs

    @staticmethod
    def calculate_leave_days(start_date, end_date):
        total_days = (end_date - start_date).days + 1
        return Decimal(str(total_days))

class ApproveLeaveRequestSerializer(serializers.Serializer):
    leave_request_id = serializers.IntegerField()

class RejectLeaveRequestSerializer(serializers.Serializer):
    leave_request_id = serializers.IntegerField()
    rejection_reason = serializers.CharField()

    def validate_rejection_reason(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Rejection reason is required.")
        return value.strip()

class CancelLeaveRequestSerializer(serializers.Serializer):
    leave_request_id = serializers.IntegerField()
    cancellation_reason = serializers.CharField(required=False, allow_blank=True)

    def validate_cancellation_reason(self, value):
        return value.strip()