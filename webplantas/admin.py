from django.contrib import admin
from webplantas.models import (
    Usuario, Rol, UsuarioRol,
    Departamento, Municipio, Parcela,
    CategoriaPlanta, CatalogoPilon,
    Pedido, DetallePedido, HistorialEstadoPedido,
    RutaEntrega, PedidoRuta, Vehiculo,
    
    Transportista, DocumentoVehiculo, PuntoSiembra, Finca,
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

# ============= LOGÍSTICA =============
@admin.register(RutaEntrega)
class RutaEntregaAdmin(admin.ModelAdmin):
    list_display = ['codigo_ruta', 'nombre_ruta', 'tecnico_campo', 'fecha_planificada', 'estado', 'vehiculo']
    list_filter = ['estado', 'departamento', 'fecha_planificada']
    search_fields = ['codigo_ruta', 'nombre_ruta', 'tecnico_campo__nombre_completo']
    readonly_fields = ['codigo_ruta']

@admin.register(PedidoRuta)
class PedidoRutaAdmin(admin.ModelAdmin):
    list_display = ['ruta', 'pedido', 'orden_entrega', 'entregado', 'hora_llegada', 'hora_salida']
    list_filter = ['entregado', 'ruta__estado']
    search_fields = ['ruta__codigo_ruta', 'pedido__codigo_seguimiento']

@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ['placa', 'tipo', 'marca', 'modelo', 'transportista', 'capacidad_carga_kg', 'activo']
    list_filter = ['tipo', 'activo', 'transportista']
    search_fields = ['placa', 'marca', 'modelo']

# ✅ NUEVOS: Transportistas
@admin.register(Transportista)
class TransportistaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'contacto', 'telefono', 'email', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre', 'contacto', 'nit']

# ✅ NUEVOS: Documentos de Vehículos
@admin.register(DocumentoVehiculo)
class DocumentoVehiculoAdmin(admin.ModelAdmin):
    list_display = ['vehiculo', 'tipo', 'numero_documento', 'fecha_vencimiento', 'estado_documento', 'dias_restantes']
    list_filter = ['tipo', 'fecha_vencimiento']
    search_fields = ['vehiculo__placa', 'numero_documento']
    date_hierarchy = 'fecha_vencimiento'
    
    def estado_documento(self, obj):
        from datetime import date
        if obj.esta_vencido:
            return "❌ VENCIDO"
        elif obj.dias_para_vencer <= 30:
            return "⚠️ POR VENCER"
        return "✅ VIGENTE"
    estado_documento.short_description = "Estado"
    
    def dias_restantes(self, obj):
        dias = obj.dias_para_vencer
        if dias < 0:
            return f"{abs(dias)} días vencido"
        return f"{dias} días"
    dias_restantes.short_description = "Días Restantes"

# ✅ NUEVOS: Puntos de Siembra
@admin.register(PuntoSiembra)
class PuntoSiembraAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'municipio', 'departamento', 'contacto', 'telefono', 'activo']
    list_filter = ['departamento', 'activo']
    search_fields = ['nombre', 'contacto', 'aldea_colonia']

# ✅ NUEVOS: Fincas/Viveros
@admin.register(Finca)
class FincaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'municipio', 'departamento', 'contacto', 'telefono', 'usuario', 'activo']
    list_filter = ['departamento', 'activo']
    search_fields = ['nombre', 'contacto', 'aldea_colonia']
    raw_id_fields = ['usuario']  # Para mejor rendimiento si hay muchos usuarios

# Notificaciones
@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'titulo', 'tipo', 'leida', 'fecha_creacion']
    list_filter = ['tipo', 'leida']