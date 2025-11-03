from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, F

from webplantas.models import CategoriaPlanta, CatalogoPilon
from webplantas.serializers import (
    CategoriaPlantaSerializer,
    CatalogoPilonSerializer,
    CatalogoPilonListSerializer,
    CatalogoPilonCreateUpdateSerializer,
)
from webplantas.permissions import EsAdministrador, EsPersonalViveroOAdmin


class CategoriaPlantaViewSet(viewsets.ModelViewSet):
    """ViewSet para categorías de plantas"""
    queryset = CategoriaPlanta.objects.filter(activo=True)
    serializer_class = CategoriaPlantaSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [EsAdministrador]
        return super().get_permissions()


class CatalogoPilonViewSet(viewsets.ModelViewSet):
    """ViewSet para catálogo de pilones"""
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre_variedad', 'descripcion', 'categoria__nombre']
    ordering_fields = ['precio_unitario', 'stock', 'fecha_creacion']
    ordering = ['-fecha_creacion']
    
    def get_queryset(self):
        queryset = CatalogoPilon.objects.filter(activo=True).select_related('categoria')
        
        # Filtros adicionales
        categoria = self.request.query_params.get('categoria', None)
        if categoria:
            queryset = queryset.filter(categoria_id=categoria)
        
        stock_minimo = self.request.query_params.get('stock_bajo', None)
        if stock_minimo:
            queryset = queryset.filter(stock__lte=F('stock_minimo'))
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CatalogoPilonListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return CatalogoPilonCreateUpdateSerializer
        return CatalogoPilonSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'disponibles', 'stock_bajo']:
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [EsAdministrador]
        return super().get_permissions()
    
    @action(detail=False, methods=['get'])
    def disponibles(self, request):
        """Plantas disponibles (con stock > 0)"""
        plantas = self.get_queryset().filter(stock__gt=0, activo=True)
        serializer = CatalogoPilonSerializer(plantas, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[EsPersonalViveroOAdmin])
    def stock_bajo(self, request):
        """Plantas con stock bajo"""
        plantas = self.get_queryset().filter(
            stock__lte=F('stock_minimo'),
            activo=True
        )
        serializer = CatalogoPilonSerializer(plantas, many=True)
        return Response(serializer.data)