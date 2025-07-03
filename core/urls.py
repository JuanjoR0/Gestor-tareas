from django.urls import path, include
from . import views
from .views import TaskViewSet, BoardViewSet, current_user  
from django.contrib.auth import views as auth_views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'tasks', TaskViewSet)
router.register(r'boards', BoardViewSet)

urlpatterns = [
    
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', views.register, name='register'),

    
    path('', views.home, name='home'),

 
    path('board/create/', views.create_board, name='create_board'),
    path('board/<int:board_id>/task/create/', views.task_create, name='task_create'),
    path('board/<int:board_id>/task/<int:task_id>/edit/', views.task_edit, name='task_edit'),
    path('board/<int:board_id>/task/<int:task_id>/delete/', views.task_delete, name='task_delete'),
    path('board/<int:board_id>/', views.board_detail, name='board_detail'),
    path('board/<int:board_id>/tasklist/create/', views.tasklist_create, name='tasklist_create'),
    path('board/<int:board_id>/tasklist/<int:tasklist_id>/edit/', views.tasklist_edit, name='tasklist_edit'),
    path('board/<int:board_id>/tasklist/<int:tasklist_id>/delete/', views.tasklist_delete, name='tasklist_delete'),


    path('api/', include(router.urls)),
    path('api/user/', current_user),
]
