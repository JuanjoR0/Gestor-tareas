from rest_framework import serializers
from .models import Task, Board, TaskList
from django.contrib.auth.models import User
from rest_framework import serializers


class AssignedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class TaskSerializer(serializers.ModelSerializer):
    tags = serializers.SerializerMethodField()
    tags_input = serializers.CharField(write_only=True, required=False)
    assigned_to = AssignedUserSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'task_list', 'assigned_to', 'due_date', 'priority', 'position', 'tags', 'tags_input']

    def get_tags(self, obj):
        return obj.tags.split(",") if obj.tags else []

    def update(self, instance, validated_data):
        tags_input = validated_data.pop("tags_input", "")
        if tags_input:
            validated_data["tags"] = tags_input
        return super().update(instance, validated_data)

    def create(self, validated_data):
        tags_input = validated_data.pop("tags_input", "")
        if tags_input:
            validated_data["tags"] = tags_input
        return super().create(validated_data)
    
class TaskListSerializer(serializers.ModelSerializer):
    tasks = serializers.SerializerMethodField()  # 👈 Usamos método personalizado

    class Meta:
        model = TaskList
        fields = ['id', 'name', 'tasks']

    def get_tasks(self, obj):
        ordered_tasks = obj.tasks.order_by('position')  # 👈 Aquí se ordenan por posición
        return TaskSerializer(ordered_tasks, many=True).data

class BoardSerializer(serializers.ModelSerializer):
    task_lists = TaskListSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'name', 'task_lists']

