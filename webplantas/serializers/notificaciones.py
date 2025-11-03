from rest_framework import serializers
from webplantas.models import Notificacion


class NotificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notificacion
        fields = [
            'id', 'tipo', 'titulo', 'mensaje', 'leida', 
            'fecha_creacion', 'pedido', 'ruta'
        ]
        read_only_fields = ['fecha_creacion']