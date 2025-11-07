from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
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
    filterset_fields = ['activo', 'roles__nombre_rol', 'email']
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
        # ⬅️ IMPORTANTE: Permitir reset_password sin autenticación
        if self.action == 'reset_password':
            return [AllowAny()]
        
        if self.action == 'list':
            if self.request.query_params.get('email'):
                return [AllowAny()]
            else:
                return [EsPersonalViveroOAdmin()]
        
        if self.action in ['create', 'destroy']:
            return [EsAdministrador()]
        
        return [IsAuthenticated()]
    
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
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def reset_password(self, request):
        """Resetear contraseña sin autenticación (para recuperación)"""
        print("🔍 RESET PASSWORD ENDPOINT LLAMADO")
        print("📧 Email:", request.data.get('email'))
        
        email = request.data.get('email')
        new_password = request.data.get('new_password')
        
        if not email or not new_password:
            return Response(
                {'error': 'Email y nueva contraseña son requeridos'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if len(new_password) < 8:
            return Response(
                {'error': 'La contraseña debe tener al menos 8 caracteres'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            usuario = Usuario.objects.get(email=email, activo=True)
            usuario.set_password(new_password)
            usuario.save()
            
            print(f"✅ Contraseña actualizada para: {usuario.nombre_completo}")
            
            return Response({
                'mensaje': 'Contraseña actualizada exitosamente',
                'usuario': usuario.nombre_completo
            })
        except Usuario.DoesNotExist:
            return Response(
                {'error': 'Usuario no encontrado o inactivo'},
                status=status.HTTP_404_NOT_FOUND
            )


class RolViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para roles (solo lectura)"""
    queryset = Rol.objects.all()
    serializer_class = RolSerializer
    permission_classes = [EsAdministrador]

    