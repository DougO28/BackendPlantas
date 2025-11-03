from django.db import models

ESTADOS_RUTA = [
    ('planificada', 'Planificada'),
    ('en_progreso', 'En Progreso'),
    ('completada', 'Completada'),
    ('cancelada', 'Cancelada'),
]


class RutaEntrega(models.Model):
    """Agrupación de pedidos para un técnico de campo"""
    
    # Identificación
    codigo_ruta = models.CharField(max_length=20, unique=True, editable=False)
    nombre_ruta = models.CharField(max_length=100, help_text="Ej: Ruta Quiché Norte - 15/01/2025")
    
    # Asignación
    tecnico_campo = models.ForeignKey('Usuario', on_delete=models.CASCADE, related_name='rutas_asignadas')
    vehiculo = models.ForeignKey('Vehiculo', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Fechas
    fecha_planificada = models.DateField()
    fecha_inicio = models.DateTimeField(null=True, blank=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)
    
    # Estado
    estado = models.CharField(max_length=20, choices=ESTADOS_RUTA, default='planificada')
    
    # Zona geográfica
    departamento = models.ForeignKey('Departamento', on_delete=models.CASCADE)
    
    # Observaciones
    observaciones = models.TextField(blank=True)
    
    class Meta:
        db_table = 'ruta_entrega'
        ordering = ['-fecha_planificada']
    
    def save(self, *args, **kwargs):
        if not self.codigo_ruta:
            from datetime import datetime
            fecha = datetime.now().strftime('%Y%m%d')
            ultimo = RutaEntrega.objects.filter(codigo_ruta__startswith=f'RUT-{fecha}').count()
            self.codigo_ruta = f'RUT-{fecha}-{ultimo+1:04d}'
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.codigo_ruta} - {self.nombre_ruta}"


class PedidoRuta(models.Model):
    """Relación entre pedidos y rutas con orden de entrega"""
    
    ruta = models.ForeignKey(RutaEntrega, on_delete=models.CASCADE, related_name='pedidos')
    pedido = models.ForeignKey('Pedido', on_delete=models.CASCADE)
    orden_entrega = models.PositiveIntegerField(default=0, help_text="Orden en la ruta")
    
    # Estado específico de la entrega
    hora_llegada = models.TimeField(null=True, blank=True)
    hora_salida = models.TimeField(null=True, blank=True)
    entregado = models.BooleanField(default=False)
    
    # Confirmación de entrega
    receptor_nombre = models.CharField(max_length=100, blank=True)
    receptor_documento = models.CharField(max_length=20, blank=True)
    firma_digital = models.TextField(blank=True, help_text="Base64 de la firma")
    foto_entrega = models.CharField(max_length=500, blank=True, help_text="URL de la foto")
    
    observaciones_entrega = models.TextField(blank=True)
    
    class Meta:
        db_table = 'pedido_ruta'
        ordering = ['orden_entrega']
        unique_together = ('ruta', 'pedido')
    
    def __str__(self):
        return f"Orden {self.orden_entrega}: {self.pedido.codigo_seguimiento}"


class Vehiculo(models.Model):
    placa = models.CharField(max_length=10, unique=True)
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    año = models.IntegerField(null=True, blank=True)
    capacidad_carga_kg = models.DecimalField(max_digits=10, decimal_places=2)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.placa} - {self.marca} {self.modelo}"

    class Meta:
        db_table = 'vehiculo'