# Backend/webplantas/serializers/catalogos_logistica.py
from rest_framework import serializers
from webplantas.models import (
    Transportista, DocumentoVehiculo, PuntoSiembra, Finca
)


class TransportistaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transportista
        fields = '__all__'


class DocumentoVehiculoSerializer(serializers.ModelSerializer):
    vehiculo_placa = serializers.CharField(source='vehiculo.placa', read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    esta_vencido = serializers.BooleanField(read_only=True)
    dias_para_vencer = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = DocumentoVehiculo
        fields = '__all__'


class PuntoSiembraSerializer(serializers.ModelSerializer):
    departamento_nombre = serializers.CharField(source='departamento.nombre', read_only=True)
    municipio_nombre = serializers.CharField(source='municipio.nombre', read_only=True)
    
    class Meta:
        model = PuntoSiembra
        fields = '__all__'


class FincaSerializer(serializers.ModelSerializer):
    departamento_nombre = serializers.CharField(source='departamento.nombre', read_only=True)
    municipio_nombre = serializers.CharField(source='municipio.nombre', read_only=True)
    usuario_nombre = serializers.CharField(source='usuario.nombre_completo', read_only=True, allow_null=True)
    
    class Meta:
        model = Finca
        fields = '__all__'