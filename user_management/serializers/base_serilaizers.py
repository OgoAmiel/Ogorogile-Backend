from rest_framework import serializers
from user_management.models import User, UserRole

class CreateUserSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, required=False, allow_blank=True)
    first_name = serializers.CharField(max_length=150, required=True, allow_blank=False)
    last_name = serializers.CharField(max_length=150, required=True, allow_blank=False)
    email = serializers.EmailField(required=True, allow_blank=False)
    password = serializers.CharField(write_only=True, min_length=8)
    role = serializers.ChoiceField(choices=UserRole.choices)
    employee_number = serializers.CharField(max_length=50, required=True, allow_blank=False, allow_null=False)
    department = serializers.CharField(max_length=100, required=True, allow_blank=False)
    manager_id = serializers.IntegerField(required=False, allow_null=True)
    is_active = serializers.BooleanField(required=False, default=True)

    def validate_username(self, value):
        value = value.strip()

        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value

    def validate_first_name(self, value):
        return value.strip()

    def validate_last_name(self, value):
        return value.strip()

    def validate_department(self, value):
        return value.strip()

    def validate_email(self, value):
        return value.strip()

    def validate_employee_number(self, value):
        if value in [None, ""]:
            return None

        value = value.strip()

        if User.objects.filter(employee_number=value).exists():
            raise serializers.ValidationError("A user with this employee number already exists.")
        return value

    def validate(self, attrs):
        role = attrs.get("role")
        manager_id = attrs.get("manager_id")
        manager = None

        if manager_id is not None:
            try:
                manager = User.objects.get(id=manager_id, is_active=True)
            except User.DoesNotExist:
                raise serializers.ValidationError({
                    "manager_id": "Selected manager does not exist or is inactive."
                })

            if manager.role != UserRole.MANAGER:
                raise serializers.ValidationError({
                    "manager_id": "Selected user is not a manager."
                })

        if role == UserRole.EMPLOYEE and manager is None:
            raise serializers.ValidationError({
                "manager_id": "Employees must be assigned to a manager."
            })

        if role in [UserRole.MANAGER, UserRole.ADMIN] and manager is not None:
            raise serializers.ValidationError({
                "manager_id": "Only employees can be assigned to a manager."
            })

        attrs["manager"] = manager
        return attrs

class UpdateUserSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    email = serializers.EmailField(required=False, allow_blank=True)
    role = serializers.ChoiceField(choices=UserRole.choices)
    employee_number = serializers.CharField(max_length=50, required=False, allow_blank=True, allow_null=True,)
    department = serializers.CharField(max_length=100, required=False, allow_blank=True,)
    manager_id = serializers.IntegerField(required=False, allow_null=True)
    is_active = serializers.BooleanField(required=False)

    def validate_first_name(self, value):
        return value.strip()

    def validate_last_name(self, value):
        return value.strip()

    def validate_department(self, value):
        return value.strip()

    def validate_email(self, value):
        return value.strip()

    def validate_user_id(self, value):
        try:
            user = User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Selected user does not exist.")
        return value

    def validate_employee_number(self, value):
        if value in [None, ""]:
            return None

        value = value.strip()
        user_id = self.initial_data.get("user_id")

        if User.objects.filter(employee_number=value).exclude(id=user_id).exists():
            raise serializers.ValidationError("A user with this employee number already exists.")

        return value

    def validate(self, attrs):
        user_id = attrs.get("user_id")
        role = attrs.get("role")
        manager_id = attrs.get("manager_id")
        manager = None

        try:
            target_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise serializers.ValidationError({
                "user_id": "Selected user does not exist."
            })

        if manager_id is not None:
            try:
                manager = User.objects.get(id=manager_id, is_active=True)
            except User.DoesNotExist:
                raise serializers.ValidationError({
                    "manager_id": "Selected manager does not exist or is inactive."
                })

            if manager.role != UserRole.MANAGER:
                raise serializers.ValidationError({
                    "manager_id": "Selected user is not a manager."
                })

            if manager.id == target_user.id:
                raise serializers.ValidationError({
                    "manager_id": "A user cannot be their own manager."
                })

        if role == UserRole.EMPLOYEE and manager is None:
            raise serializers.ValidationError({
                "manager_id": "Employees must be assigned to a manager."
            })

        if role in [UserRole.MANAGER, UserRole.ADMIN] and manager is not None:
            raise serializers.ValidationError({
                "manager_id": "Only employees can be assigned to a manager."
            })

        attrs["target_user"] = target_user
        attrs["manager"] = manager
        return attrs