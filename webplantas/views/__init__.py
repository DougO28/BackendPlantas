# Backend/webplantas/views/__init__.py

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
from .dashboard import (
    DashboardView, 
    MetricasView, 
    DashboardEstadisticasView,
    ExportarExcelView  
)

# Test Data (TEMPORAL)
from .test_data import GenerarDatosPruebaView 

 
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
    'DashboardView', 
    'MetricasView', 
    'DashboardEstadisticasView',
    'ExportarExcelView',  # ✅ AGREGADO
    
    # Test Data (TEMPORAL)
    'GenerarDatosPruebaView',
]