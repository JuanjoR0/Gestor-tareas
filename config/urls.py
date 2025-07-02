
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views import BoardViewSet, TaskViewSet,logout_view
from core import views
from django.views.generic import TemplateView
from django.urls import re_path

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()
router.register(r'boards', BoardViewSet, basename='board')
router.register(r'tasks', TaskViewSet, basename='task')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('logout/', logout_view, name='logout'),
    path('', include('core.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
urlpatterns += [
    re_path(r'^.*$', TemplateView.as_view(template_name="index.html")),
]
