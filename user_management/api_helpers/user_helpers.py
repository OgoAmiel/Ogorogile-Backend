from django.core.exceptions import ValidationError
from django.db import transaction

from leave_management.models import LeaveBalance, LeaveType
from user_management.models import User, UserRole


def assign_manager(role, manager_id):
    manager = None

    if manager_id is not None:
        try:
            manager = User.objects.get(id=manager_id, is_active=True)
        except User.DoesNotExist:
            raise ValidationError({
                "manager_id": "Selected manager does not exist or is inactive."
            })

        if manager.role != UserRole.MANAGER:
            raise ValidationError({
                "manager_id": "Selected user is not a manager."
            })

    if role == UserRole.EMPLOYEE and manager is None:
        raise ValidationError({
            "manager_id": "Employees must be assigned to a manager."
        })

    if role in [UserRole.MANAGER, UserRole.ADMIN] and manager is not None:
        raise ValidationError({
            "manager_id": "Only employees can be assigned to a manager."
        })

    return manager


def update_assign_manager(target_user, role, manager_id):
    manager = None

    if manager_id is not None:
        try:
            manager = User.objects.get(id=manager_id, is_active=True)
        except User.DoesNotExist:
            raise ValidationError({
                "manager_id": "Selected manager does not exist or is inactive."
            })

        if manager.role != UserRole.MANAGER:
            raise ValidationError({
                "manager_id": "Selected user is not a manager."
            })

        if manager.id == target_user.id:
            raise ValidationError({
                "manager_id": "A user cannot be their own manager."
            })

    if role == UserRole.EMPLOYEE and manager is None:
        raise ValidationError({
            "manager_id": "Employees must be assigned to a manager."
        })

    if role in [UserRole.MANAGER, UserRole.ADMIN] and manager is not None:
        raise ValidationError({
            "manager_id": "Only employees can be assigned to a manager."
        })

    return manager


@transaction.atomic
def create_user_helper(request_user, username, first_name, last_name, email, password, role, employee_number, department, manager, is_active):

    if request_user.role != UserRole.ADMIN:
        raise ValidationError("Only admins can create users.")

    user = User.objects.create_user(
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

    if user.role == UserRole.EMPLOYEE:
        active_leave_types = LeaveType.objects.filter(is_active=True)

        for leave_type in active_leave_types:
            LeaveBalance.objects.create(
                employee=user,
                leave_type=leave_type,
                total_days=leave_type.default_days,
                used_days=0,
            )

    return user

@transaction.atomic
def update_user_helper(request_user, target_user, first_name, last_name, email, role, employee_number, department, manager, is_active):

    if request_user.role != UserRole.ADMIN:
        raise ValidationError("Only admins can update users.")

    target_user.first_name = first_name
    target_user.last_name = last_name
    target_user.email = email or ""
    target_user.role = role
    target_user.employee_number = employee_number
    target_user.department = department
    target_user.manager = manager
    target_user.is_active = is_active

    target_user.full_clean()
    target_user.save()

    return target_user

@transaction.atomic
def delete_user_helper(request_user, target_user):

    if request_user.role != UserRole.ADMIN:
        raise ValidationError("Only admins can delete users.")

    if request_user.id == target_user.id:
        raise ValidationError("You cannot delete your own account.")

    target_user.delete()
    return None