# Backend/webplantas/serializers/logistica.py
from rest_framework import serializers
from webplantas.models import RutaEntrega, PedidoRuta, Vehiculo
from .pedidos import PedidoListSerializer
from .usuarios import UsuarioListSerializer


class VehiculoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehiculo
        fields = '__all__'


class PedidoRutaSerializer(serializers.ModelSerializer):
    """Serializer para pedidos dentro de una ruta"""
    pedido = PedidoListSerializer(read_only=True)
    pedido_codigo = serializers.CharField(source='pedido.codigo_seguimiento', read_only=True)
    
    class Meta:
        model = PedidoRuta
        fields = [
            'id', 'pedido', 'pedido_codigo', 'orden_entrega',
            'entregado', 'hora_llegada', 'hora_salida',
            'receptor_nombre', 'receptor_documento', 'observaciones_entrega'
        ]


class RutaEntregaListSerializer(serializers.ModelSerializer):
    """Para listar rutas (vista resumida)"""
    tecnico_nombre = serializers.CharField(source='tecnico_campo.nombre_completo', read_only=True)
    vehiculo_placa = serializers.CharField(source='vehiculo.placa', read_only=True, allow_null=True)
    vehiculo_detalle = VehiculoSerializer(source='vehiculo', read_only=True)  # ✅ AGREGAR
    departamento_nombre = serializers.CharField(source='departamento.nombre', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    total_pedidos = serializers.SerializerMethodField()  # ✅ CAMBIAR nombre
    pedidos_entregados = serializers.SerializerMethodField()  # ✅ AGREGAR
    
    class Meta:
        model = RutaEntrega
        fields = [
            'id', 'codigo_ruta', 'nombre_ruta', 
            'tecnico_campo', 'tecnico_nombre',  # ✅ AGREGAR tecnico_campo (id)
            'vehiculo', 'vehiculo_placa', 'vehiculo_detalle',  # ✅ AGREGAR vehiculo (id)
            'fecha_planificada', 'fecha_inicio', 'fecha_fin',  # ✅ AGREGAR fechas
            'estado', 'estado_display',
            'departamento', 'departamento_nombre',  # ✅ AGREGAR departamento (id)
            'total_pedidos', 'pedidos_entregados',  # ✅ CAMBIAR
            'observaciones'  # ✅ AGREGAR
        ]
    
    def get_total_pedidos(self, obj):
        return obj.pedidos.count()
    
    def get_pedidos_entregados(self, obj):  # ✅ AGREGAR
        return obj.pedidos.filter(entregado=True).count()


class RutaEntregaDetailSerializer(serializers.ModelSerializer):
    """Para detalles completos de la ruta"""
    tecnico_campo = UsuarioListSerializer(read_only=True)
    tecnico_nombre = serializers.CharField(source='tecnico_campo.nombre_completo', read_only=True)  # ✅ AGREGAR
    vehiculo = VehiculoSerializer(read_only=True)
    vehiculo_detalle = VehiculoSerializer(source='vehiculo', read_only=True)  # ✅ AGREGAR
    pedidos = PedidoRutaSerializer(many=True, read_only=True)
    departamento_nombre = serializers.CharField(source='departamento.nombre', read_only=True)
    total_pedidos = serializers.SerializerMethodField()  # ✅ AGREGAR
    pedidos_entregados = serializers.SerializerMethodField()  # ✅ AGREGAR
    
    class Meta:
        model = RutaEntrega
        fields = '__all__'
    
    def get_total_pedidos(self, obj):  # ✅ AGREGAR
        return obj.pedidos.count()
    
    def get_pedidos_entregados(self, obj):  # ✅ AGREGAR
        return obj.pedidos.filter(entregado=True).count()


class RutaEntregaCreateSerializer(serializers.ModelSerializer):
    """Para crear rutas"""
    pedidos_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = RutaEntrega
        fields = [
            'nombre_ruta', 'tecnico_campo', 'vehiculo',
            'fecha_planificada', 'departamento', 'observaciones',
            'pedidos_ids'
        ]
    
    def create(self, validated_data):
        pedidos_ids = validated_data.pop('pedidos_ids', [])
        ruta = RutaEntrega.objects.create(**validated_data)
        
        # Asignar pedidos a la ruta
        from webplantas.models import Pedido
        for idx, pedido_id in enumerate(pedidos_ids):
            try:
                pedido = Pedido.objects.get(id=pedido_id)
                PedidoRuta.objects.create(
                    ruta=ruta,
                    pedido=pedido,
                    orden_entrega=idx + 1
                )
            except Pedido.DoesNotExist:
                pass
        
        return ruta


class ConfirmarEntregaSerializer(serializers.Serializer):
    """Serializer para confirmar entrega de un pedido en ruta"""
    receptor_nombre = serializers.CharField(max_length=100)
    receptor_documento = serializers.CharField(max_length=20, required=False)
    observaciones_entrega = serializers.CharField(required=False, allow_blank=True)