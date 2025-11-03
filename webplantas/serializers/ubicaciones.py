from rest_framework import serializers
from webplantas.models import Departamento, Municipio, Parcela


class DepartamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Departamento
        fields = '__all__'


class MunicipioSerializer(serializers.ModelSerializer):
    departamento_nombre = serializers.CharField(source='departamento.nombre', read_only=True)
    
    class Meta:
        model = Municipio
        fields = ['id', 'nombre', 'departamento', 'departamento_nombre']


class ParcelaSerializer(serializers.ModelSerializer):
    municipio = MunicipioSerializer(read_only=True)
    usuario_nombre = serializers.CharField(source='usuario.nombre_completo', read_only=True)
    
    class Meta:
        model = Parcela
        fields = '__all__'