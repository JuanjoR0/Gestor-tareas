from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from core.views import BoardViewSet, TaskViewSet, logout_view
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

# View que carga React sin CSRF ni login requerido
@method_decorator(csrf_exempt, name='dispatch')
class FrontendAppView(TemplateView):
    template_name = "frontend/index.html"

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    # 👇 Asegúrate de que esto existe para que no requiera autenticación
    def dispatch(self, request, *args, **kwargs):
        request._dont_enforce_csrf_checks = True
        return super().dispatch(request, *args, **kwargs)

# API routing
router = DefaultRouter()
router.register(r'boards', BoardViewSet, basename='board')
router.register(r'tasks', TaskViewSet, basename='task')

# URL patterns
urlpatterns = [
    path('admin/', admin.site.urls),
    path('logout/', logout_view, name='logout'),
    path('', include('core.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('', FrontendAppView.as_view(), name='frontend'),
    
    # Esta ruta SIEMPRE al final: sirve React para cualquier ruta no encontrada
    re_path(r'^.*$', FrontendAppView.as_view(), name='frontend'),
]
