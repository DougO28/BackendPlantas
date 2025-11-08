# Backend/webplantas/serializers/__init__.py

# Auth
from .auth import LoginSerializer, ChangePasswordSerializer, RegisterSerializer

# Usuarios
from .usuarios import (
    RolSerializer, UsuarioListSerializer, UsuarioDetailSerializer,
    UsuarioCreateSerializer, UsuarioUpdateSerializer
)

# Ubicaciones
from .ubicaciones import DepartamentoSerializer, MunicipioSerializer, ParcelaSerializer

# Catálogo
from .catalogo import (
    CategoriaPlantaSerializer,
    CatalogoPilonSerializer,
    CatalogoPilonListSerializer,
    CatalogoPilonCreateUpdateSerializer,
)

# Logística - catálogos (CORREGIDO: catalogos_logistica con 's')
from .catalogos_logistica import (
    TransportistaSerializer,
    DocumentoVehiculoSerializer,
    PuntoSiembraSerializer,
    FincaSerializer
)

# Pedidos
from .pedidos import (
    DetallePedidoSerializer, HistorialEstadoSerializer,
    PedidoListSerializer, PedidoDetailSerializer,
    PedidoCreateSerializer, CambiarEstadoPedidoSerializer
)

# Logística
from .logistica import (
    VehiculoSerializer, PedidoRutaSerializer,
    RutaEntregaListSerializer, RutaEntregaDetailSerializer,
    RutaEntregaCreateSerializer, ConfirmarEntregaSerializer
)

# Notificaciones
from .notificaciones import NotificacionSerializer

__all__ = [
    # Auth
    'LoginSerializer', 'ChangePasswordSerializer', 'RegisterSerializer',
    
    # Usuarios
    'RolSerializer', 'UsuarioListSerializer', 'UsuarioDetailSerializer',
    'UsuarioCreateSerializer', 'UsuarioUpdateSerializer',
    
    # Ubicaciones
    'DepartamentoSerializer', 'MunicipioSerializer', 'ParcelaSerializer',
    
    # Catálogo
    'CategoriaPlantaSerializer', 'CatalogoPilonSerializer',  
    'CatalogoPilonListSerializer', 'CatalogoPilonCreateUpdateSerializer',
    
    # Catálogos Logística
    'TransportistaSerializer', 'DocumentoVehiculoSerializer',
    'PuntoSiembraSerializer', 'FincaSerializer',
    
    # Pedidos
    'DetallePedidoSerializer', 'HistorialEstadoSerializer',
    'PedidoListSerializer', 'PedidoDetailSerializer',
    'PedidoCreateSerializer', 'CambiarEstadoPedidoSerializer',
    
    # Logística
    'VehiculoSerializer', 'PedidoRutaSerializer',
    'RutaEntregaListSerializer', 'RutaEntregaDetailSerializer',
    'RutaEntregaCreateSerializer', 'ConfirmarEntregaSerializer',
    
    # Notificaciones
    'NotificacionSerializer',
]