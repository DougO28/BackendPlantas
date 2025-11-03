from django.core.management.base import BaseCommand
from webplantas.models import Rol, Departamento, Municipio, Usuario, UsuarioRol, CategoriaPlanta


class Command(BaseCommand):
    help = 'Crea los datos iniciales del sistema'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Creando datos iniciales...'))

        # ============= ROLES =============
        self.stdout.write('Creando roles...')
        roles_data = [
            {
                'nombre_rol': 'Administrador',
                'descripcion': 'Gerencia de Agriconecta - Acceso total al sistema'
            },
            {
                'nombre_rol': 'Personal Vivero',
                'descripcion': 'Personal de vivero y logística - Gestión de pedidos e inventario'
            },
            {
                'nombre_rol': 'Tecnico Campo',
                'descripcion': 'Técnicos de campo - Entregas y rutas asignadas'
            },
            {
                'nombre_rol': 'Agricultor',
                'descripcion': 'Cliente final - Seguimiento de pedidos'
            },
        ]

        for rol_data in roles_data:
            rol, created = Rol.objects.get_or_create(
                nombre_rol=rol_data['nombre_rol'],
                defaults={'descripcion': rol_data['descripcion']}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ Rol creado: {rol.nombre_rol}'))
            else:
                self.stdout.write(f'  - Rol ya existe: {rol.nombre_rol}')

        # ============= DEPARTAMENTOS Y MUNICIPIOS =============
        self.stdout.write('\nCreando departamentos y municipios...')
        
        departamentos_data = {
            'Quiché': {
                'region': 'Noroccidente',
                'municipios': [
                    'Santa Cruz del Quiché', 'Chiché', 'Chinique', 'Zacualpa',
                    'Chajul', 'Chichicastenango', 'Patzité', 'San Antonio Ilotenango',
                    'San Pedro Jocopilas', 'Cunén', 'San Juan Cotzal', 'Joyabaj',
                    'Nebaj', 'San Andrés Sajcabajá', 'Uspantán', 'Sacapulas',
                    'San Bartolomé Jocotenango', 'Canillá', 'Chicamán', 'Ixcán',
                    'Pachalum'
                ]
            },
            'Huehuetenango': {
                'region': 'Noroccidente',
                'municipios': [
                    'Huehuetenango', 'Chiantla', 'Malacatancito', 'Cuilco',
                    'Nentón', 'San Pedro Necta', 'Jacaltenango', 'San Antonio Huista',
                    'La Libertad', 'La Democracia', 'San Miguel Acatán', 'San Rafael La Independencia',
                    'Todos Santos Cuchumatán', 'San Juan Atitán', 'Santa Bárbara',
                    'Tectitán', 'Concepción Huista', 'San Juan Ixcoy', 'San Mateo Ixtatán',
                    'Colotenango', 'San Sebastián Huehuetenango', 'San Rafael Petzal',
                    'San Gaspar Ixchil', 'Santiago Chimaltenango', 'Santa Ana Huista',
                    'San Sebastián Coatán', 'Barillas', 'Aguacatán', 'San Antonio Huista',
                    'Santa Eulalia', 'Santa Cruz Barillas'
                ]
            },
            'San Marcos': {
                'region': 'Suroccidente',
                'municipios': [
                    'San Marcos', 'San Pedro Sacatepéquez', 'San Antonio Sacatepéquez',
                    'Comitancillo', 'San Miguel Ixtahuacán', 'Concepción Tutuapa',
                    'Tacaná', 'Sibinal', 'Tajumulco', 'Tejutla', 'San Rafael Pie de la Cuesta',
                    'Nuevo Progreso', 'El Tumbador', 'San José El Rodeo', 'Malacatán',
                    'Catarina', 'Ayutla', 'Ocós', 'San Pablo', 'El Quetzal',
                    'La Reforma', 'Pajapita', 'Ixchiguán', 'San José Ojetenam',
                    'San Cristóbal Cucho', 'Sipacapa', 'Esquipulas Palo Gordo',
                    'Río Blanco', 'San Lorenzo'
                ]
            },
            'Totonicapán': {
                'region': 'Suroccidente',
                'municipios': [
                    'Totonicapán', 'San Cristóbal Totonicapán', 'San Francisco El Alto',
                    'San Andrés Xecul', 'Momostenango', 'Santa María Chiquimula',
                    'Santa Lucía La Reforma', 'San Bartolo'
                ]
            },
        }

        for dept_nombre, dept_info in departamentos_data.items():
            departamento, created = Departamento.objects.get_or_create(
                nombre=dept_nombre,
                defaults={'region': dept_info['region']}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ Departamento creado: {dept_nombre}'))
            
            for municipio_nombre in dept_info['municipios']:
                municipio, created = Municipio.objects.get_or_create(
                    nombre=municipio_nombre,
                    departamento=departamento
                )
                if created:
                    self.stdout.write(f'    • Municipio creado: {municipio_nombre}')

        # ============= CATEGORÍAS DE PLANTAS =============
        self.stdout.write('\nCreando categorías de plantas...')
        categorias_data = [
            {'nombre': 'Café', 'descripcion': 'Pilones de café de diferentes variedades'},
            {'nombre': 'Aguacate', 'descripcion': 'Pilones de aguacate Hass y otras variedades'},
            {'nombre': 'Cítricos', 'descripcion': 'Naranjas, limones, mandarinas'},
            {'nombre': 'Forestales', 'descripcion': 'Árboles maderables y de conservación'},
            {'nombre': 'Frutales', 'descripcion': 'Diversos árboles frutales'},
        ]

        for cat_data in categorias_data:
            categoria, created = CategoriaPlanta.objects.get_or_create(
                nombre=cat_data['nombre'],
                defaults={'descripcion': cat_data['descripcion']}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ Categoría creada: {categoria.nombre}'))

        # ============= USUARIO ADMINISTRADOR =============
        self.stdout.write('\nCreando usuario administrador...')
        
        admin_email = 'admin@agriconecta.com'
        if not Usuario.objects.filter(email=admin_email).exists():
            admin = Usuario.objects.create_user(
                email=admin_email,
                password='admin123',
                nombre_completo='Administrador Sistema',
                telefono='12345678',
                activo=True
            )
            admin.is_staff = True
            admin.is_superuser = True
            admin.save()

            # Asignar rol de Administrador
            rol_admin = Rol.objects.get(nombre_rol='Administrador')
            UsuarioRol.objects.create(usuario=admin, rol=rol_admin)

            self.stdout.write(self.style.SUCCESS('  ✓ Usuario administrador creado'))
            self.stdout.write(self.style.WARNING('    Email: admin@agriconecta.com'))
            self.stdout.write(self.style.WARNING('    Password: admin123'))
        else:
            self.stdout.write('  - Usuario administrador ya existe')

        self.stdout.write(self.style.SUCCESS('\n¡Datos iniciales creados exitosamente! ✓'))