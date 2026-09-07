import json
import base64
import io
import pandas as pd
from http.server import BaseHTTPRequestHandler


def parse_multipart(body: bytes, content_type: str):
    """Parse multipart/form-data"""
    if 'multipart/form-data' not in content_type:
        return {}, {}
    
    boundary = content_type.split('boundary=')[1].encode()
    parts = body.split(b'--' + boundary)
    
    files = {}
    fields = {}
    
    for part in parts:
        if not part.strip() or part.strip() == b'--':
            continue
        
        headers_end = part.find(b'\r\n\r\n')
        if headers_end == -1:
            continue
            
        headers_raw = part[:headers_end].decode('utf-8', errors='ignore')
        content = part[headers_end + 4:-2]  # remove \r\n\r\n and trailing \r\n
        
        # Parse headers
        content_disposition = ''
        for line in headers_raw.split('\r\n'):
            if 'content-disposition' in line.lower():
                content_disposition = line.split(':', 1)[1].strip()
                break
        
        name = ''
        filename = ''
        for item in content_disposition.split(';'):
            item = item.strip()
            if item.startswith('name='):
                name = item[6:-1] if item.endswith('"') else item[5:]
            elif item.startswith('filename='):
                filename = item[10:-1] if item.endswith('"') else item[9:]
        
        if filename:
            files[name] = {'filename': filename, 'content': content}
        else:
            fields[name] = content.decode('utf-8', errors='ignore')
    
    return fields, files


def analyze_dataframe(df: pd.DataFrame) -> dict:
    """Analyze dataframe and return metrics"""
    df_clean = df.dropna()
    numeric_cols = df_clean.select_dtypes(include='number').columns
    
    metrics = {
        "filas_total": int(len(df)),
        "columnas": int(len(df.columns)),
        "columnas_con_nulos": int(df.isnull().sum().sum()),
        "porcentaje_nulos": round(df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100, 2) if len(df) > 0 else 0,
        "nulos_por_columna": df.isnull().sum().to_dict(),
        "tipos_dato": {col: str(dtype) for col, dtype in df.dtypes.items()},
    }
    
    if len(numeric_cols) > 0 and len(df_clean) > 0:
        metrics["estadisticas"] = {
            "media": df_clean[numeric_cols].mean().to_dict(),
            "mediana": df_clean[numeric_cols].median().to_dict(),
            "varianza": df_clean[numeric_cols].var().to_dict(),
            "desviacion_estandar": df_clean[numeric_cols].std().to_dict(),
            "minimo": df_clean[numeric_cols].min().to_dict(),
            "maximo": df_clean[numeric_cols].max().to_dict(),
        }
    
    return metrics


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            content_type = self.headers.get('Content-Type', '')
            
            fields, files = parse_multipart(body, content_type)
            
            if 'file' not in files:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "No se envió archivo"}).encode())
                return
            
            file_data = files['file']
            filename = file_data['filename']
            content = file_data['content']
            
            # Read file based on extension
            if filename.endswith('.csv'):
                df = pd.read_csv(io.BytesIO(content))
            elif filename.endswith('.xlsx') or filename.endswith('.xls'):
                df = pd.read_excel(io.BytesIO(content))
            else:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Formato no soportado. Use .csv o .xlsx"}).encode())
                return
            
            # Analyze
            metrics = analyze_dataframe(df)
            
            # Generate file reference for imputation
            import uuid
            file_reference = str(uuid.uuid4())
            
            # Store in memory (in production use Redis/temp storage)
            # For now, return metrics and reference
            response = {
                "file_reference": file_reference,
                "metrics": metrics,
                "preview": df.head(10).to_dict('records'),
                "columns": df.columns.tolist()
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response, default=str).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())