from django.db import models


class CategoriaPlanta(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'categoria_planta'


class CatalogoPilon(models.Model):
    nombre_variedad = models.CharField(max_length=100)
    categoria = models.ForeignKey(CategoriaPlanta, on_delete=models.CASCADE)
    descripcion = models.TextField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    tiempo_produccion = models.IntegerField(help_text="Días de producción")
    stock = models.IntegerField(default=0)
    stock_minimo = models.IntegerField(default=10)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre_variedad

    class Meta:
        db_table = 'catalogo_pilon'