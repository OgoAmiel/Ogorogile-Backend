from django.db import models

# Create your models here.
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class LeaveRequestStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    APPROVED = "APPROVED", "Approved"
    REJECTED = "REJECTED", "Rejected"
    CANCELLED = "CANCELLED", "Cancelled"


class LeaveType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    default_days = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    requires_attachment = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class LeaveBalance(models.Model):
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="leave_balances")
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE, related_name="balances")
    total_days = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    used_days = models.DecimalField(max_digits=5, decimal_places=1, default=0)

    class Meta:
        unique_together = ("employee", "leave_type")

    @property
    def remaining_days(self):
        return self.total_days - self.used_days

    def clean(self):
        if self.total_days < 0:
            raise ValidationError("Total days cannot be negative.")

        if self.used_days < 0:
            raise ValidationError("Used days cannot be negative.")

        if self.used_days > self.total_days:
            raise ValidationError("Used days cannot be greater than total days.")

    def __str__(self):
        return f"{self.employee.username} - {self.leave_type.name}"


class LeaveRequest(models.Model):
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="leave_requests")
    leave_type = models.ForeignKey(LeaveType, on_delete=models.PROTECT, related_name="leave_requests")
    start_date = models.DateField()
    end_date = models.DateField()
    days_requested = models.DecimalField(max_digits=5, decimal_places=1)
    reason = models.TextField(blank=True)
    attachment = models.FileField(upload_to="leave_attachments/", null=True, blank=True)

    status = models.CharField(max_length=20, choices=LeaveRequestStatus.choices, default=LeaveRequestStatus.PENDING)
    rejection_reason = models.TextField(blank=True)
    cancellation_reason = models.TextField(blank=True)

    rejected_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="rejected_leave_requests")
    rejected_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="approved_leave_requests")
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def clean(self):
        if self.start_date > self.end_date:
            raise ValidationError("Start date cannot be after end date.")

        if self.days_requested <= 0:
            raise ValidationError("Days requested must be greater than zero.")

    def __str__(self):
        return f"{self.employee.username} - {self.leave_type.name} ({self.status})"