from rest_framework import serializers
from user_management.models import User


class CurrentUserSerializer(serializers.ModelSerializer):
    manager_id = serializers.IntegerField(source="manager.id", read_only=True)
    manager_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "role",
            "employee_number",
            "department",
            "manager_id",
            "manager_name",
        ]

    def get_manager_name(self, obj):
        if obj.manager:
            return obj.manager.get_full_name() or obj.manager.username
        return None

class UserReadSerializer(serializers.ModelSerializer):
    manager_id = serializers.IntegerField(source="manager.id", read_only=True)
    manager_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "role",
            "employee_number",
            "department",
            "is_active",
            "manager_id",
            "manager_name",
        ]

    def get_manager_name(self, obj):
        if obj.manager:
            return obj.manager.get_full_name() or obj.manager.username
        return None