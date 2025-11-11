#!/usr/bin/env bash
# Backend/build.sh
# Script ejecutado por Render al hacer deploy

set -o errexit

# Usar settings de producción
export DJANGO_SETTINGS_MODULE=config.settings_prod

# Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt

# Colectar archivos estáticos
python manage.py collectstatic --no-input

# Ejecutar migraciones
python manage.py migrate --no-input

echo "✅ Build completado exitosamente"