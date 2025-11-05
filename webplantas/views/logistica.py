# Backend/webplantas/views/logistica.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.utils import timezone
from django.db.models import Count, Q  # ✅ AGREGAR
from datetime import date  # ✅ AGREGAR

from webplantas.models import RutaEntrega, PedidoRuta, Vehiculo, Pedido  # ✅ AGREGAR Pedido
from webplantas.serializers import (
    RutaEntregaListSerializer, RutaEntregaDetailSerializer,
    RutaEntregaCreateSerializer, VehiculoSerializer,
    ConfirmarEntregaSerializer
)
from webplantas.permissions import EsPersonalViveroOAdmin, EsTecnicoCampo


class RutaEntregaViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de rutas de entrega"""
    queryset = RutaEntrega.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['estado', 'departamento', 'tecnico_campo']
    search_fields = ['codigo_ruta', 'nombre_ruta']
    ordering_fields = ['fecha_planificada', 'fecha_inicio']
    ordering = ['-fecha_planificada']

    def get_serializer_class(self):
        if self.action == 'create':
            return RutaEntregaCreateSerializer
        elif self.action == 'retrieve':
            return RutaEntregaDetailSerializer
        return RutaEntregaListSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [EsPersonalViveroOAdmin]
        else:
            self.permission_classes = [EsTecnicoCampo]
        return super().get_permissions()

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        # Si es técnico de campo, solo ve sus rutas
        if user.roles.filter(nombre_rol='Tecnico Campo').exists() and \
           not user.roles.filter(nombre_rol__in=['Administrador', 'Personal Vivero']).exists():
            queryset = queryset.filter(tecnico_campo=user)

        return queryset

    # ✅ AGREGAR ESTE MÉTODO
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """Obtener estadísticas de logística"""
        hoy = date.today()
        
        # Rutas activas (planificadas o en progreso)
        rutas_activas = RutaEntrega.objects.filter(
            estado__in=['planificada', 'en_progreso']
        ).count()
        
        # Pedidos sin asignar a ruta (estado listo_entrega)
        pedidos_sin_asignar = Pedido.objects.filter(
            estado='listo_entrega'
        ).exclude(
            pedidoruta__isnull=False
        ).count()
        
        # Entregas completadas hoy
        entregas_hoy = PedidoRuta.objects.filter(
            entregado=True,
            pedido__fecha_entrega_real=hoy
        ).count()
        
        # Vehículos disponibles y totales
        vehiculos_disponibles = Vehiculo.objects.filter(activo=True).count()
        total_vehiculos = Vehiculo.objects.count()
        
        return Response({
            'rutas_activas': rutas_activas,
            'pedidos_sin_asignar': pedidos_sin_asignar,
            'entregas_completadas_hoy': entregas_hoy,
            'vehiculos_disponibles': vehiculos_disponibles,
            'total_vehiculos': total_vehiculos,
        })

    @action(detail=True, methods=['post'], permission_classes=[EsTecnicoCampo])
    def iniciar_ruta(self, request, pk=None):
        """Iniciar ruta (técnico marca que salió)"""
        ruta = self.get_object()

        if ruta.estado != 'planificada':
            return Response(
                {'error': 'Solo se pueden iniciar rutas planificadas'},
                status=status.HTTP_400_BAD_REQUEST
            )

        ruta.estado = 'en_progreso'
        ruta.fecha_inicio = timezone.now()
        ruta.save()

        return Response({
            'mensaje': 'Ruta iniciada',
            'fecha_inicio': ruta.fecha_inicio
        })

    @action(detail=True, methods=['post'], permission_classes=[EsTecnicoCampo])
    def finalizar_ruta(self, request, pk=None):
        """Finalizar ruta"""
        ruta = self.get_object()

        if ruta.estado != 'en_progreso':
            return Response(
                {'error': 'Solo se pueden finalizar rutas en progreso'},
                status=status.HTTP_400_BAD_REQUEST
            )

        ruta.estado = 'completada'
        ruta.fecha_fin = timezone.now()
        ruta.save()

        return Response({
            'mensaje': 'Ruta finalizada',
            'fecha_fin': ruta.fecha_fin
        })

    @action(detail=True, methods=['post'], permission_classes=[EsTecnicoCampo])
    def confirmar_entrega_pedido(self, request, pk=None):
        """Confirmar entrega de un pedido específico en la ruta"""
        ruta = self.get_object()
        pedido_id = request.data.get('pedido_id')

        try:
            pedido_ruta = PedidoRuta.objects.get(ruta=ruta, pedido_id=pedido_id)

            serializer = ConfirmarEntregaSerializer(data=request.data)
            if serializer.is_valid():
                pedido_ruta.entregado = True
                pedido_ruta.hora_salida = timezone.now().time()
                pedido_ruta.receptor_nombre = serializer.validated_data['receptor_nombre']
                pedido_ruta.receptor_documento = serializer.validated_data.get('receptor_documento', '')
                pedido_ruta.observaciones_entrega = serializer.validated_data.get('observaciones_entrega', '')
                pedido_ruta.save()

                # Actualizar estado del pedido
                pedido = pedido_ruta.pedido
                pedido.estado = 'entregado'
                pedido.fecha_entrega_real = timezone.now().date()
                pedido.save()

                return Response({
                    'mensaje': 'Entrega confirmada',
                    'pedido': pedido.codigo_seguimiento
                })

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except PedidoRuta.DoesNotExist:
            return Response(
                {'error': 'Pedido no encontrado en esta ruta'},
                status=status.HTTP_404_NOT_FOUND
            )


class VehiculoViewSet(viewsets.ModelViewSet):
    """ViewSet para vehículos"""
    queryset = Vehiculo.objects.all()
    serializer_class = VehiculoSerializer
    permission_classes = [EsPersonalViveroOAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['placa', 'marca', 'modelo']
    filterset_fields = ['activo']