# Cómo ejecutar el sistema

Ruta del proyecto: `/home/kiri/Documentos/sistema-campanas`

## Índice

1. [Requisitos](#1-requisitos)
2. [Primera vez (después de clonar el repo)](#2-primera-vez-después-de-clonar-el-repo)
3. [Levantar el sistema](#3-levantar-el-sistema) — elige Opción A o B
4. [Sembrar datos de prueba](#4-sembrar-datos-de-prueba)
5. [Ver la base de datos (Adminer)](#5-ver-la-base-de-datos-adminer)
6. [Generar el PDF/TXT de credenciales](#6-generar-el-pdftxt-de-credenciales)
7. [Apagar](#7-apagar)
8. [Otros comandos útiles](#8-otros-comandos-útiles)

---

## 1. Requisitos

- Docker + Docker Compose
- Node.js v20 o superior

---

## 2. Primera vez (después de clonar el repo)

```bash
cd /home/kiri/Documentos/sistema-campanas
cp .env.example .env
```

Genera valores reales para los secretos (los de `.env.example` son placeholders inválidos a propósito). Corre esto y pega cada resultado en el `.env` que acabas de crear:

```bash
# para AES_KEY_B64=
python3 -c "import secrets, base64; print(base64.b64encode(secrets.token_bytes(32)).decode())"

# para JWT_SECRET= (corre esto DOS veces: una para JWT_SECRET, otra para HUELLA_SECRET — deben ser distintos)
python3 -c "import secrets; print(secrets.token_urlsafe(48))"
```

Instala las dependencias del frontend:

```bash
cd /home/kiri/Documentos/sistema-campanas/frontend
npm install
```

---

## 3. Levantar el sistema

Dos formas de correrlo. Usa **A** si solo vas a usar/presentar la app; usa **B** si vas a editar el frontend.

### Opción A — Un solo comando

El backend sirve el frontend ya compilado, en el mismo proceso y puerto.

```bash
cd /home/kiri/Documentos/sistema-campanas
cd frontend && npm run build && cd ..
docker compose up -d
```

**Abre → http://localhost:8000**

> Solo repites el `npm run build` si vuelves a tocar código del frontend. `docker compose up -d` lo puedes correr las veces que quieras, no hace nada si ya está arriba.

### Opción B — Modo desarrollo (dos terminales)

**Terminal 1:**
```bash
cd /home/kiri/Documentos/sistema-campanas
docker compose up -d
```

**Terminal 2:**
```bash
cd /home/kiri/Documentos/sistema-campanas/frontend
npm run dev
```

**Abre → http://localhost:5173** (recarga sola cada vez que guardas un cambio en el frontend)

---

Con cualquiera de las dos opciones, confirma que no haya errores:

```bash
cd /home/kiri/Documentos/sistema-campanas
docker compose ps
docker compose logs backend --tail 30
```

---

## 4. Sembrar datos de prueba

Solo la primera vez, o después de resetear la base:

```bash
cd /home/kiri/Documentos/sistema-campanas
docker compose exec backend python -m app.seed
```

Genera `backend/seed_credentials.txt` con usuario/contraseña de cada cuenta (CMs + admin). Archivo local, no se sube a git.

Inicia sesión con cualquiera de esas cuentas en la URL que abriste en el paso 3.

---

## 5. Ver la base de datos (Adminer)

**No es un comando aparte.** Adminer ya está incluido en `docker-compose.yml` y arranca solo con el `docker compose up -d` del paso 3 (opción A o B, cualquiera de las dos).

**Abre → http://localhost:8080**

Datos de conexión:

| Campo | Valor |
|---|---|
| Sistema | PostgreSQL |
| Servidor | `db` |
| Usuario | `campanas` |
| Contraseña | `campanas` |
| Base de datos | `campanas` |

### Alternativa por terminal (sin instalar nada)

```bash
cd /home/kiri/Documentos/sistema-campanas
docker compose exec db psql -U campanas -d campanas
```

Dentro de `psql`:
- `\dt` — listar tablas
- `\d nombre_tabla` — ver estructura de una tabla
- `SELECT * FROM usuarios;` — consultar datos
- `\q` — salir

### Alternativa con app de escritorio

DBeaver, TablePlus o pgAdmin, conectando a `localhost:5433` con los mismos datos de la tabla de arriba.

---

## 6. Generar el PDF/TXT de credenciales

Para entregar usuario/contraseña de cada CM y admin:

```bash
cd /home/kiri/Documentos/sistema-campanas
docker compose exec backend python generar_credenciales_entrega.py
```

Genera `backend/credenciales_entrega.pdf` y `.txt`. Tampoco se suben a git — son secretos.

---

## 7. Apagar

```bash
cd /home/kiri/Documentos/sistema-campanas

docker compose down        # apaga backend + base de datos + Adminer, conserva los datos
docker compose down -v     # apaga TODO y BORRA los datos de la base (irreversible)
```

Si usaste la opción B, además presiona `Ctrl+C` en la terminal donde corre `npm run dev`.

---

## 8. Otros comandos útiles

**Aplicar migraciones nuevas a mano** (normalmente se aplican solas al reiniciar el contenedor):

```bash
cd /home/kiri/Documentos/sistema-campanas
docker compose exec backend python -m app.migrations.run_migrations
```

**Correr los jobs programados sin esperar al cron real** (cierre de semana, recordatorio, cierre de ciclo, purga de no renovados):

```bash
cd /home/kiri/Documentos/sistema-campanas
docker compose exec backend python -m app.jobs.cierre_semana
docker compose exec backend python -m app.jobs.recordatorio
docker compose exec backend python -m app.jobs.cierre_ciclo
docker compose exec backend python -m app.jobs.purga_no_renovados
```
