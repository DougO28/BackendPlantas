# Backend/webplantas/views/pedidos.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction

from webplantas.models import Pedido, DetallePedido, HistorialEstadoPedido
from webplantas.serializers.pedidos import (
    PedidoListSerializer,
    PedidoDetailSerializer,
    PedidoCreateSerializer,
    CambiarEstadoPedidoSerializer,
)
from webplantas.permissions import EsAdministrador, EsPersonalViveroOAdmin


class PedidoViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de pedidos"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Pedido.objects.filter(activo=True)
        
        # Filtrar por usuario si no es admin
        if not self.request.user.is_staff:
            queryset = queryset.filter(usuario=self.request.user)
        
        # Filtros adicionales
        estado = self.request.query_params.get('estado', None)
        if estado:
            queryset = queryset.filter(estado=estado)
        
        return queryset.select_related(
            'usuario', 'municipio_entrega'
        ).prefetch_related('detallepedido_set__pilon')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PedidoListSerializer
        elif self.action == 'create':
            return PedidoCreateSerializer
        return PedidoDetailSerializer
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """Crear nuevo pedido"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Agregar el usuario al validated_data antes de crear
        serializer.validated_data['usuario'] = request.user
        
        # Crear el pedido
        pedido = serializer.save()
        
        # Crear historial inicial
        HistorialEstadoPedido.objects.create(
            pedido=pedido,
            estado_nuevo=pedido.estado,
            usuario_cambio=request.user,
            comentario="Pedido creado"
        )
        
        # Serializar respuesta con detalles completos
        response_serializer = PedidoDetailSerializer(pedido)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'], url_path='mis-pedidos', permission_classes=[IsAuthenticated])
    def mis_pedidos(self, request):
        """Obtener pedidos del usuario actual"""
        pedidos = Pedido.objects.filter(
            usuario=request.user,
            activo=True
        ).select_related(
            'usuario', 'municipio_entrega'
        ).prefetch_related(
            'detallepedido_set__pilon__categoria'
        ).order_by('-fecha_pedido')
        
        serializer = PedidoListSerializer(pedidos, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[EsPersonalViveroOAdmin])
    def cambiar_estado(self, request, pk=None):
        """Cambiar estado del pedido"""
        pedido = self.get_object()
        serializer = CambiarEstadoPedidoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        estado_anterior = pedido.estado
        nuevo_estado = serializer.validated_data['estado']
        comentario = serializer.validated_data.get('comentario', '')
        
        # Actualizar estado
        pedido.estado = nuevo_estado
        pedido.save()
        
        # Registrar en historial
        HistorialEstadoPedido.objects.create(
            pedido=pedido,
            estado_anterior=estado_anterior,
            estado_nuevo=nuevo_estado,
            usuario_cambio=request.user,
            comentario=comentario
        )
        
        response_serializer = PedidoDetailSerializer(pedido)
        return Response(response_serializer.data)
    
    @action(detail=True, methods=['post'])
    def calificar(self, request, pk=None):
        """Calificar pedido entregado"""
        pedido = self.get_object()
        
        # Verificar que sea del usuario
        if pedido.usuario != request.user:
            return Response(
                {'detail': 'No tienes permiso para calificar este pedido'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Verificar que esté entregado
        if pedido.estado != 'entregado':
            return Response(
                {'detail': 'Solo puedes calificar pedidos entregados'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        calificacion = request.data.get('calificacion')
        comentario = request.data.get('comentario', '')
        
        if not calificacion or not (1 <= int(calificacion) <= 5):
            return Response(
                {'detail': 'La calificación debe ser entre 1 y 5'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        pedido.calificacion = calificacion
        pedido.comentario_calificacion = comentario
        pedido.save()
        
        response_serializer = PedidoDetailSerializer(pedido)
        return Response(response_serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        """Cancelar pedido"""
        pedido = self.get_object()
        
        # Verificar permisos
        if pedido.usuario != request.user and not request.user.is_staff:
            return Response(
                {'detail': 'No tienes permiso para cancelar este pedido'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Verificar que se pueda cancelar
        if pedido.estado in ['entregado', 'cancelado']:
            return Response(
                {'detail': f'No se puede cancelar un pedido {pedido.estado}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        motivo = request.data.get('motivo', 'Cancelado por el usuario')
        
        estado_anterior = pedido.estado
        pedido.estado = 'cancelado'
        pedido.save()
        
        # Registrar en historial
        HistorialEstadoPedido.objects.create(
            pedido=pedido,
            estado_anterior=estado_anterior,
            estado_nuevo='cancelado',
            usuario_cambio=request.user,
            comentario=motivo
        )
        
        response_serializer = PedidoDetailSerializer(pedido)
        return Response(response_serializer.data)