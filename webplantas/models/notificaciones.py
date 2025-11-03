from django.db import models


class Notificacion(models.Model):
    TIPOS_NOTIFICACION = [
        ('pedido_confirmado', 'Pedido Confirmado'),
        ('cambio_estado', 'Cambio de Estado'),
        ('ruta_asignada', 'Ruta Asignada'),
        ('entrega_realizada', 'Entrega Realizada'),
        ('stock_bajo', 'Stock Bajo'),
        ('sistema', 'Sistema'),
    ]
    
    usuario = models.ForeignKey('Usuario', on_delete=models.CASCADE, related_name='notificaciones')
    tipo = models.CharField(max_length=20, choices=TIPOS_NOTIFICACION)
    titulo = models.CharField(max_length=100)
    mensaje = models.TextField()
    leida = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    # Referencias opcionales
    pedido = models.ForeignKey('Pedido', on_delete=models.CASCADE, null=True, blank=True)
    ruta = models.ForeignKey('RutaEntrega', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        ordering = ['-fecha_creacion']
        db_table = 'notificacion'

    def __str__(self):
        return f"{self.usuario.nombre_completo} - {self.titulo}"