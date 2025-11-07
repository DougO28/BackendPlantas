# Backend/webplantas/views/test_data.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import random

from webplantas.models import (
    Pedido, DetallePedido, Usuario, CatalogoPilon, 
    Municipio, HistorialEstadoPedido
)
from webplantas.permissions import EsPersonalViveroOAdmin


class GenerarDatosPruebaView(APIView):
    """
    Genera datos de prueba para el dashboard
    POST: Crea pedidos de prueba para los últimos 7 días
    DELETE: Elimina todos los pedidos de prueba
    """
    permission_classes = [EsPersonalViveroOAdmin]
    
    def post(self, request):
        """Generar pedidos de prueba para los últimos 7 días"""
        try:
            with transaction.atomic():
                # Obtener usuarios y productos disponibles
                usuarios = list(Usuario.objects.filter(activo=True))
                productos = list(CatalogoPilon.objects.filter(activo=True, stock__gt=0))
                municipios = list(Municipio.objects.all())
                
                if not usuarios:
                    return Response({
                        'error': 'No hay usuarios activos. Crea al menos un usuario primero.'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                if not productos:
                    return Response({
                        'error': 'No hay productos disponibles. Crea productos en el catálogo primero.'
                    }, status=status.HTTP_400_BAD_REQUEST)
                    
                if not municipios:
                    return Response({
                        'error': 'No hay municipios. Crea al menos un municipio primero.'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                estados_posibles = ['recibido', 'confirmado', 'en_preparacion', 'en_ruta', 'entregado']
                nombres_ejemplo = ['Juan', 'María', 'Pedro', 'Ana', 'Luis', 'Carmen', 'José', 'Laura']
                apellidos_ejemplo = ['García', 'López', 'Martínez', 'Rodríguez', 'Pérez', 'González', 'Hernández']
                
                pedidos_creados = 0
                
                # 🔧 USAR timezone.localtime() para obtener la fecha local
                ahora = timezone.localtime(timezone.now())
                hoy = ahora.date()
                
                print(f"\n{'='*60}")
                print(f" GENERANDO DATOS DE PRUEBA")
                print(f"Ahora (local): {ahora}")
                print(f" Hoy (date): {hoy}")
                print(f" Usuarios disponibles: {len(usuarios)}")
                print(f" Productos disponibles: {len(productos)}")
                print(f"  Municipios disponibles: {len(municipios)}")
                print(f"{'='*60}\n")
                
                # Generar pedidos para los últimos 7 días
                for dias_atras in range(6, -1, -1):  # De 6 días atrás hasta hoy
                    fecha = hoy - timedelta(days=dias_atras)
                    
                    # Generar entre 3 y 8 pedidos por día
                    cantidad_pedidos = random.randint(3, 8)
                    
                    print(f" Generando {cantidad_pedidos} pedidos para {fecha}")
                    
                    for i in range(cantidad_pedidos):
                        # Seleccionar datos aleatorios
                        usuario = random.choice(usuarios)
                        municipio = random.choice(municipios)
                        estado = random.choice(estados_posibles)
                        
                        # Nombres aleatorios
                        nombre = random.choice(nombres_ejemplo)
                        apellido = random.choice(apellidos_ejemplo)
                        
                        # 🔧 Crear fecha y hora aleatoria ese día (TIMEZONE AWARE)
                        hora_aleatoria = random.randint(8, 18)  # Entre 8 AM y 6 PM
                        minuto_aleatorio = random.randint(0, 59)
                        
                        # Crear datetime naive primero
                        fecha_pedido_naive = timezone.datetime(
                            fecha.year, fecha.month, fecha.day,
                            hora_aleatoria, minuto_aleatorio, 0
                        )
                        
                        # 🔧 Convertir a timezone aware usando la zona horaria actual
                        fecha_pedido = timezone.make_aware(
                            fecha_pedido_naive,
                            timezone.get_current_timezone()
                        )
                        
                        # 🔧 PRIMERO: Crear pedido SIN total (se calculará después)
                        pedido = Pedido.objects.create(
                            usuario=usuario,
                            municipio_entrega=municipio,
                            direccion_entrega=f"Calle {random.randint(1, 50)}, Zona {random.randint(1, 20)}",
                            nombre_contacto=f"{nombre} {apellido}",
                            telefono_contacto=f"5{random.randint(1000, 9999)}{random.randint(1000, 9999)}",
                            nombres_cliente=nombre,
                            apellidos_cliente=apellido,
                            estado=estado,
                            fecha_pedido=fecha_pedido,
                            total=Decimal('0.00'),  # Temporal
                            descuento=Decimal('0.00'),
                            canal_origen='web',
                            observaciones=' Pedido de prueba generado automáticamente',
                            pendiente_viaje=False,
                            activo=True,  #  AGREGAR ESTO
                        )
                        
                        #  SEGUNDO: Agregar productos al pedido
                        cantidad_productos = random.randint(1, 4)
                        productos_pedido = random.sample(productos, min(cantidad_productos, len(productos)))
                        
                        total_calculado = Decimal('0.00')
                        
                        for producto in productos_pedido:
                            cantidad = random.randint(10, 100)
                            precio_unitario = Decimal(str(producto.precio_unitario))
                            subtotal_item = precio_unitario * Decimal(str(cantidad))
                            
                            #  NO restamos stock en pedidos de prueba
                            DetallePedido.objects.create(
                                pedido=pedido,
                                pilon=producto,
                                cantidad=cantidad,
                                precio_unitario=precio_unitario,
                                subtotal=subtotal_item
                            )
                            
                            total_calculado += subtotal_item
                        
                        #  TERCERO: Actualizar el total del pedido
                        pedido.total = total_calculado
                        pedido.save(update_fields=['total'])
                        
                        #  CUARTO: Verificar que se guardó correctamente
                        pedido.refresh_from_db()
                        
                        if pedido.total == 0:
                            print(f"   ⚠️  ERROR: Pedido {pedido.id} tiene total=0 después de guardar!")
                            print(f"      Total calculado: {total_calculado}")
                            print(f"      Detalles: {pedido.detallepedido_set.count()}")
                        else:
                            # Solo mostrar log si el total es correcto
                            pass  # El log principal se muestra abajo
                        
                        # Crear historial inicial
                        HistorialEstadoPedido.objects.create(
                            pedido=pedido,
                            estado_nuevo=estado,
                            usuario_cambio=request.user,
                            comentario='🧪 Pedido de prueba generado'
                        )
                        
                        pedidos_creados += 1
                        
                        # Log del pedido creado (con total verificado)
                        total_final = pedido.total
                        emoji_status = "✅" if total_final > 0 else "❌"
                        print(f"   {emoji_status} Pedido #{pedido.id} ({pedido.codigo_seguimiento}): {fecha_pedido.strftime('%Y-%m-%d %H:%M')} | Estado: {estado} | Total: Q{total_final:.2f}")
                
                #  VERIFICAR: Contar pedidos creados por fecha
                from django.db.models import Sum
                
                print(f"\n{'='*60}")
                print(f" VERIFICACIÓN - Pedidos creados por fecha:")
                for dias_atras in range(6, -1, -1):
                    fecha = hoy - timedelta(days=dias_atras)
                    count = Pedido.objects.filter(
                        fecha_pedido__date=fecha,
                        observaciones__icontains='prueba generado'
                    ).count()
                    total_ventas = Pedido.objects.filter(
                        fecha_pedido__date=fecha,
                        observaciones__icontains='prueba generado'
                    ).exclude(estado='cancelado').aggregate(total=Sum('total'))['total'] or Decimal('0')
                    print(f"   {fecha}: {count} pedidos, Total: Q{total_ventas:.2f}")
                print(f"{'='*60}\n")
                
                return Response({
                    'mensaje': f' Se generaron {pedidos_creados} pedidos de prueba exitosamente',
                    'total_pedidos': pedidos_creados,
                    'rango_fechas': f'{hoy - timedelta(days=6)} a {hoy}',
                    'zona_horaria': str(timezone.get_current_timezone())
                }, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            import traceback
            print(f"\n❌ ERROR al generar datos:")
            print(traceback.format_exc())
            return Response({
                'error': f'Error al generar datos de prueba: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request):
        """Eliminar todos los pedidos de prueba"""
        try:
            # Eliminar pedidos que tengan "prueba" en las observaciones
            pedidos_prueba = Pedido.objects.filter(
                observaciones__icontains='Pedido de prueba generado automáticamente'
            )
            
            cantidad = pedidos_prueba.count()
            
            print(f"\n Eliminando {cantidad} pedidos de prueba...")
            
            # Eliminar en cascada (DetallePedido y HistorialEstadoPedido se eliminan automáticamente)
            pedidos_prueba.delete()
            
            print(f"Pedidos eliminados exitosamente\n")
            
            return Response({
                'mensaje': f' Se eliminaron {cantidad} pedidos de prueba',
                'cantidad_eliminada': cantidad
            })
            
        except Exception as e:
            import traceback
            print(f"\n ERROR al eliminar datos:")
            print(traceback.format_exc())
            return Response({
                'error': f'Error al eliminar datos de prueba: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)