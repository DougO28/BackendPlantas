from rest_framework import serializers
from webplantas.models import Usuario, Rol, UsuarioRol


class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = ['id', 'nombre_rol', 'descripcion']


class UsuarioListSerializer(serializers.ModelSerializer):
    """Serializer para listar usuarios (datos básicos)"""
    roles = RolSerializer(many=True, read_only=True)
    municipio_nombre = serializers.CharField(source='municipio.nombre', read_only=True)
    
    class Meta:
        model = Usuario
        fields = [
            'id', 'nombre_completo', 'email', 'telefono', 
            'activo', 'municipio_nombre', 'roles', 'fecha_registro'
        ]


class UsuarioDetailSerializer(serializers.ModelSerializer):
    """Serializer para detalles completos del usuario"""
    roles = RolSerializer(many=True, read_only=True)
    municipio_nombre = serializers.CharField(source='municipio.nombre', read_only=True)
    
    class Meta:
        model = Usuario
        fields = [
            'id', 'nombre_completo', 'email', 'telefono', 'direccion',
            'municipio', 'municipio_nombre', 'activo', 'roles', 
            'fecha_registro', 'ultimo_acceso'
        ]


class UsuarioCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear usuarios"""
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = Usuario
        fields = [
            'nombre_completo', 'email', 'telefono', 'direccion',
            'municipio', 'password'
        ]
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = Usuario(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UsuarioUpdateSerializer(serializers.ModelSerializer):
    """Serializer para actualizar usuarios"""
    class Meta:
        model = Usuario
        fields = ['nombre_completo', 'telefono', 'direccion', 'municipio']