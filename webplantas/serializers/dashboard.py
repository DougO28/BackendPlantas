# Backend/webplantas/serializers/dashboard.py
from rest_framework import serializers


class EstadisticasVentasSerializer(serializers.Serializer):
    """Serializer para estadísticas de ventas"""
    total_ventas_hoy = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_ventas_semana = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_ventas_mes = serializers.DecimalField(max_digits=12, decimal_places=2)
    
    pedidos_hoy = serializers.IntegerField()
    pedidos_semana = serializers.IntegerField()
    pedidos_mes = serializers.IntegerField()
    
    pedidos_por_estado = serializers.DictField()
    

class ProductoMasVendidoSerializer(serializers.Serializer):
    """Serializer para productos más vendidos"""
    pilon_id = serializers.IntegerField()
    nombre_variedad = serializers.CharField()
    categoria = serializers.CharField()
    cantidad_vendida = serializers.IntegerField()
    total_vendido = serializers.DecimalField(max_digits=12, decimal_places=2)


class StockBajoSerializer(serializers.Serializer):
    """Serializer para productos con stock bajo"""
    id = serializers.IntegerField()
    nombre_variedad = serializers.CharField()
    categoria = serializers.CharField()
    stock = serializers.IntegerField()
    stock_minimo = serializers.IntegerField()
    porcentaje_stock = serializers.FloatField()


class VentasDiariaSerializer(serializers.Serializer):
    """Serializer para ventas por día"""
    fecha = serializers.DateField()
    total = serializers.DecimalField(max_digits=12, decimal_places=2)
    cantidad_pedidos = serializers.IntegerField()