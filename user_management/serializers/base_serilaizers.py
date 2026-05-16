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
        return value.strip()

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

        return value.strip()

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

    def validate_employee_number(self, value):
        if value in [None, ""]:
            return None

        return value.strip()

class DeleteUserSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=True)