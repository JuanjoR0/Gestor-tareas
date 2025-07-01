from django import forms
from .models import Board,Task,TaskList,TAGS_CHOICES
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

User = get_user_model()

TAG_CHOICES = [
    ('Urgente', 'Urgente'),
    ('Diseño', 'Diseño'),
    ('Bugs', 'Bugs'),
    ('Reunión', 'Reunión'),
    ('Frontend', 'Frontend'),
    ('Backend', 'Backend'),
]

class BoardForm(forms.ModelForm):
    class Meta:
        model = Board
        fields = ['name']  


class TaskListForm(forms.ModelForm):
    class Meta:
        model = TaskList
        fields = ['name']

class TaskForm(forms.ModelForm):
    due_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False,
        label='Fecha max de entrega'
    )

    tags = forms.MultipleChoiceField(
        choices=TAGS_CHOICES,
        widget=forms.SelectMultiple(attrs={'size': 6}),
        required=False,
        label='Etiquetas'
    )

    def __init__(self, *args, **kwargs):
        self.board = kwargs.pop('board', None) 
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.tags:
            self.fields['tags'].initial = self.instance.tags.split(',')

    def clean_tags(self):
        tags = self.cleaned_data.get('tags', [])
        if len(tags) > 2:
            raise forms.ValidationError("Solo puedes seleccionar hasta 2 etiquetas.")
        return ",".join(tags)

    class Meta:
        model = Task
        fields = ['title', 'description', 'due_date','assigned_to', 'priority', 'tags']
