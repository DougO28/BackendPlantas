from django.db import models


class Departamento(models.Model):
    nombre = models.CharField(max_length=100)
    region = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'departamento'


class Municipio(models.Model):
    nombre = models.CharField(max_length=100)
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'municipio'


class Parcela(models.Model):
    usuario = models.ForeignKey('Usuario', on_delete=models.CASCADE, related_name='parcelas')
    municipio = models.ForeignKey(Municipio, on_delete=models.CASCADE)
    nombre_parcela = models.CharField(max_length=100)
    direccion = models.CharField(max_length=250)
    area_hectareas = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    tipo_cultivo = models.CharField(max_length=100, blank=True)
    activa = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    observaciones = models.TextField(blank=True)

    def __str__(self):
        return f"{self.nombre_parcela} - {self.usuario.nombre_completo}"

    class Meta:
        db_table = 'parcela'