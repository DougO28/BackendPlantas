from rest_framework import serializers
from webplantas.models import CategoriaPlanta, CatalogoPilon


class CategoriaPlantaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaPlanta
        fields = ['id', 'nombre', 'descripcion', 'activo']


class CatalogoPilonSerializer(serializers.ModelSerializer):
    categoria = CategoriaPlantaSerializer(read_only=True)
    categoria_id = serializers.PrimaryKeyRelatedField(
        queryset=CategoriaPlanta.objects.all(),
        source='categoria',
        write_only=True
    )
    
    # Aliases para compatibilidad con frontend
    nombre_comun = serializers.CharField(source='nombre_variedad', read_only=True)
    cantidad_disponible = serializers.IntegerField(source='stock', read_only=True)
    tiempo_crecimiento_dias = serializers.IntegerField(source='tiempo_produccion', read_only=True)
    unidad_medida = serializers.SerializerMethodField()
    codigo_pilon = serializers.SerializerMethodField()
    foto = serializers.SerializerMethodField()
    
    class Meta:
        model = CatalogoPilon
        fields = [
            'id',
            'nombre_variedad',
            'nombre_comun',  # Alias
            'categoria',
            'categoria_id',
            'descripcion',
            'precio_unitario',
            'tiempo_produccion',
            'tiempo_crecimiento_dias',  # Alias
            'stock',
            'cantidad_disponible',  # Alias
            'stock_minimo',
            'unidad_medida',
            'codigo_pilon',
            'foto',
            'activo',
            'fecha_creacion',
            'fecha_actualizacion',
        ]
        read_only_fields = ['fecha_creacion', 'fecha_actualizacion']
    
    def get_unidad_medida(self, obj):
        return 'unidad'
    
    def get_codigo_pilon(self, obj):
        return f'PIL-{obj.id:04d}'
    
    def get_foto(self, obj):
        return None  # Por ahora, puedes agregar campo de foto después


class CatalogoPilonListSerializer(serializers.ModelSerializer):
    """Serializer para listar catálogo (versión resumida)"""
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    nombre_comun = serializers.CharField(source='nombre_variedad', read_only=True)
    cantidad_disponible = serializers.IntegerField(source='stock', read_only=True)
    
    class Meta:
        model = CatalogoPilon
        fields = [
            'id',
            'nombre_variedad',
            'nombre_comun',
            'categoria_nombre',
            'precio_unitario',
            'stock',
            'cantidad_disponible',
            'activo',
        ]


class CatalogoPilonCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer para crear/actualizar"""
    categoria_id = serializers.PrimaryKeyRelatedField(
        queryset=CategoriaPlanta.objects.all(),
        source='categoria'
    )
    
    class Meta:
        model = CatalogoPilon
        fields = [
            'nombre_variedad',
            'categoria_id',
            'descripcion',
            'precio_unitario',
            'tiempo_produccion',
            'stock',
            'stock_minimo',
            'activo',
        ]