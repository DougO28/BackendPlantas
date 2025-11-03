from django.contrib import admin
from webplantas.models import (
    Usuario, Rol, UsuarioRol,
    Departamento, Municipio, Parcela,
    CategoriaPlanta, CatalogoPilon,
    Pedido, DetallePedido, HistorialEstadoPedido,
    RutaEntrega, PedidoRuta, Vehiculo,
    Notificacion
)

# Usuarios
@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ['email', 'nombre_completo', 'activo', 'is_staff']
    list_filter = ['activo', 'is_staff']
    search_fields = ['email', 'nombre_completo']

@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ['nombre_rol', 'descripcion']

@admin.register(UsuarioRol)
class UsuarioRolAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'rol', 'fecha_asignacion', 'activo']
    list_filter = ['rol', 'activo']

# Ubicaciones
@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'region']

@admin.register(Municipio)
class MunicipioAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'departamento']
    list_filter = ['departamento']
    search_fields = ['nombre']

@admin.register(Parcela)
class ParcelaAdmin(admin.ModelAdmin):
    list_display = ['nombre_parcela', 'usuario', 'municipio', 'activa']
    list_filter = ['activa', 'municipio']

# Catálogo
@admin.register(CategoriaPlanta)
class CategoriaPlantaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'activo']

@admin.register(CatalogoPilon)
class CatalogoPilonAdmin(admin.ModelAdmin):
    list_display = ['nombre_variedad', 'categoria', 'precio_unitario', 'stock', 'activo']
    list_filter = ['categoria', 'activo']
    search_fields = ['nombre_variedad']

# Pedidos
@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ['codigo_seguimiento', 'usuario', 'estado', 'fecha_pedido', 'total']
    list_filter = ['estado', 'canal_origen', 'fecha_pedido']
    search_fields = ['codigo_seguimiento', 'usuario__nombre_completo']

@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):
    list_display = ['pedido', 'pilon', 'cantidad', 'precio_unitario', 'subtotal']

@admin.register(HistorialEstadoPedido)
class HistorialEstadoPedidoAdmin(admin.ModelAdmin):
    list_display = ['pedido', 'estado_anterior', 'estado_nuevo', 'fecha_cambio', 'usuario_cambio']
    list_filter = ['estado_nuevo']

# Logística
@admin.register(RutaEntrega)
class RutaEntregaAdmin(admin.ModelAdmin):
    list_display = ['codigo_ruta', 'nombre_ruta', 'tecnico_campo', 'fecha_planificada', 'estado']
    list_filter = ['estado', 'departamento']
    search_fields = ['codigo_ruta', 'nombre_ruta']

@admin.register(PedidoRuta)
class PedidoRutaAdmin(admin.ModelAdmin):
    list_display = ['ruta', 'pedido', 'orden_entrega', 'entregado']
    list_filter = ['entregado']

@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ['placa', 'marca', 'modelo', 'activo']
    list_filter = ['activo']
    search_fields = ['placa']

# Notificaciones
@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'titulo', 'tipo', 'leida', 'fecha_creacion']
    list_filter = ['tipo', 'leida']