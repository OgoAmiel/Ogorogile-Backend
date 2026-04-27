from leave_management.models import LeaveBalance, LeaveRequest, LeaveType
from rest_framework import serializers

class LeaveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveType
        fields = [
            "id",
            "name",
            "default_days",
            "requires_attachment",
            "is_active",
        ]


class LeaveBalanceSerializer(serializers.ModelSerializer):
    leave_type_name = serializers.CharField(source="leave_type.name", read_only=True)
    remaining_days = serializers.SerializerMethodField()

    class Meta:
        model = LeaveBalance
        fields = [
            "id",
            "leave_type",
            "leave_type_name",
            "total_days",
            "used_days",
            "remaining_days",
        ]

    def get_remaining_days(self, obj):
        return obj.remaining_days

class LeaveRequestListSerializer(serializers.ModelSerializer):
    leave_type = LeaveTypeSerializer(read_only=True)
    employee = serializers.SerializerMethodField()
    approved_by = serializers.SerializerMethodField()
    rejected_by = serializers.SerializerMethodField()
    attachment_url = serializers.SerializerMethodField()

    class Meta:
        model = LeaveRequest
        fields = [
            "id",
            "employee",
            "leave_type",
            "start_date",
            "end_date",
            "days_requested",
            "reason",
            "attachment",
            "attachment_url",
            "status",
            "rejection_reason",
            "cancellation_reason",
            "rejected_by",
            "rejected_at",
            "approved_by",
            "approved_at",
            "created_at",
            "updated_at",
        ]

    def get_employee(self, obj):
        user = obj.employee
        return {
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
            "employee_number": user.employee_number,
            "department": user.department,
        }

    def get_approved_by(self, obj):
        if not obj.approved_by:
            return None

        user = obj.approved_by
        return {
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
        }

    def get_rejected_by(self, obj):
        if not obj.rejected_by:
            return None

        user = obj.rejected_by
        return {
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
        }

    def get_attachment_url(self, obj):
        request = self.context.get("request")
        if obj.attachment and request:
            return request.build_absolute_uri(obj.attachment.url)
        return None
