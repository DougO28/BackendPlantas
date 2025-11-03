from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from webplantas.models import Usuario, Rol, UsuarioRol
from webplantas.serializers import (
    UsuarioListSerializer, UsuarioDetailSerializer,
    UsuarioCreateSerializer, UsuarioUpdateSerializer,
    RolSerializer, ParcelaSerializer
)
from webplantas.permissions import EsAdministrador, EsPersonalViveroOAdmin


class UsuarioViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de usuarios"""
    queryset = Usuario.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['activo', 'roles__nombre_rol']
    search_fields = ['nombre_completo', 'email']
    ordering_fields = ['nombre_completo', 'fecha_registro']
    ordering = ['-fecha_registro']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UsuarioCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UsuarioUpdateSerializer
        elif self.action == 'retrieve':
            return UsuarioDetailSerializer
        return UsuarioListSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            self.permission_classes = [EsAdministrador]
        elif self.action in ['list']:
            self.permission_classes = [EsPersonalViveroOAdmin]
        return super().get_permissions()
    
    @action(detail=True, methods=['get'])
    def parcelas(self, request, pk=None):
        """Obtener parcelas del usuario"""
        usuario = self.get_object()
        parcelas = usuario.parcelas.all()
        serializer = ParcelaSerializer(parcelas, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[EsAdministrador])
    def asignar_rol(self, request, pk=None):
        """Asignar rol a usuario"""
        usuario = self.get_object()
        rol_id = request.data.get('rol_id')
        
        try:
            rol = Rol.objects.get(id=rol_id)
            usuario_rol, created = UsuarioRol.objects.get_or_create(
                usuario=usuario, 
                rol=rol,
                defaults={'activo': True}
            )
            
            if not created and not usuario_rol.activo:
                usuario_rol.activo = True
                usuario_rol.save()
            
            return Response({'mensaje': f'Rol {rol.nombre_rol} asignado correctamente'})
        except Rol.DoesNotExist:
            return Response(
                {'error': 'Rol no encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )


class RolViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para roles (solo lectura)"""
    queryset = Rol.objects.all()
    serializer_class = RolSerializer
    permission_classes = [EsAdministrador]