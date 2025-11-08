# Importar modelos de usuarios
from .usuarios import Usuario, Rol, UsuarioRol, UsuarioManager

# Importar modelos de ubicaciones
from .ubicaciones import Departamento, Municipio, Parcela

# Importar modelos de catálogo
from .catalogo import CategoriaPlanta, CatalogoPilon

# Importar modelos de pedidos
from .pedidos import Pedido, DetallePedido, HistorialEstadoPedido, ESTADOS_PEDIDO

# Importar modelos de logística
from .logistica import (
    RutaEntrega, PedidoRuta, Vehiculo, ESTADOS_RUTA,
    Transportista, DocumentoVehiculo, PuntoSiembra, Finca, ETIQUETAS_RUTA
)

# Importar modelos de notificaciones
from .notificaciones import Notificacion

# Definir qué se exporta cuando se hace "from webplantas.models import *"
__all__ = [
    # Usuarios
    'Usuario',
    'Rol',
    'UsuarioRol',
    'UsuarioManager',
    
    # Ubicaciones
    'Departamento',
    'Municipio',
    'Parcela',
    
    # Catálogo
    'CategoriaPlanta',
    'CatalogoPilon',
    
    # Pedidos
    'Pedido',
    'DetallePedido',
    'HistorialEstadoPedido',
    'ESTADOS_PEDIDO',
    
    # Logística
    'RutaEntrega',
    'PedidoRuta',
    'Vehiculo',
    'ESTADOS_RUTA',
    'ETIQUETAS_RUTA',  
    'Transportista',  
    'DocumentoVehiculo',  
    'PuntoSiembra',  
    'Finca',  
    
    # Notificaciones
    'Notificacion',
]