from rest_framework import permissions


class EsAdministrador(permissions.BasePermission):
    """
    Permiso para Administradores (Gerencia)
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and \
               request.user.roles.filter(nombre_rol='Administrador').exists()


class EsPersonalVivero(permissions.BasePermission):
    """
    Permiso para Personal de Vivero y Logística
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and \
               request.user.roles.filter(nombre_rol__in=['Administrador', 'Personal Vivero']).exists()


class EsTecnicoCampo(permissions.BasePermission):
    """
    Permiso para Técnicos de Campo
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and \
               request.user.roles.filter(nombre_rol__in=['Administrador', 'Personal Vivero', 'Tecnico Campo']).exists()


class EsAgricultor(permissions.BasePermission):
    """
    Permiso para Agricultores (Clientes)
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and \
               request.user.roles.filter(nombre_rol='Agricultor').exists()


class EsAgricultorOAdmin(permissions.BasePermission):
    """
    Permiso para Agricultores o Administradores
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and \
               request.user.roles.filter(nombre_rol__in=['Administrador', 'Agricultor']).exists()


class EsPersonalViveroOAdmin(permissions.BasePermission):
    """
    Permiso para Personal de Vivero o Administradores
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and \
               request.user.roles.filter(nombre_rol__in=['Administrador', 'Personal Vivero']).exists()