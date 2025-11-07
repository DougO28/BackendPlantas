from rest_framework import viewsets
from rest_framework.permissions import AllowAny  # CAMBIAR ESTE IMPORT
from django_filters.rest_framework import DjangoFilterBackend

from webplantas.models import Departamento, Municipio
from webplantas.serializers import DepartamentoSerializer, MunicipioSerializer


class DepartamentoViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para departamentos (solo lectura)"""
    queryset = Departamento.objects.all()
    serializer_class = DepartamentoSerializer
    permission_classes = [AllowAny]  # CAMBIAR A AllowAny
    ordering = ['nombre']  # AGREGAR para que estén ordenados


class MunicipioViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para municipios (solo lectura)"""
    queryset = Municipio.objects.all()
    serializer_class = MunicipioSerializer
    permission_classes = [AllowAny]  # CAMBIAR A AllowAny
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['departamento']
    ordering = ['nombre']  # AGREGAR para que estén ordenados