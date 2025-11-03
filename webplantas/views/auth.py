from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils import timezone

from webplantas.serializers import LoginSerializer, ChangePasswordSerializer, RegisterSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Serializer personalizado para incluir info del usuario"""
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Actualizar último acceso
        self.user.ultimo_acceso = timezone.now()
        self.user.save(update_fields=['ultimo_acceso'])
        
        # Agregar información del usuario
        data['user'] = {
            'id': self.user.id,
            'nombre_completo': self.user.nombre_completo,
            'email': self.user.email,
            'roles': [rol.nombre_rol for rol in self.user.roles.all()]
        }
        
        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    """Vista personalizada para login con JWT"""
    serializer_class = CustomTokenObtainPairSerializer


class ChangePasswordView(APIView):
    """Cambiar contraseña del usuario autenticado"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            
            # Verificar contraseña actual
            if not user.check_password(serializer.validated_data['old_password']):
                return Response(
                    {'error': 'Contraseña actual incorrecta'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Establecer nueva contraseña
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            return Response({'mensaje': 'Contraseña actualizada correctamente'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(APIView):
    """Registro de nuevos usuarios (Agricultores)"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'mensaje': 'Usuario registrado correctamente',
                'user': {
                    'id': user.id,
                    'nombre_completo': user.nombre_completo,
                    'email': user.email
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)