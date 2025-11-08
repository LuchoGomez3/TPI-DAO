# Sistema de Reservas de Canchas Deportivas

## Funcionalidades Principales

- ABM de clientes, canchas y horarios disponibles.
- Registro de reservas (cliente + cancha + fecha/hora).
- Validación de disponibilidad de la cancha antes de confirmar la reserva.
- Gestión de torneos o campeonatos.
- Control de iluminación o servicios asociados a cada cancha.

## Reportes Requeridos

- Listado de reservas por cliente.
- Reservas por cancha en un período.
- Canchas más utilizadas.
- Gráfico estadístico: utilización mensual de canchas.

## Opciones Adicionales (Mayor Complejidad)

- Administración de pagos en línea.

# Pasos para ejecutar el proyecto

### 1. Clonar el repositorio y crearse una rama propia de trabajo

```bash
git clone https://github.com/lucho/TPI-DAO.git
cd TPI-DAO
git checkout -b nombre_de_tu_rama
```

### 2. Crear un entorno virtual

```bash
python -m venv TPI_DAO
```

### 3. Activar el entorno virtual

```bash
# En Windows
TPI_DAO\Scripts\activate

# En Linux/Mac
source TPI_DAO/bin/activate
```

### 4. Instalar las dependencias

```bash
pip install -r requeriments.txt
```

### 5. Ejecutar el proyecto

```bash
uvicorn main:app --reload
```

### 6. Acceder a la API

```bash
http://127.0.0.1:8000/docs
```
