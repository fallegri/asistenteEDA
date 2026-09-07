import json
import base64
import io
import pandas as pd
import numpy as np
from http.server import BaseHTTPRequestHandler
from sklearn.impute import KNNImputer
from sklearn.preprocessing import LabelEncoder


def impute_dataframe(df: pd.DataFrame, method: str, params: dict) -> tuple:
    """Apply imputation method and return imputed df + new metrics"""
    df_imputed = df.copy()
    
    numeric_cols = df_imputed.select_dtypes(include='number').columns.tolist()
    categorical_cols = df_imputed.select_dtypes(include=['object']).columns.tolist()
    
    if method == 'knn':
        k = params.get('k', 5)
        # Encode categorical columns temporarily
        encoders = {}
        df_encoded = df_imputed.copy()
        
        for col in categorical_cols:
            le = LabelEncoder()
            # Fill NaN with a placeholder for encoding
            col_data = df_encoded[col].fillna('__NAN__')
            df_encoded[col] = le.fit_transform(col_data)
            encoders[col] = le
        
        # Apply KNN
        imputer = KNNImputer(n_neighbors=k)
        imputed_array = imputer.fit_transform(df_encoded)
        df_imputed = pd.DataFrame(imputed_array, columns=df_encoded.columns, index=df_encoded.index)
        
        # Decode categorical back
        for col in categorical_cols:
            le = encoders[col]
            # Round to nearest integer for categorical
            df_imputed[col] = df_imputed[col].round().astype(int)
            # Map back
            df_imputed[col] = df_imputed[col].apply(lambda x: le.inverse_transform([x])[0] if 0 <= x < len(le.classes_) else le.classes_[0])
            # Restore NaN placeholder
            df_imputed[col] = df_imputed[col].replace('__NAN__', np.nan)
        
    elif method == 'media':
        for col in numeric_cols:
            mean_val = df_imputed[col].mean()
            df_imputed[col] = df_imputed[col].fillna(mean_val)
        for col in categorical_cols:
            mode_val = df_imputed[col].mode()
            if len(mode_val) > 0:
                df_imputed[col] = df_imputed[col].fillna(mode_val[0])
                
    elif method == 'mediana':
        for col in numeric_cols:
            median_val = df_imputed[col].median()
            df_imputed[col] = df_imputed[col].fillna(median_val)
        for col in categorical_cols:
            mode_val = df_imputed[col].mode()
            if len(mode_val) > 0:
                df_imputed[col] = df_imputed[col].fillna(mode_val[0])
                
    elif method == 'agrupada':
        group_col = params.get('group_by')
        if group_col and group_col in df_imputed.columns:
            for col in numeric_cols:
                df_imputed[col] = df_imputed.groupby(group_col)[col].transform(lambda x: x.fillna(x.mean()))
            for col in categorical_cols:
                df_imputed[col] = df_imputed.groupby(group_col)[col].transform(lambda x: x.fillna(x.mode()[0] if len(x.mode()) > 0 else x.iloc[0]))
        else:
            # Fallback to media
            for col in numeric_cols:
                mean_val = df_imputed[col].mean()
                df_imputed[col] = df_imputed[col].fillna(mean_val)
    else:
        raise ValueError(f"Método no soportado: {method}")
    
    return df_imputed


def get_metrics(df: pd.DataFrame) -> dict:
    """Get metrics from dataframe"""
    df_clean = df.dropna()
    numeric_cols = df_clean.select_dtypes(include='number').columns
    
    metrics = {
        "filas_total": int(len(df)),
        "columnas": int(len(df.columns)),
        "valores_nulos": int(df.isnull().sum().sum()),
    }
    
    if len(numeric_cols) > 0 and len(df_clean) > 0:
        metrics["estadisticas"] = {
            "media": df_clean[numeric_cols].mean().to_dict(),
            "mediana": df_clean[numeric_cols].median().to_dict(),
            "varianza": df_clean[numeric_cols].var().to_dict(),
            "desviacion_estandar": df_clean[numeric_cols].std().to_dict(),
        }
    
    return metrics


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            request_data = json.loads(body.decode('utf-8'))
            
            file_reference = request_data.get('file_reference', '')
            method = request_data.get('method', 'knn')
            params = request_data.get('params', {})
            
            # In production, retrieve df from storage using file_reference
            # For demo, we expect the data to be sent or use a mock
            if 'data' in request_data:
                df = pd.DataFrame(request_data['data'])
            else:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Se requiere 'data' con el DataFrame"}).encode())
                return
            
            # Apply imputation
            df_imputed = impute_dataframe(df, method, params)
            
            # Get new metrics
            new_metrics = get_metrics(df_imputed)
            
            # Generate download data (CSV)
            csv_buffer = io.StringIO()
            df_imputed.to_csv(csv_buffer, index=False)
            csv_content = csv_buffer.getvalue()
            
            response = {
                "file_reference": file_reference,
                "method": method,
                "params": params,
                "new_metrics": new_metrics,
                "download_csv": base64.b64encode(csv_content.encode()).decode(),
                "preview": df_imputed.head(10).to_dict('records')
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response, default=str).encode())
            
        except Exception as e:
            import traceback
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e), "trace": traceback.format_exc()}).encode())