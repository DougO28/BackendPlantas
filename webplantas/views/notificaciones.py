from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from webplantas.models import Notificacion
from webplantas.serializers import NotificacionSerializer


class NotificacionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para notificaciones del usuario"""
    serializer_class = NotificacionSerializer
    permission_classes = [IsAuthenticated]
    ordering = ['-fecha_creacion']
    
    def get_queryset(self):
        return Notificacion.objects.filter(usuario=self.request.user)
    
    @action(detail=True, methods=['patch'])
    def marcar_leida(self, request, pk=None):
        """Marcar notificación como leída"""
        notificacion = self.get_object()
        notificacion.leida = True
        notificacion.save()
        return Response({'mensaje': 'Notificación marcada como leída'})
    
    @action(detail=False, methods=['patch'])
    def marcar_todas_leidas(self, request):
        """Marcar todas las notificaciones como leídas"""
        self.get_queryset().update(leida=True)
        return Response({'mensaje': 'Todas las notificaciones marcadas como leídas'})
    
    @action(detail=False, methods=['get'])
    def no_leidas(self, request):
        """Obtener notificaciones no leídas"""
        notificaciones = self.get_queryset().filter(leida=False)
        serializer = self.get_serializer(notificaciones, many=True)
        return Response({
            'count': notificaciones.count(),
            'results': serializer.data
        })