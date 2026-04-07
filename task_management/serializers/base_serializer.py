from rest_framework import serializers

class TaskBaseSerializer(serializers.Serializer):
    title = serializers.CharField(required=True, max_length=200)
    description = serializers.CharField(required=False, allow_blank=True, default="")
    completed = serializers.BooleanField(required=False, default=False)

class TaskUpdateSerializer(serializers.Serializer):
    task_id = serializers.IntegerField(required=True)
    title = serializers.CharField(required=True, max_length=200)
    description = serializers.CharField(required=False, allow_blank=True, default="")
    completed = serializers.BooleanField(required=False, default=False)

class TaskDeleteSerializer(serializers.Serializer):
    task_id = serializers.IntegerField(required=True)