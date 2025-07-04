from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField


class Board(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_boards')
    members = models.ManyToManyField(User, related_name='boards') 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class TaskList(models.Model):
    name = models.CharField(max_length=100)
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='task_lists')
    position = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.name} ({self.board.name})"

class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    task_list = models.ForeignKey(TaskList, on_delete=models.CASCADE, related_name='tasks')
    assigned_to = models.ManyToManyField(User, blank=True, related_name='tasks_assigned')
    due_date = models.DateField(null=True, blank=True)
    tags = models.CharField(max_length=200, blank=True)
    priority = models.CharField(max_length=20, choices=[
        ('low', 'Baja'),
        ('medium', 'Media'),
        ('high', 'Alta'),
    ], default='medium')
    position = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['position']

    def __str__(self):
        return self.title
    
TAGS_CHOICES = [
    ('Urgente', 'Urgente'),
    ('Diseño', 'Diseño'),
    ('Bugs', 'Bugs'),
    ('Reunión', 'Reunión'),
    ('Frontend', 'Frontend'),
    ('Backend', 'Backend'),
]
