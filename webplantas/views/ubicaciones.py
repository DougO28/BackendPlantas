from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from webplantas.models import Departamento, Municipio
from webplantas.serializers import DepartamentoSerializer, MunicipioSerializer


class DepartamentoViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para departamentos (solo lectura)"""
    queryset = Departamento.objects.all()
    serializer_class = DepartamentoSerializer
    permission_classes = [IsAuthenticated]


class MunicipioViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para municipios (solo lectura)"""
    queryset = Municipio.objects.all()
    serializer_class = MunicipioSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['departamento']