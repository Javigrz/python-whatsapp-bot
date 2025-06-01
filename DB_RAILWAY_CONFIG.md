# Configuración de Base de Datos en Railway

Este documento proporciona información sobre la configuración actual de la base de datos PostgreSQL en Railway para el proyecto WhatsApp Bot.

## Servicios PostgreSQL

El proyecto utiliza un servicio PostgreSQL dedicado llamado **Postgres-Eroj** en Railway.

### Credenciales de Conexión

Hay dos formas de conectar a la base de datos:

1. **Conexión Interna** (solo desde dentro de Railway):
   - Host: `postgres-eroj.railway.internal`
   - Puerto: `5432`
   - Base de datos: `railway`
   - Usuario: `postgres`
   - URL completa: `postgresql://postgres:PASSWORD@postgres-eroj.railway.internal:5432/railway`

2. **Conexión Externa** (desde fuera de Railway):
   - Host: `shuttle.proxy.rlwy.net`
   - Puerto: `24766`
   - Base de datos: `railway`
   - Usuario: `postgres`
   - URL completa: `postgresql://postgres:PASSWORD@shuttle.proxy.rlwy.net:24766/railway`

> Nota: La contraseña real está configurada como una variable de entorno segura en Railway.

## Modo de Conexión

La aplicación intentará conectarse automáticamente a la base de datos usando diferentes configuraciones de SSL para adaptarse al entorno:

- En Railway: Utilizará la conexión interna con `postgres-eroj.railway.internal` cuando sea posible
- Localmente: Utilizará la conexión proxy externa con `shuttle.proxy.rlwy.net`

## Solución de Problemas

Si hay problemas con la conexión a la base de datos:

1. Verifica que el servicio PostgreSQL esté funcionando en Railway
2. Comprueba que la variable `DATABASE_URL` esté correctamente configurada
3. Si estás usando la conexión externa, asegúrate de que el puerto `24766` esté abierto en tu firewall
4. Ejecuta el script `railway_health_check.py` para diagnosticar problemas

## Tablas de la Base de Datos

La base de datos contiene las siguientes tablas principales:

- `agents`: Almacena información sobre los agentes de WhatsApp
- `clients`: Gestiona los clientes que usan el servicio
- `threads`: Almacena las conversaciones entre agentes y clientes

## Mantenimiento

Para respaldar la base de datos:

```sh
railway service postgres-eroj
railway run pg_dump > backup.sql
```

Para restaurar la base de datos:

```sh
cat backup.sql | railway run psql
```
