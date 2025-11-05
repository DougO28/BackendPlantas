# Auth
from .auth import CustomTokenObtainPairView, ChangePasswordView, RegisterView

# Usuarios
from .usuarios import UsuarioViewSet, RolViewSet

# Ubicaciones
from .ubicaciones import DepartamentoViewSet, MunicipioViewSet

# Catálogo
from .catalogo import CatalogoPilonViewSet, CategoriaPlantaViewSet

# Pedidos
from .pedidos import PedidoViewSet

# Logística
from .logistica import RutaEntregaViewSet, VehiculoViewSet

# Notificaciones
from .notificaciones import NotificacionViewSet

# Dashboard
from .dashboard import DashboardView, MetricasView, DashboardEstadisticasView

# Test Data (TEMPORAL)
from .test_data import GenerarDatosPruebaView  # ✅ AGREGAR

__all__ = [
    # Auth
    'CustomTokenObtainPairView', 'ChangePasswordView', 'RegisterView',
    
    # Usuarios
    'UsuarioViewSet', 'RolViewSet',
    
    # Ubicaciones
    'DepartamentoViewSet', 'MunicipioViewSet',
    
    # Catálogo
    'CatalogoPilonViewSet', 'CategoriaPlantaViewSet',
    
    # Pedidos
    'PedidoViewSet',
    
    # Logística
    'RutaEntregaViewSet', 'VehiculoViewSet',
    
    # Notificaciones
    'NotificacionViewSet',
    
    # Dashboard
    'DashboardView', 'MetricasView', 'DashboardEstadisticasView',
    
    # Test Data (TEMPORAL)
    'GenerarDatosPruebaView',  # ✅ AGREGAR
]