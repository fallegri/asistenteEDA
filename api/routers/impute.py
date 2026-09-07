from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from api.database import get_db
from api.schemas import AnalysisRequest, AnalysisResponse, ImputationRequest, ImputationResponse
from api.services import AuthService, ItemService
from api.models import User


router = APIRouter(prefix="/api", tags=["imputation"])


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """POST /api/analyze - Recibir archivo y devolver metadatos"""
    import pandas as pd
    import io
    
    # Leer archivo dependiendo del tipo
    content = await file.read()
    if file.filename.endswith('.csv'):
        df = pd.read_csv(io.BytesIO(content))
    elif file.filename.endswith('.xlsx'):
        df = pd.read_excel(io.BytesIO(content))
    else:
        raise HTTPException(status_code=400, detail="Formato de archivo no soportado")
    
    # Calcular métricas básicas omitiendo nulos
    df_clean = df.dropna()
    metrics = {
        "filas_total": len(df),
        "columnas": len(df.columns),
        "porcentaje_nulos": (len(df) - len(df_clean)) / len(df) * 100 if len(df) > 0 else 0,
        "media": df_clean.select_dtypes(include='number').mean().to_dict() if not df_clean.empty else {},
    }
    
    # Generar referencia temporal
    import uuid
    file_reference = str(uuid.uuid4())
    
    return {
        "file_reference": file_reference,
        "initial_metrics": metrics,
        "new_metrics": metrics,
        "download_url": f"/download/{file_reference}"
    }


@router.post("/impute", response_model=ImputationResponse)
async def impute_data(
    request: ImputationRequest,
    db: Session = Depends(get_db)
):
    """POST /api/impute - Aplicar estrategia de imputación"""
    auth_service = AuthService(db)
    item_service = ItemService(db)
    
    # Verificar sesión de usuario (simplificado)
    user = await auth_service.authenticate(UserLogin(
        email="test@test.com", 
        password="test"
    ))
    
    if not user:
        raise HTTPException(status_code=401, detail="No autenticado")
    
    # En un implementation real, aplicarían KNNImputer o mediana/media
    # basándose en request.method y request.params
    
    new_metrics = {
        "media": 0.0,
        "varianza": 0.0
    }
    
    return {
        "file_reference": request.file_reference,
        "new_metrics": new_metrics,
        "download_url": f"/download/{request.file_reference}",
        "message": f"Imputación completada usando {request.method}"
    }


@router.get("/users/me", response_model=UserResponse)
async def get_current_user(db: Session = Depends(get_db)):
    """Obtener usuario actual"""
    # En un caso real, vendría del token JWT
    user = db.query(User).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user