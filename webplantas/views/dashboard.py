# Backend/webplantas/views/dashboard.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, F, Q, FloatField
from django.db.models.functions import Cast, TruncDate
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from webplantas.models import Pedido, DetallePedido, Usuario, CatalogoPilon, RutaEntrega
from webplantas.permissions import EsPersonalViveroOAdmin


class DashboardView(APIView):
    """Vista del dashboard con estadísticas generales"""
    permission_classes = [EsPersonalViveroOAdmin]
    
    def get(self, request):
        # Estadísticas básicas
        total_pedidos = Pedido.objects.count()
        pedidos_pendientes = Pedido.objects.filter(
            estado__in=['recibido', 'confirmado', 'en_preparacion']
        ).count()
        pedidos_entregados = Pedido.objects.filter(estado='entregado').count()
        
        total_usuarios = Usuario.objects.filter(activo=True).count()
        usuarios_activos = Usuario.objects.filter(
            activo=True, 
            ultimo_acceso__gte=timezone.now() - timedelta(days=30)
        ).count()
        
        plantas_disponibles = CatalogoPilon.objects.filter(activo=True, stock__gt=0).count()
        rutas_pendientes = RutaEntrega.objects.filter(estado__in=['planificada', 'en_progreso']).count()
        
        # Ingresos del mes actual
        inicio_mes = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        ingresos_mes = Pedido.objects.filter(
            fecha_pedido__gte=inicio_mes,
            estado='entregado'
        ).aggregate(total=Sum('total'))['total'] or 0
        
        data = {
            'total_pedidos': total_pedidos,
            'pedidos_pendientes': pedidos_pendientes,
            'pedidos_entregados': pedidos_entregados,
            'total_usuarios': total_usuarios,
            'usuarios_activos': usuarios_activos,
            'plantas_disponibles': plantas_disponibles,
            'rutas_pendientes': rutas_pendientes,
            'ingresos_mes_actual': float(ingresos_mes)
        }
        
        return Response(data)


class DashboardEstadisticasView(APIView):
    """Vista para estadísticas completas del dashboard"""
    permission_classes = [IsAuthenticated, EsPersonalViveroOAdmin]
    
    def get(self, request):
        # 🔧 USAR timezone.now() y timezone.localtime() para zona horaria correcta
        # 🔧 Usar timezone.localtime() para obtener la fecha local
        ahora_local = timezone.localtime(timezone.now())
        hoy = ahora_local.date()

        # ⚠️ IMPORTANTE: Para las consultas, usar __date directamente con la fecha local
        # pero MySQL puede usar UTC, así que convertimos primero

        print(f"\n{'='*50}")
        print(f"🕐 Ahora (timezone aware): {timezone.now()}")
        print(f"🕐 Ahora (local): {ahora_local}")
        print(f"📅 Hoy (local date): {hoy}")

        # ✅ SOLUCIÓN: Consultar usando rangos de datetime en lugar de __date
        inicio_hoy = timezone.make_aware(
            timezone.datetime.combine(hoy, timezone.datetime.min.time())
        )
        fin_hoy = timezone.make_aware(
            timezone.datetime.combine(hoy, timezone.datetime.max.time())
        )

        print(f"⏰ Rango de búsqueda HOY:")
        print(f"   Inicio: {inicio_hoy}")
        print(f"   Fin: {fin_hoy}")

        # Ventas de hoy (usando rango de datetime)
        ventas_hoy_query = Pedido.objects.filter(
            fecha_pedido__gte=inicio_hoy,
            fecha_pedido__lte=fin_hoy,
            activo=True
        )
        print(f"💰 Pedidos encontrados para HOY: {ventas_hoy_query.count()}")

        ventas_hoy = ventas_hoy_query.exclude(estado='cancelado').aggregate(
            total=Sum('total')
        )['total'] or Decimal('0.00')
        print(f"💰 Total ventas hoy: {ventas_hoy}")

        # Ventas de la semana
        inicio_semana = hoy - timedelta(days=hoy.weekday())
        inicio_semana_dt = timezone.make_aware(
            timezone.datetime.combine(inicio_semana, timezone.datetime.min.time())
        )

        ventas_semana = Pedido.objects.filter(
            fecha_pedido__gte=inicio_semana_dt,
            activo=True
        ).exclude(estado='cancelado').aggregate(
            total=Sum('total')
        )['total'] or Decimal('0.00')

        # Ventas del mes
        inicio_mes = hoy.replace(day=1)
        inicio_mes_dt = timezone.make_aware(
            timezone.datetime.combine(inicio_mes, timezone.datetime.min.time())
        )

        ventas_mes = Pedido.objects.filter(
            fecha_pedido__gte=inicio_mes_dt,
            activo=True
        ).exclude(estado='cancelado').aggregate(
            total=Sum('total')
        )['total'] or Decimal('0.00')

        # ============= PEDIDOS =============
        pedidos_hoy = ventas_hoy_query.count()

        pedidos_semana = Pedido.objects.filter(
            fecha_pedido__gte=inicio_semana_dt,
            activo=True
        ).count()

        pedidos_mes = Pedido.objects.filter(
            fecha_pedido__gte=inicio_mes_dt,
            activo=True
        ).count()
        
        # Pedidos por estado
        pedidos_por_estado = {}
        estados = Pedido.objects.filter(activo=True).values('estado').annotate(
            total=Count('id')
        )
        for estado in estados:
            pedidos_por_estado[estado['estado']] = estado['total']
        
        # ============= TOP 5 PRODUCTOS MÁS VENDIDOS =============
        productos_vendidos = DetallePedido.objects.filter(
            pedido__activo=True,
            pedido__fecha_pedido__date__gte=inicio_mes
        ).exclude(
            pedido__estado='cancelado'
        ).values(
            'pilon_id',
            'pilon__nombre_variedad',
            'pilon__categoria__nombre'
        ).annotate(
            cantidad_vendida=Sum('cantidad'),
            total_vendido=Sum(F('cantidad') * F('precio_unitario'))
        ).order_by('-cantidad_vendida')[:5]
        
        top_productos = [
            {
                'pilon_id': p['pilon_id'],
                'nombre_variedad': p['pilon__nombre_variedad'],
                'categoria': p['pilon__categoria__nombre'] or 'Sin categoría',
                'cantidad_vendida': p['cantidad_vendida'],
                'total_vendido': float(p['total_vendido'])
            }
            for p in productos_vendidos
        ]
        
        # ============= STOCK BAJO =============
        stock_bajo = CatalogoPilon.objects.filter(
            activo=True,
            stock__lte=F('stock_minimo')
        ).annotate(
            porcentaje_stock=Cast(F('stock'), FloatField()) / Cast(F('stock_minimo'), FloatField()) * 100
        ).values(
            'id',
            'nombre_variedad',
            'categoria__nombre',
            'stock',
            'stock_minimo',
            'porcentaje_stock'
        ).order_by('porcentaje_stock')[:10]
        
        productos_stock_bajo = [
            {
                'id': p['id'],
                'nombre_variedad': p['nombre_variedad'],
                'categoria': p['categoria__nombre'] or 'Sin categoría',
                'stock': p['stock'],
                'stock_minimo': p['stock_minimo'],
                'porcentaje_stock': round(p['porcentaje_stock'], 1)
            }
            for p in stock_bajo
        ]
        
                # ============= VENTAS ÚLTIMOS 7 DÍAS =============
        ventas_diarias = []

        # Calcular rango de fechas (últimos 7 días)
        fecha_inicio = hoy - timedelta(days=6)

        print(f"\n📊 Consultando ventas desde {fecha_inicio} hasta {hoy}")

        # Para cada día, crear rangos de datetime
        for i in range(6, -1, -1):
            fecha = hoy - timedelta(days=i)
            
            # 🔧 Crear rango de datetime para ese día
            inicio_dia = timezone.make_aware(
                timezone.datetime.combine(fecha, timezone.datetime.min.time())
            )
            fin_dia = timezone.make_aware(
                timezone.datetime.combine(fecha, timezone.datetime.max.time())
            )
            
            # Consultar pedidos de ese día
            ventas_dia = Pedido.objects.filter(
                fecha_pedido__gte=inicio_dia,
                fecha_pedido__lte=fin_dia,
                activo=True
            ).exclude(estado='cancelado').aggregate(
                total=Sum('total'),
                cantidad=Count('id')
            )
            
            total = float(ventas_dia['total'] or 0)
            cantidad = ventas_dia['cantidad'] or 0
            
            ventas_diarias.append({
                'fecha': fecha.strftime('%Y-%m-%d'),
                'total': total,
                'cantidad_pedidos': cantidad
            })
            
            emoji = "✅" if cantidad > 0 else "⭕"
            print(f"{emoji} {fecha}: Q{total:.2f} ({cantidad} pedidos)")

        print(f"{'='*50}\n")
        
        # ============= RESPUESTA =============
        data = {
            'ventas': {
                'total_ventas_hoy': float(ventas_hoy),
                'total_ventas_semana': float(ventas_semana),
                'total_ventas_mes': float(ventas_mes),
                'pedidos_hoy': pedidos_hoy,
                'pedidos_semana': pedidos_semana,
                'pedidos_mes': pedidos_mes,
                'pedidos_por_estado': pedidos_por_estado,
            },
            'top_productos': top_productos,
            'stock_bajo': productos_stock_bajo,
            'ventas_diarias': ventas_diarias,
        }
        
        return Response(data)


class MetricasView(APIView):
    """Vista para métricas personalizadas por rol"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        if user.roles.filter(nombre_rol='Agricultor').exists():
            return self._metricas_agricultor(user)
        elif user.roles.filter(nombre_rol__in=['Administrador', 'Personal Vivero']).exists():
            return self._metricas_admin()
        else:
            return Response({'error': 'Sin permisos para ver métricas'}, status=403)
    
    def _metricas_agricultor(self, user):
        """Métricas específicas del agricultor"""
        mis_pedidos = Pedido.objects.filter(usuario=user)
        
        data = {
            'total_pedidos': mis_pedidos.count(),
            'pedidos_activos': mis_pedidos.exclude(estado__in=['entregado', 'cancelado']).count(),
            'pedidos_entregados': mis_pedidos.filter(estado='entregado').count(),
            'gasto_total': float(mis_pedidos.filter(estado='entregado').aggregate(Sum('total'))['total'] or 0),
            'notificaciones_no_leidas': user.notificaciones.filter(leida=False).count()
        }
        
        return Response(data)
    
    def _metricas_admin(self):
        """Métricas para administradores"""
        hoy = timezone.localtime(timezone.now()).date()
        
        data = {
            'pedidos_hoy': Pedido.objects.filter(fecha_pedido__date=hoy).count(),
            'rutas_hoy': RutaEntrega.objects.filter(fecha_planificada=hoy).count(),
            'entregas_hoy': Pedido.objects.filter(fecha_entrega_real=hoy).count(),
            'pedidos_pendientes_confirmacion': Pedido.objects.filter(estado='recibido').count(),
            'plantas_stock_critico': CatalogoPilon.objects.filter(
                stock__lte=F('stock_minimo'),
                activo=True
            ).count()
        }
        
        return Response(data)