# Backend/webplantas/views/catalogos_logistica.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from webplantas.models import Transportista, DocumentoVehiculo, PuntoSiembra, Finca
from webplantas.serializers import (
    TransportistaSerializer,
    DocumentoVehiculoSerializer,
    PuntoSiembraSerializer,
    FincaSerializer
)
from webplantas.permissions import EsPersonalViveroOAdmin


class TransportistaViewSet(viewsets.ModelViewSet):
    """ViewSet para transportistas"""
    queryset = Transportista.objects.all()
    serializer_class = TransportistaSerializer
    permission_classes = [EsPersonalViveroOAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['activo']
    search_fields = ['nombre', 'contacto']


class DocumentoVehiculoViewSet(viewsets.ModelViewSet):
    """ViewSet para documentos de vehículos"""
    queryset = DocumentoVehiculo.objects.all()
    serializer_class = DocumentoVehiculoSerializer
    permission_classes = [EsPersonalViveroOAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['vehiculo', 'tipo']
    search_fields = ['vehiculo__placa', 'numero_documento']


class PuntoSiembraViewSet(viewsets.ModelViewSet):
    """ViewSet para puntos de siembra"""
    queryset = PuntoSiembra.objects.all()
    serializer_class = PuntoSiembraSerializer
    permission_classes = [EsPersonalViveroOAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['departamento', 'municipio', 'activo']
    search_fields = ['nombre', 'contacto']


class FincaViewSet(viewsets.ModelViewSet):
    """ViewSet para fincas/viveros destino"""
    queryset = Finca.objects.all()
    serializer_class = FincaSerializer
    permission_classes = [EsPersonalViveroOAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['departamento', 'municipio', 'activo', 'usuario']
    search_fields = ['nombre', 'contacto']