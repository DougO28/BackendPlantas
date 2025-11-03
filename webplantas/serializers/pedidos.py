from rest_framework import serializers
from webplantas.models import Pedido, DetallePedido, HistorialEstadoPedido
from .usuarios import UsuarioListSerializer
from .ubicaciones import MunicipioSerializer


class DetallePedidoSerializer(serializers.ModelSerializer):
    pilon_nombre = serializers.CharField(source='pilon.nombre_variedad', read_only=True)
    precio_unitario_actual = serializers.DecimalField(source='pilon.precio_unitario', max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = DetallePedido
        fields = [
            'id', 'pilon', 'pilon_nombre', 'cantidad', 
            'precio_unitario', 'precio_unitario_actual', 'subtotal'
        ]
        read_only_fields = ['subtotal']


class HistorialEstadoSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(source='usuario_cambio.nombre_completo', read_only=True)
    
    class Meta:
        model = HistorialEstadoPedido
        fields = [
            'id', 'estado_anterior', 'estado_nuevo', 'fecha_cambio',
            'usuario_nombre', 'comentario'
        ]


class PedidoListSerializer(serializers.ModelSerializer):
    """Para listar pedidos (vista resumida)"""
    usuario_nombre = serializers.CharField(source='usuario.nombre_completo', read_only=True)
    municipio_entrega_nombre = serializers.CharField(source='municipio_entrega.nombre', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    cantidad_items = serializers.SerializerMethodField()
    detalles = DetallePedidoSerializer(source='detallepedido_set', many=True, read_only=True)  # ✅ DEBE ESTAR AQUÍ
    
    class Meta:
        model = Pedido
        fields = [
            'id', 'codigo_seguimiento', 'usuario_nombre', 'estado', 'estado_display', 
            'fecha_pedido', 'fecha_entrega_estimada', 'total', 
            'municipio_entrega_nombre', 'cantidad_items', 'canal_origen',
            'detalles',  # ✅ DEBE ESTAR AQUÍ
        ]
    
    def get_cantidad_items(self, obj):
        return obj.detallepedido_set.count()


class PedidoDetailSerializer(serializers.ModelSerializer):
    """Para detalles completos del pedido"""
    usuario = UsuarioListSerializer(read_only=True)
    municipio_entrega = MunicipioSerializer(read_only=True)
    detalles = DetallePedidoSerializer(source='detallepedido_set', many=True, read_only=True)
    historial = HistorialEstadoSerializer(source='historial_estados', many=True, read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    
    class Meta:
        model = Pedido
        fields = '__all__'


class PedidoCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear pedidos - CON TODOS LOS CAMPOS"""
    detalles = DetallePedidoSerializer(many=True)
    
    class Meta:
        model = Pedido
        fields = [
            # Información de contacto
            'nombres_cliente',
            'apellidos_cliente',
            'nombre_contacto',
            'telefono_contacto',
            # Datos de facturación
            'nit_facturacion',
            'nombre_facturacion',
            'direccion_facturacion',
            # Dirección de entrega
            'direccion_entrega',
            'centro_poblado',
            'municipio_entrega',
            'referencia_entrega',
            # Información de pago
            'tipo_pago',
            'comentario_pago',
            'numero_deposito',
            'fecha_deposito',
            'monto_deposito',
            'comprobante_pago',
            # Observaciones
            'observaciones',
            # Canal
            'canal_origen',
            # Detalles
            'detalles',
        ]
    
    def validate_detalles(self, value):
        if not value:
            raise serializers.ValidationError("Debe incluir al menos un producto")
        
        # Validar stock disponible
        for detalle in value:
            pilon = detalle['pilon']
            cantidad = detalle['cantidad']
            if pilon.stock < cantidad:
                raise serializers.ValidationError(
                    f"Stock insuficiente para {pilon.nombre_variedad}. "
                    f"Disponible: {pilon.stock}, Solicitado: {cantidad}"
                )
        
        return value
    
    def create(self, validated_data):
        # Extraer detalles antes de crear el pedido
        detalles_data = validated_data.pop('detalles')
        
        # Crear el pedido (el usuario ya viene en validated_data)
        pedido = Pedido.objects.create(**validated_data)
        
        print(f"✅ Pedido creado: {pedido.codigo_seguimiento}")  # Debug
        print(f"📦 Detalles a crear: {len(detalles_data)}")  # Debug
        
        # Crear los detalles y actualizar stock
        total = 0
        for detalle_data in detalles_data:
            pilon = detalle_data['pilon']
            cantidad = detalle_data['cantidad']
            
            # Obtener el precio del detalle o del pilón
            if 'precio_unitario' in detalle_data and detalle_data['precio_unitario']:
                precio = float(detalle_data['precio_unitario'])
            else:
                precio = float(pilon.precio_unitario)
            
            subtotal = cantidad * precio
            
            # Crear el detalle
            DetallePedido.objects.create(
                pedido=pedido,
                pilon=pilon,
                cantidad=cantidad,
                precio_unitario=precio,
                subtotal=subtotal
            )
            
            print(f"  ✓ Detalle creado: {pilon.nombre_variedad} x{cantidad} = Q{subtotal}")  # Debug
            # Actualizar stock del pilón
            pilon.stock -= cantidad
            pilon.save()
            print(f"  ✓ Stock actualizado: {pilon.nombre_variedad} ahora tiene {pilon.stock} unidades")  # Debug
            
            
            total += subtotal
        
        # Actualizar el total del pedido
        pedido.total = total
        pedido.save()
        
        print(f"✅ Total del pedido: Q{total}")  # Debug
        
        return pedido


class CambiarEstadoPedidoSerializer(serializers.Serializer):
    """Serializer para cambiar estado de pedido"""
    estado = serializers.ChoiceField(choices=[
        'recibido', 'confirmado', 'en_preparacion', 'listo_entrega',
        'en_ruta', 'entregado', 'cancelado'
    ])
    comentario = serializers.CharField(required=False, allow_blank=True)