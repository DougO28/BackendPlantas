from django.db import models
from decimal import Decimal
from django.utils import timezone

ESTADOS_PEDIDO = [
    ('recibido', 'Recibido'),
    ('confirmado', 'Confirmado'),
    ('en_preparacion', 'En Preparación'),
    ('listo_entrega', 'Listo para Entrega'),
    ('en_ruta', 'En Ruta'),
    ('entregado', 'Entregado'),
    ('cancelado', 'Cancelado'),
]


class Pedido(models.Model):
    # Identificación
    codigo_seguimiento = models.CharField(max_length=20, unique=True, editable=False)
    
    # Cliente
    usuario = models.ForeignKey('Usuario', on_delete=models.CASCADE)
    
    # Estado y fechas
    estado = models.CharField(max_length=20, choices=ESTADOS_PEDIDO, default='recibido')
    fecha_pedido = models.DateTimeField(default=timezone.now)
    fecha_entrega_estimada = models.DateField(null=True, blank=True)
    fecha_entrega_real = models.DateField(null=True, blank=True)
    
    # Información de entrega
    direccion_entrega = models.CharField(max_length=300)
    municipio_entrega = models.ForeignKey('Municipio', on_delete=models.CASCADE)
    referencia_entrega = models.TextField(blank=True, help_text="Referencias para llegar al lugar")
    
    # Contacto
    nombre_contacto = models.CharField(max_length=100)
    telefono_contacto = models.CharField(max_length=15)
    
    # ============= CAMPOS ADICIONALES PARA EXCEL =============
    
    # Nombres separados (además de nombre_contacto que ya tienes)
    nombres_cliente = models.CharField(max_length=100, blank=True)
    apellidos_cliente = models.CharField(max_length=100, blank=True)
    
    # Datos de facturación
    nit_facturacion = models.CharField(max_length=20, blank=True)
    nombre_facturacion = models.CharField(max_length=200, blank=True)
    direccion_facturacion = models.TextField(blank=True)
    
    # Centro Poblado (adicional a municipio_entrega)
    centro_poblado = models.CharField(max_length=200, blank=True, help_text="Aldea, caserío, barrio, etc.")
    direccion_compuesta = models.TextField(blank=True, help_text="Dirección completa formateada")
    
    # Información de pago
    TIPOS_PAGO = [
        ('transferencia', 'Transferencia'),
        ('contra_entrega', 'Pago Contra Entrega'),
        ('efectivo', 'Efectivo'),
        ('tarjeta', 'Tarjeta'),
    ]
    tipo_pago = models.CharField(max_length=20, choices=TIPOS_PAGO, default='transferencia')
    comentario_pago = models.TextField(blank=True)
    numero_deposito = models.CharField(max_length=50, blank=True, help_text="No. de depósito bancario")
    fecha_deposito = models.DateField(null=True, blank=True)
    monto_deposito = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Comprobante de pago (imagen)
    comprobante_pago = models.ImageField(upload_to='comprobantes/%Y/%m/', null=True, blank=True)
    
    # Información de viaje/logística
    pendiente_viaje = models.BooleanField(default=True, help_text="¿Está pendiente de programar viaje?")
    fecha_viaje = models.DateField(null=True, blank=True)
    link_pendientes = models.URLField(max_length=500, blank=True, help_text="Link a hoja de pendientes")
    
    # Gestión interna
    vendedor = models.ForeignKey(
        'Usuario', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='pedidos_vendedor',
        help_text="Usuario que realizó la venta"
    )
    tecnico_encargado = models.ForeignKey(
        'Usuario', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='pedidos_tecnico',
        help_text="Técnico asignado"
    )
    orden_cerrada = models.BooleanField(default=False, help_text="¿La orden está completamente cerrada?")
    comentarios_internos = models.TextField(blank=True, help_text="Comentarios adicionales del equipo")
    
    # ============= FIN CAMPOS ADICIONALES =============
    
    # Valores
    total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    descuento = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    # Observaciones (ya existente - se mantiene para comentarios de entrega)
    observaciones = models.TextField(blank=True)
    observaciones_internas = models.TextField(blank=True, help_text="Solo visible para personal")
    
    # Canal de origen
    CANALES = [
        ('telefono', 'Teléfono'),
        ('whatsapp', 'WhatsApp'),
        ('presencial', 'Presencial'),
        ('app_movil', 'App Móvil'),
        ('web', 'Web'),
    ]
    canal_origen = models.CharField(max_length=20, choices=CANALES, default='telefono')
    
    # Calificación del cliente
    calificacion = models.IntegerField(null=True, blank=True, help_text="Calificación de 1 a 5")
    comentario_calificacion = models.TextField(blank=True)
    
    activo = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.codigo_seguimiento:
            # Generar código único: PED-YYYYMMDD-XXXX
            from datetime import datetime
            fecha = datetime.now().strftime('%Y%m%d')
            
            # Obtener el último número de secuencia usado hoy
            ultimo_pedido = Pedido.objects.filter(
                codigo_seguimiento__startswith=f'PED-{fecha}'
            ).order_by('-codigo_seguimiento').first()
            
            if ultimo_pedido:
                # Extraer el número del último código
                ultimo_numero = int(ultimo_pedido.codigo_seguimiento.split('-')[-1])
                nuevo_numero = ultimo_numero + 1
            else:
                nuevo_numero = 1
            
            self.codigo_seguimiento = f'PED-{fecha}-{nuevo_numero:04d}'
        
        # Auto-completar dirección compuesta si está vacía
        if not self.direccion_compuesta and self.direccion_entrega:
            partes = [
                self.direccion_entrega,
                self.centro_poblado if self.centro_poblado else '',
                self.municipio_entrega.nombre if self.municipio_entrega else '',
                self.municipio_entrega.departamento.nombre if self.municipio_entrega and self.municipio_entrega.departamento else ''
            ]
            self.direccion_compuesta = ', '.join(filter(None, partes))
        
        super().save(*args, **kwargs)

    def __str__(self):
        nombre = f"{self.nombres_cliente} {self.apellidos_cliente}".strip() or self.nombre_contacto
        return f"{self.codigo_seguimiento} - {nombre}"

    def calcular_total(self):
        subtotal = sum(detalle.cantidad * detalle.precio_unitario for detalle in self.detallepedido_set.all())
        return subtotal - self.descuento
    
    def get_cantidad_total_plantas(self):
        """Retorna la cantidad total de plantas en el pedido"""
        return sum(detalle.cantidad for detalle in self.detallepedido_set.all())

    class Meta:
        db_table = 'pedido'
        ordering = ['-fecha_pedido']


class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    pilon = models.ForeignKey('CatalogoPilon', on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'detalle_pedido'

    def __str__(self):
        return f"{self.pilon.nombre_variedad} x{self.cantidad}"


class HistorialEstadoPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='historial_estados')
    estado_anterior = models.CharField(max_length=20, choices=ESTADOS_PEDIDO, null=True, blank=True)
    estado_nuevo = models.CharField(max_length=20, choices=ESTADOS_PEDIDO)
    fecha_cambio = models.DateTimeField(auto_now_add=True)
    usuario_cambio = models.ForeignKey('Usuario', on_delete=models.SET_NULL, null=True)
    comentario = models.TextField(blank=True)

    class Meta:
        ordering = ['-fecha_cambio']
        db_table = 'historial_estado_pedido'

    def __str__(self):
        return f"{self.pedido.codigo_seguimiento}: {self.estado_anterior} → {self.estado_nuevo}"