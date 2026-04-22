from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import LeaveType, LeaveBalance, LeaveRequest


@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "default_days", "requires_attachment", "is_active")
    list_filter = ("is_active", "requires_attachment")
    search_fields = ("name",)


@admin.register(LeaveBalance)
class LeaveBalanceAdmin(admin.ModelAdmin):
    list_display = ("employee", "leave_type", "total_days", "used_days", "remaining_days")
    list_filter = ("leave_type",)
    search_fields = ("employee__username", "employee__first_name", "employee__last_name", "leave_type__name")


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "leave_type",
        "start_date",
        "end_date",
        "days_requested",
        "status",
        "approved_by",
        "approved_at",
        "rejected_by",
        "rejected_at",
        "created_at",
    )
    list_filter = ("status", "leave_type", "start_date", "end_date")
    search_fields = (
        "employee__username",
        "employee__first_name",
        "employee__last_name",
        "leave_type__name",
        "reason",
    )
    readonly_fields = ("created_at", "updated_at", "approved_at", "rejected_at")