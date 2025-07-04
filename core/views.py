from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import models
from .models import Board, Task, TaskList
from .forms import BoardForm, TaskForm, TaskListForm

from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from .serializers import TaskSerializer, BoardSerializer

from django.views.generic import View
from django.http import HttpResponse
from django.conf import settings
import os
from django.contrib.auth import logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.shortcuts import render
from rest_framework.permissions import BasePermission, SAFE_METHODS
import logging
from rest_framework.response import Response
from rest_framework import status

class IsTaskOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        
        if request.method in SAFE_METHODS:
            return True
        
        return obj.created_by == request.user or request.user in obj.assigned_to.all()
    
logger = logging.getLogger(__name__) 


class TaskViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def update(self, request, *args, **kwargs):
        print("🛠️ PATCH recibido")
        print("Datos recibidos:", request.data)

        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        if serializer.is_valid():
            print("✔️ Datos validados correctamente")
            self.perform_update(serializer)
            return Response(serializer.data)
        else:
            print("❌ Errores de validación:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BoardViewSet(ReadOnlyModelViewSet): 
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated]


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    return Response({
        'id': request.user.id,
        'username': request.user.username,
    })

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario creado correctamente. Ya puedes iniciar sesión.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@csrf_exempt
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return JsonResponse({'message': 'Sesión cerrada'})  
    elif request.method == 'GET':
        logout(request)
        return redirect('login')  
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)

@login_required
def home(request):
    boards = Board.objects.filter(
        models.Q(owner=request.user) | models.Q(members=request.user)
    ).prefetch_related('task_lists__tasks', 'task_lists', 'members').distinct()
    return render(request, 'core/home.html', {'boards': boards})

@login_required
def create_board(request):
    if request.method == 'POST':
        form = BoardForm(request.POST)
        if form.is_valid():
            board = form.save(commit=False)
            board.owner = request.user
            board.save()
            board.members.add(request.user)
            return redirect('home')
    else:
        form = BoardForm()
    return render(request, 'core/create_board.html', {'form': form})

@login_required
def board_detail(request, board_id):
    board = get_object_or_404(Board, id=board_id)
    if request.user not in board.members.all() and request.user != board.owner:
        return redirect('home')
    task_lists = board.task_lists.prefetch_related('tasks')
    return render(request, 'core/board_detail.html', {'board': board, 'task_lists': task_lists})

@login_required
def tasklist_create(request, board_id):
    board = get_object_or_404(Board, id=board_id)
    if request.user != board.owner and request.user not in board.members.all():
        return redirect('home')
    if request.method == 'POST':
        form = TaskListForm(request.POST)
        if form.is_valid():
            tasklist = form.save(commit=False)
            tasklist.board = board
            tasklist.save()
            return redirect('board_detail', board_id=board.id)
    else:
        form = TaskListForm()
    return render(request, 'core/tasklist_form.html', {'form': form, 'board': board})

@login_required
def tasklist_edit(request, board_id, tasklist_id):
    board = get_object_or_404(Board, id=board_id)
    tasklist = get_object_or_404(TaskList, id=tasklist_id, board=board)
    if request.user != board.owner and request.user not in board.members.all():
        return redirect('home')
    if request.method == 'POST':
        form = TaskListForm(request.POST, instance=tasklist)
        if form.is_valid():
            form.save()
            return redirect('board_detail', board_id=board.id)
    else:
        form = TaskListForm(instance=tasklist)
    return render(request, 'core/tasklist_form.html', {'form': form, 'board': board})

@login_required
def tasklist_delete(request, board_id, tasklist_id):
    board = get_object_or_404(Board, id=board_id)
    tasklist = get_object_or_404(TaskList, id=tasklist_id, board=board)
    if request.user != board.owner and request.user not in board.members.all():
        return redirect('home')
    if request.method == 'POST':
        tasklist.delete()
        return redirect('board_detail', board_id=board.id)
    return render(request, 'core/tasklist_confirm_delete.html', {'tasklist': tasklist, 'board': board})

@login_required
def task_create(request, board_id):
    board = get_object_or_404(Board, id=board_id)
    if request.user != board.owner and request.user not in board.members.all():
        return redirect('home')
    list_id = request.GET.get('list_id')
    if not list_id:
        return redirect('board_detail', board_id=board.id)
    task_list = get_object_or_404(TaskList, id=list_id, board=board)
    if request.method == 'POST':
        form = TaskForm(request.POST, board=board)
        if form.is_valid():
            task = form.save(commit=False)
            task.task_list = task_list
            task.save()
            form.save_m2m()
            return redirect('board_detail', board_id=board.id)
    else:
        form = TaskForm(board=board)
    return render(request, 'core/task_form.html', {'form': form, 'board': board, 'task_list': task_list})

@login_required
def task_edit(request, board_id, task_id):
    board = get_object_or_404(Board, id=board_id)
    if request.user != board.owner and request.user not in board.members.all():
        return redirect('home')
    task = get_object_or_404(Task, id=task_id, task_list__board=board)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task, board=board)
        if form.is_valid():
            form.save()
            return redirect('board_detail', board_id=board.id)
    else:
        form = TaskForm(instance=task, board=board)
    return render(request, 'core/task_form.html', {'form': form, 'board': board, 'task': task})

@login_required
def task_delete(request, board_id, task_id):
    board = get_object_or_404(Board, id=board_id)
    task = get_object_or_404(Task, id=task_id)
    if request.method == 'POST':
        task.delete()
        return redirect('board_detail', board_id=board.id)
    return render(request, 'core/task_confirm_delete.html', {'task': task, 'board': board})

class FrontendAppView(View):
    def get(self, request):
        try:
            index_path = os.path.join(settings.BASE_DIR, 'core', 'templates', 'frontend', 'index.html')
            with open(index_path, encoding='utf-8') as f:
                return HttpResponse(f.read())
        except FileNotFoundError:
            return HttpResponse("El archivo index.html no se encontró, asegúrate de haber corrido npm run build.", status=501)