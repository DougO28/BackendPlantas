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

# Catálogos Logística (NUEVO - AGREGAR ESTA LÍNEA)
from .catalogos_logistica import (
    TransportistaViewSet,
    DocumentoVehiculoViewSet,
    PuntoSiembraViewSet,
    FincaViewSet
)

# Notificaciones
from .notificaciones import NotificacionViewSet

# Dashboard
from .dashboard import (
    DashboardView,
    DashboardEstadisticasView,
    MetricasView,
    ExportarExcelView
)

# Otros
from .test_data import GenerarDatosPruebaView

__all__ = [
    # Auth
    'CustomTokenObtainPairView',
    'ChangePasswordView',
    'RegisterView',
    
    # Usuarios
    'UsuarioViewSet',
    'RolViewSet',
    
    # Ubicaciones
    'DepartamentoViewSet',
    'MunicipioViewSet',
    
    # Catálogo
    'CatalogoPilonViewSet',
    'CategoriaPlantaViewSet',
    
    # Pedidos
    'PedidoViewSet',
    
    # Logística
    'RutaEntregaViewSet',
    'VehiculoViewSet',
    
    # Catálogos Logística (AGREGAR ESTOS)
    'TransportistaViewSet',
    'DocumentoVehiculoViewSet',
    'PuntoSiembraViewSet',
    'FincaViewSet',
    
    # Notificaciones
    'NotificacionViewSet',
    
    # Dashboard
    'DashboardView',
    'DashboardEstadisticasView',
    'MetricasView',
    'ExportarExcelView',
    
    # Otros
    'GenerarDatosPruebaView',
]