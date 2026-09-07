# Plataforma de Imputación y Análisis Multivariado

API para análisis de datos con valores faltantes e imputación (KNN, Media, Mediana, Agrupada).

## Stack
- **Backend**: FastAPI + SQLAlchemy + Pydantic
- **Auth**: JWT + bcrypt (OWASP A02/A07)
- **Imputación**: scikit-learn KNNImputer
- **Tests**: pytest + TestClient
- **BDD**: Gherkin (.feature files)

## Inicio rápido

```bash
# 1. Clonar y entrar
cd edaAssistant

# 2. Variables de entorno
cp .env.example .env
# Editar .env con JWT_SECRET_KEY seguro

# 3. Instalar dependencias
pip install -e .

# 4. Ejecutar API
uvicorn api.main:app --reload

# 5. Tests
pytest tests/ -v

# 6. BDD (behave)
pip install behave
behave features/
```

## Endpoints principales

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/auth/register` | Registrar usuario |
| POST | `/auth/login` | Login + JWT |
| GET | `/auth/me` | Usuario actual |
| POST | `/items/` | Crear item (requiere auth) |
| GET | `/items/` | Listar items (requiere auth) |
| GET | `/items/{id}` | Obtener item (requiere auth) |
| PATCH | `/items/{id}` | Actualizar item (requiere auth) |
| DELETE | `/items/{id}` | Soft delete (requiere auth) |

## Estructura
```
edaAssistant/
├── api/
│   ├── main.py              # App FastAPI
│   ├── database.py          # SQLAlchemy setup
│   ├── models.py            # Modelos User, Item
│   ├── schemas/
│   │   ├── user.py          # UserCreate, UserResponse, UserUpdate
│   │   └── item.py          # ItemCreate, ItemResponse, ItemUpdate
│   ├── repositories/
│   │   ├── user_repository.py
│   │   └── item_repository.py
│   ├── services/
│   │   ├── auth_service.py  # bcrypt + JWT
│   │   └── item_service.py
│   └── routers/
│       ├── auth_router.py
│       └── item_router.py
├── tests/
│   ├── conftest.py          # Fixtures
│   └── unit/
│       ├── test_auth.py     # 5 tests OWASP
│       └── test_item.py     # 11 tests CRUD
├── features/
│   ├── analysis.feature
│   ├── imputation.feature
│   └── export.feature
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── .env.example
```

## Calidad (Arcana)
- **SOLID**: 100/100 (0 violaciones)
- **OWASP**: 100/100 (0 findings)
- **Tests**: 16/16 passing
- **BDD**: 3 feature files

## Despliegue

### Docker
```bash
docker-compose up -d
```

### Vercel (Frontend) + Railway/Render (Backend)
1. Push a GitHub
2. Conectar repo en Vercel (frontend) y Railway (backend)
3. Configurar variables de entorno
4. Deploy automático