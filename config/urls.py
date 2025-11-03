from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView
from webplantas.views import DashboardEstadisticasView

from webplantas.views import (
    # Auth
    CustomTokenObtainPairView, ChangePasswordView, RegisterView,
    # ViewSets
    UsuarioViewSet, RolViewSet,
    DepartamentoViewSet, MunicipioViewSet,
    CatalogoPilonViewSet, CategoriaPlantaViewSet,
    PedidoViewSet,
    RutaEntregaViewSet, VehiculoViewSet,
    NotificacionViewSet,
    # APIViews
    DashboardView, MetricasView,
)

# Router principal
router = routers.DefaultRouter()

# Registrar ViewSets
router.register(r'usuarios', UsuarioViewSet, basename='usuario')
router.register(r'roles', RolViewSet, basename='rol')
router.register(r'departamentos', DepartamentoViewSet, basename='departamento')
router.register(r'municipios', MunicipioViewSet, basename='municipio')
router.register(r'catalogo', CatalogoPilonViewSet, basename='catalogo')
router.register(r'categorias', CategoriaPlantaViewSet, basename='categoria')
router.register(r'pedidos', PedidoViewSet, basename='pedido')
router.register(r'rutas', RutaEntregaViewSet, basename='ruta')
router.register(r'vehiculos', VehiculoViewSet, basename='vehiculo')
router.register(r'notificaciones', NotificacionViewSet, basename='notificacion')

urlpatterns = [
    # Admin de Django
    path('admin/', admin.site.urls),
    
    # Autenticación JWT
    path('api/auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('api/auth/register/', RegisterView.as_view(), name='register'),
    
    # Dashboard y Métricas
    path('api/dashboard/', DashboardView.as_view(), name='dashboard'),
    path('api/metricas/', MetricasView.as_view(), name='metricas'),
    path('api/dashboard/estadisticas/', DashboardEstadisticasView.as_view(), name='dashboard-estadisticas'),
    
    # Incluir todas las rutas del router
    path('api/', include(router.urls)),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)