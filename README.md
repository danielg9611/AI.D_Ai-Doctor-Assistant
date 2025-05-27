# AID - Asistente Inteligente para Consultas Médicas
<p align="center">
  <img src="docs/img/Logo-clear.png" alt="AID Logo" width="300"/>
</p>

AID es una plataforma inteligente diseñada para optimizar la atención médica, facilitando la recopilación y organización de información clínica tanto para pacientes como para doctores. Gracias a su asistente conversacional basado en IA, AID permite a los pacientes describir sus síntomas de manera sencilla y empática, generando automáticamente resúmenes claros y estructurados para los profesionales de la salud. Esto no solo agiliza el flujo de pacientes y reduce el tiempo de consulta, sino que también ayuda a los doctores a tomar decisiones más informadas, mejorando la calidad del diagnóstico y la eficiencia operativa en clínicas y consultorios.

---

## Características

- 🤖 **Asistente conversacional para pacientes:** Utiliza IA para guiar al paciente en la descripción de sus síntomas y antecedentes, con un lenguaje claro, empático y adaptado a personas sin conocimientos médicos.
- 🩺 **Resumen automático para doctores:** Genera resúmenes estructurados y profesionales de la información recopilada, facilitando la revisión y el diagnóstico por parte del médico.
- 🧑‍⚕️ **Sugerencia de diagnóstico y especialidad:** El sistema analiza los síntomas y sugiere posibles padecimientos, la especialidad médica recomendada y el nivel de urgencia del caso.
- 📋 **Gestión de tickets clínicos:** Permite crear, visualizar y gestionar tickets de consulta, centralizando la información relevante de cada paciente y su evolución.
- ⏱️ **Optimización del flujo de pacientes:** Reduce el tiempo de consulta y mejora la eficiencia operativa, permitiendo a los doctores atender a más pacientes con información precisa desde el inicio.
- 🔒 **Privacidad y seguridad:** Manejo seguro de los datos clínicos y personales, cumpliendo con buenas prácticas de protección de la información.
- 🌐 **Interfaz web intuitiva:** Acceso fácil desde cualquier navegador, sin necesidad de instalaciones complejas.
- 🛠️ **Integración con fuentes médicas:** Acceso a información científica relevante (por ejemplo, PubMed) para enriquecer las respuestas y recomendaciones.

---

## Estructura del Proyecto

```
.
├── app.py                # Interfaz Streamlit (frontend)
├── api.py                # API FastAPI (backend)
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env                  # Variables de entorno
└── docs/
    └── img/
        └── Logo-clear.png
```

---

## Requisitos

- Docker y Docker Compose instalados
- Cuenta en Docker Hub (opcional, para subir imágenes)
- Archivo `.env` con las variables necesarias para la base de datos y APIs

---

## Variables de Entorno

Crea un archivo `.env` en la raíz con el siguiente contenido (ajusta los valores):

```
DB_NAME=aid_db
DB_USER=postgres
DB_PASSWORD=tu_password
DB_HOST=localhost
DB_PORT=5432
GEMINI_API_KEY=tu_api_key
```

---

## Uso rápido

### 1. Clona el repositorio

```sh
git clone https://github.com/tu_usuario/aid.git
cd aid
```

### 2. Configura el archivo `.env`

Copia el ejemplo anterior y ajústalo a tu entorno.

### 3. Construye y levanta los servicios

```sh
docker compose up --build
```

Esto levantará dos servicios:
- **api**: FastAPI en el puerto `8000`
- **streamlit**: Interfaz web en el puerto `8501`

### 4. Accede a la aplicación

- Interfaz web: [http://localhost:8501](http://localhost:8501)
- API: [http://localhost:8000/docs](http://localhost:8000/docs) (documentación Swagger)

---

## Subir imágenes a Docker Hub (opcional)

1. Haz login:
   ```sh
   docker login
   ```
2. Construye las imágenes:
   ```sh
   docker compose build
   ```
3. Sube cada imagen:
   ```sh
   docker push TU_USUARIO_DOCKER/aid-api:latest
   docker push TU_USUARIO_DOCKER/aid-streamlit:latest
   ```

---

## Notas técnicas

- La comunicación entre servicios se realiza usando los nombres de los servicios definidos en `docker-compose.yml` (por ejemplo, la interfaz usa `http://api:8000` para llamar a la API).
- La base de datos utilizada es PostgreSQL (debes tenerla corriendo y accesible desde los contenedores).
- El frontend utiliza [LangChain](https://python.langchain.com/) y Gemini API para la IA conversacional.

---

## Licencia

MIT

---

## Autor

Daniel G.