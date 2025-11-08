from django.db import models
from django.core.exceptions import ValidationError
from decimal import Decimal

ESTADOS_RUTA = [
    ('planificada', 'Planificada'),
    ('asignada', 'Asignada'),  
    ('en_progreso', 'En Progreso'),
    ('en_transito', 'En Tránsito'),  
    ('entregando', 'Entregando'),  
    ('completada', 'Completada'),
    ('cancelada', 'Cancelada'),
]

ETIQUETAS_RUTA = [
    ('terraceria', 'Terracería'),
    ('lluvia', 'Lluvia'),
    ('fragil', 'Frágil'),
    ('prioritario', 'Prioritario'),
]


# TRANSPORTISTAS 
class Transportista(models.Model):
    """Proveedores externos de transporte"""
    nombre = models.CharField(max_length=100)
    contacto = models.CharField(max_length=100, help_text="Nombre de contacto")
    telefono = models.CharField(max_length=15)
    email = models.EmailField(blank=True)
    nit = models.CharField(max_length=20, blank=True)
    observaciones = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'transportista'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


# ============= VEHÍCULOS  
class Vehiculo(models.Model):
    """Vehículos para rutas de entrega"""
    TIPOS_VEHICULO = [
        ('camion', 'Camión'),
        ('pickup', 'Pickup'),
        ('panel', 'Panel'),
    ]
    
    
    placa = models.CharField(max_length=10, unique=True)
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    año = models.IntegerField(null=True, blank=True)
    capacidad_carga_kg = models.DecimalField(max_digits=10, decimal_places=2)
    activo = models.BooleanField(default=True)
    
    #  NUEVOS campos
    tipo = models.CharField(max_length=20, choices=TIPOS_VEHICULO, default='camion')
    
    # Transportista (proveedor)
    transportista = models.ForeignKey(
        Transportista, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='vehiculos'
    )
    
    # Capacidades adicionales
    capacidad_volumen_m3 = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Capacidad en metros cúbicos"
    )
    
    # Dimensiones (LxAxH en metros)
    largo_m = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    ancho_m = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    alto_m = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Observaciones
    observaciones = models.TextField(blank=True, help_text="Ej: 'No entra en terracería pesada'")
    
    class Meta:
        db_table = 'vehiculo'
        ordering = ['placa']

    def __str__(self):
        return f"{self.placa} - {self.marca} {self.modelo}"
    
    @property
    def dimensiones_str(self):
        if self.largo_m and self.ancho_m and self.alto_m:
            return f"{self.largo_m}×{self.ancho_m}×{self.alto_m}m"
        return "No especificado"


# ============= DOCUMENTOS DE VEHÍCULOS 
class DocumentoVehiculo(models.Model):
    """Documentos de vehículos (póliza, RTV, etc.)"""
    TIPOS_DOCUMENTO = [
        ('poliza', 'Póliza de Seguro'),
        ('rtv', 'Revisión Técnica Vehicular'),
        ('licencia', 'Licencia de Conducir'),
        ('otro', 'Otro'),
    ]
    
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE, related_name='documentos')
    tipo = models.CharField(max_length=20, choices=TIPOS_DOCUMENTO)
    numero_documento = models.CharField(max_length=50, blank=True)
    fecha_emision = models.DateField()
    fecha_vencimiento = models.DateField()
    archivo = models.FileField(upload_to='documentos_vehiculos/%Y/%m/', null=True, blank=True)
    observaciones = models.TextField(blank=True)
    
    class Meta:
        db_table = 'documento_vehiculo'
        ordering = ['fecha_vencimiento']
    
    def __str__(self):
        return f"{self.vehiculo.placa} - {self.get_tipo_display()}"
    
    @property
    def esta_vencido(self):
        from datetime import date
        return date.today() > self.fecha_vencimiento
    
    @property
    def dias_para_vencer(self):
        from datetime import date
        delta = self.fecha_vencimiento - date.today()
        return delta.days


# ============= PUNTOS DE ORIGEN 
class PuntoSiembra(models.Model):
    """Puntos de origen (viveros/siembra)"""
    nombre = models.CharField(max_length=100)
    contacto = models.CharField(max_length=100)
    telefono = models.CharField(max_length=15)
    departamento = models.ForeignKey('Departamento', on_delete=models.CASCADE)
    municipio = models.ForeignKey('Municipio', on_delete=models.CASCADE)
    aldea_colonia = models.CharField(max_length=100, blank=True)
    referencia_ubicacion = models.TextField(help_text="Referencia corta de ubicación")
    activo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'punto_siembra'
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.nombre} ({self.municipio.nombre})"


# ============= FINCAS/VIVEROS DESTINO 
class Finca(models.Model):
    """Fincas/viveros destino"""
    nombre = models.CharField(max_length=100)
    contacto = models.CharField(max_length=100)
    telefono = models.CharField(max_length=15)
    email = models.EmailField(blank=True)
    departamento = models.ForeignKey('Departamento', on_delete=models.CASCADE)
    municipio = models.ForeignKey('Municipio', on_delete=models.CASCADE)
    aldea_colonia = models.CharField(max_length=100, blank=True)
    direccion_completa = models.TextField()
    referencia_ubicacion = models.TextField(help_text="Referencia corta de ubicación")
    
    # Usuario propietario (opcional)
    usuario = models.ForeignKey(
        'Usuario', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='fincas'
    )
    
    activo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'finca'
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.nombre} ({self.municipio.nombre})"


# ============= RUTAS AMPLIADAS 
class RutaEntrega(models.Model):
    """Agrupación de pedidos para un técnico de campo"""
    
    #  Campos  
    codigo_ruta = models.CharField(max_length=20, unique=True, editable=False)
    nombre_ruta = models.CharField(max_length=100, help_text="Ej: Ruta Quiché Norte - 15/01/2025")
    tecnico_campo = models.ForeignKey('Usuario', on_delete=models.CASCADE, related_name='rutas_asignadas')
    vehiculo = models.ForeignKey('Vehiculo', on_delete=models.SET_NULL, null=True, blank=True)
    fecha_planificada = models.DateField()
    fecha_inicio = models.DateTimeField(null=True, blank=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS_RUTA, default='planificada')
    departamento = models.ForeignKey('Departamento', on_delete=models.CASCADE)
    observaciones = models.TextField(blank=True)
    
    # NUEVOS campos
    operador_responsable = models.ForeignKey(
        'Usuario', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='rutas_operadas',
        help_text="Operador que gestiona la ruta"
    )
    
    # Origen general 
    punto_origen = models.ForeignKey(
        PuntoSiembra, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    
    # Totales calculados
    peso_total_kg = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Peso total en kg"
    )
    volumen_total_m3 = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Volumen total en m³"
    )
    
    # Kilometraje
    km_estimados = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Kilómetros estimados de la ruta"
    )
    
    # Etiquetas (JSON field para flexibilidad)
    etiquetas = models.JSONField(default=list, blank=True, help_text="Lista de etiquetas aplicadas")
    
    # Ruta plantilla (para duplicar)
    ruta_plantilla = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="Ruta desde la cual se duplicó esta"
    )
    
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
    
    def validar_capacidad(self):
        """Valida que el vehículo tenga capacidad suficiente"""
        if not self.vehiculo:
            return True, "No hay vehículo asignado"
        
        errores = []
        
        if self.peso_total_kg > self.vehiculo.capacidad_carga_kg:
            errores.append(
                f"Peso excede capacidad: {self.peso_total_kg}kg > {self.vehiculo.capacidad_carga_kg}kg"
            )
        
        if self.vehiculo.capacidad_volumen_m3 and self.volumen_total_m3 > self.vehiculo.capacidad_volumen_m3:
            errores.append(
                f"Volumen excede capacidad: {self.volumen_total_m3}m³ > {self.vehiculo.capacidad_volumen_m3}m³"
            )
        
        if errores:
            return False, " | ".join(errores)
        return True, "Capacidad OK"


# ============= PARADAS/ENTREGAS AMPLIADAS
class PedidoRuta(models.Model):
    """Relación entre pedidos y rutas con orden de entrega (PARADAS)"""
    
    # Campos
    ruta = models.ForeignKey(RutaEntrega, on_delete=models.CASCADE, related_name='pedidos')
    pedido = models.ForeignKey('Pedido', on_delete=models.CASCADE)
    orden_entrega = models.PositiveIntegerField(default=0, help_text="Orden en la ruta (parada)")
    entregado = models.BooleanField(default=False)
    receptor_nombre = models.CharField(max_length=100, blank=True)
    receptor_documento = models.CharField(max_length=20, blank=True)
    firma_digital = models.TextField(blank=True, help_text="Base64 de la firma")
    observaciones_entrega = models.TextField(blank=True)
    
    #  MODIFICAR: Cambiar TimeField a DateTimeField para mayor precisión
    hora_llegada = models.DateTimeField(null=True, blank=True)
    hora_salida = models.DateTimeField(null=True, blank=True)
    
    #  MODIFICAR: Cambiar CharField a ImageField para fotos
    foto_entrega = models.ImageField(upload_to='entregas/%Y/%m/', null=True, blank=True)
    
    #  NUEVOS campos
    # Peso/volumen estimado (del pedido)
    peso_estimado_kg = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00')
    )
    volumen_estimado_m3 = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00')
    )
    
    # Prioridad de la parada
    prioridad = models.IntegerField(default=5, help_text="1=Alta, 5=Normal, 10=Baja")
    
    # Ventana horaria sugerida
    ventana_inicio = models.TimeField(null=True, blank=True, help_text="Hora inicio sugerida")
    ventana_fin = models.TimeField(null=True, blank=True, help_text="Hora fin sugerida")
    
    class Meta:
        db_table = 'pedido_ruta'
        ordering = ['orden_entrega']
        unique_together = ('ruta', 'pedido')
    
    def __str__(self):
        return f"Parada {self.orden_entrega}: {self.pedido.codigo_seguimiento}"