import json
import pandas as pd
import io

def handler(event, context):
    """POST /api/analyze - Recibir archivo, parsearlo y devolver metadatos"""
    try:
        body = event.get('body', '')
        if isinstance(body, str):
            import base64
            body = base64.b64decode(body).decode('utf-8')
        
        # Parse multipart form data (simplified)
        if 'file' in body:
            # Read the uploaded file
            files = [f for f in body.split('filename="') if f]
            
        # For now, return empty analysis structure
        result = {
            "forma_dataset": {"filas": 0, "columnas": 0},
            "columnas_nulos": {},
            "metricas_base": {
                "media": 0, "varianza": 0, "desviacion_estandar": 0,
                "minimo": 0, "maximo": 0, "cuartiles": [0, 0, 0]
            }
        }
        
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(result)
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)})
        }