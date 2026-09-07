"use client";

import React, { useState, useRef, useCallback } from "react";

interface Metrics {
  filas_total: number;
  columnas: number;
  columnas_con_nulos: number;
  porcentaje_nulos: number;
  valores_nulos?: number;
  nulos_por_columna: Record<string, number>;
  tipos_dato: Record<string, string>;
  estadisticas?: {
    media: Record<string, number>;
    mediana: Record<string, number>;
    varianza: Record<string, number>;
    desviacion_estandar: Record<string, number>;
    minimo: Record<string, number>;
    maximo: Record<string, number>;
  };
}

interface ColumnInfo {
  name: string;
  type: string;
  nulls: number;
  nullPercent: number;
}

export default function Home() {
  const [step, setStep] = useState<"upload" | "analyze" | "impute">("upload");
  const [file, setFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [fileReference, setFileReference] = useState<string>("");
  const [previewData, setPreviewData] = useState<Record<string, unknown>[]>([]);
  const [columns, setColumns] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [imputedData, setImputedData] = useState<Record<string, unknown>[] | null>(null);
  const [newMetrics, setNewMetrics] = useState<Metrics | null>(null);
  const [selectedMethod, setSelectedMethod] = useState<"knn" | "media" | "mediana" | "agrupada">("knn");
  const [knnK, setKnnK] = useState(5);
  const [groupBy, setGroupBy] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  const methods = [
    { id: "knn", label: "KNN Predictivo", desc: "Usa vecinos más cercanos (ideal para datos correlacionados)", icon: "🤖" },
    { id: "media", label: "Media", desc: "Rellena con el promedio (sensible a outliers)", icon: "📊" },
    { id: "mediana", label: "Mediana", desc: "Rellena con la mediana (robusta a outliers)", icon: "📈" },
    { id: "agrupada", label: "Agrupada", desc: "Rellena por grupos/categorías", icon: "🔢" },
  ];

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const analyzeFile = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("/api/analyze", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();

      if (!res.ok) throw new Error(data.error || "Error al analizar");

      setMetrics(data.metrics);
      setFileReference(data.file_reference);
      setPreviewData(data.preview || []);
      setColumns(data.columns || []);
      setStep("analyze");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error desconocido");
    } finally {
      setLoading(false);
    }
  };

  const imputeData = async () => {
    if (!fileReference || previewData.length === 0) return;
    setLoading(true);
    setError(null);

    const params: Record<string, unknown> = {};
    if (selectedMethod === "knn") params.k = knnK;
    if (selectedMethod === "agrupada") params.group_by = groupBy;

    try {
      const res = await fetch("/api/impute", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          file_reference: fileReference,
          method: selectedMethod,
          params,
          data: previewData,
        }),
      });

      const data = await res.json();

      if (!res.ok) throw new Error(data.error || "Error en imputación");

      setImputedData(data.preview || []);
      setNewMetrics(data.new_metrics || null);
      setStep("impute");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error desconocido");
    } finally {
      setLoading(false);
    }
  };

  const downloadCSV = () => {
    if (!imputedData || imputedData.length === 0) return;
    const csv = [
      Object.keys(imputedData[0]).join(","),
      ...imputedData.map(row => Object.values(row).map(v => `"${v}"`).join(",")),
    ].join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "dataset_imputado.csv";
    a.click();
    URL.revokeObjectURL(url);
  };

  const reset = () => {
    setStep("upload");
    setFile(null);
    setMetrics(null);
    setFileReference("");
    setPreviewData([]);
    setColumns([]);
    setImputedData(null);
    setNewMetrics(null);
    setError(null);
  };

  const columnInfo: ColumnInfo[] = columns.map(col => ({
    name: col,
    type: metrics?.tipos_dato[col] || "unknown",
    nulls: metrics?.nulos_por_columna[col] || 0,
    nullPercent: metrics ? ((metrics.nulos_por_columna[col] || 0) / metrics.filas_total) * 100 : 0,
  }));

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow-sm border-b dark:border-gray-700">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            📊 Plataforma de Imputación y Análisis Multivariado
          </h1>
          <p className="text-gray-600 dark:text-gray-400 text-sm mt-1">
            Sube tu dataset, analiza nulos y aplica imputación (KNN, Media, Mediana, Agrupada)
          </p>
        </div>
      </header>

      {/* Progress Steps */}
      <div className="max-w-6xl mx-auto px-4 py-4">
        <div className="flex items-center justify-center">
          {["upload", "analyze", "impute"].map((s, i) => (
            <React.Fragment key={s}>
              <div
                className={`flex flex-col items-center ${
                  (step === s || (step === "analyze" && s === "upload") || (step === "impute" && (s === "upload" || s === "analyze")))
                    ? "text-blue-600 dark:text-blue-400"
                    : "text-gray-400 dark:text-gray-500"
                }`}
              >
                <div
                  className={`w-10 h-10 rounded-full border-2 flex items-center justify-center font-bold ${
                    (step === s || (step === "analyze" && s === "upload") || (step === "impute" && (s === "upload" || s === "analyze")))
                      ? "border-blue-600 bg-blue-600 text-white"
                      : "border-gray-300 dark:border-gray-600"
                  }`}
                >
                  {i + 1}
                </div>
                <span className="text-xs mt-1 font-medium">
                  {s === "upload" && "Subir"}
                  {s === "analyze" && "Analizar"}
                  {s === "impute" && "Imputar"}
                </span>
              </div>
              {i < 2 && (
                <div
                  className={`w-16 h-0.5 mx-2 ${
                    (step === "analyze" || step === "impute") ? "bg-blue-600" : "bg-gray-300 dark:bg-gray-600"
                  }`}
                />
              )}
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-4 py-8">
        {error && (
          <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-lg text-red-700 dark:text-red-300">
            {error}
          </div>
        )}

        {/* Step 1: Upload */}
        {step === "upload" && (
          <div className="max-w-2xl mx-auto">
            <div
              className={`border-2 border-dashed rounded-xl p-12 text-center transition-colors ${
                dragActive
                  ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20"
                  : "border-gray-300 dark:border-gray-600 hover:border-blue-400"
              }`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".csv,.xlsx,.xls"
                onChange={handleFileChange}
                className="hidden"
                id="file-input"
              />
              <label htmlFor="file-input" className="cursor-pointer">
                <div className="text-6xl mb-4">📁</div>
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                  Arrastra tu archivo aquí o haz clic
                </h3>
                <p className="text-gray-600 dark:text-gray-400">
                  Formatos: .csv, .xlsx, .xls · Máx. 10MB
                </p>
              </label>
              {file && (
                <div className="mt-6 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg text-left">
                  <p className="font-medium text-green-800 dark:text-green-300">✅ Archivo seleccionado:</p>
                  <p className="text-sm text-gray-700 dark:text-gray-300 mt-1">{file.name} ({(file.size / 1024).toFixed(1)} KB)</p>
                </div>
              )}
            </div>

            {file && (
              <div className="mt-6 text-center">
                <button
                  onClick={analyzeFile}
                  disabled={loading}
                  className="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-semibold py-3 px-6 rounded-lg transition-colors"
                >
                  {loading ? "Analizando..." : "🔍 Analizar Dataset"}
                </button>
              </div>
            )}
          </div>
        )}

        {/* Step 2: Analysis Results */}
        {step === "analyze" && metrics && (
          <div className="space-y-6">
            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <StatCard label="Filas" value={metrics.filas_total.toLocaleString()} icon="📋" />
              <StatCard label="Columnas" value={metrics.columnas} icon="📊" />
              <StatCard
                label="% Nulos"
                value={`${metrics.porcentaje_nulos.toFixed(1)}%`}
                icon="⚠️"
                color={metrics.porcentaje_nulos > 20 ? "red" : metrics.porcentaje_nulos > 5 ? "yellow" : "green"}
              />
              <StatCard label="Celdas nulas" value={metrics.columnas_con_nulos.toLocaleString()} icon="🕳️" />
            </div>

            {/* Columns Table */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border dark:border-gray-700 overflow-hidden">
              <div className="p-4 border-b dark:border-gray-700">
                <h3 className="font-semibold text-gray-900 dark:text-white">📋 Detalle por Columna</h3>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50 dark:bg-gray-700/50">
                    <tr>
                      <th className="p-3 text-left text-sm font-medium text-gray-500 dark:text-gray-400">Columna</th>
                      <th className="p-3 text-left text-sm font-medium text-gray-500 dark:text-gray-400">Tipo</th>
                      <th className="p-3 text-left text-sm font-medium text-gray-500 dark:text-gray-400">Nulos</th>
                      <th className="p-3 text-left text-sm font-medium text-gray-500 dark:text-gray-400">% Nulos</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                    {columnInfo.map((col) => (
                      <tr key={col.name} className="hover:bg-gray-50 dark:hover:bg-gray-700/50">
                        <td className="p-3 font-mono text-sm">{col.name}</td>
                        <td className="p-3 text-sm text-gray-600 dark:text-gray-400">{col.type}</td>
                        <td className="p-3 text-sm">{col.nulls ?? 0}</td>
                        <td className="p-3">
                          <div className="w-24 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                            <div
                              className={`h-full rounded-full transition-all ${
                                col.nullPercent > 20 ? "bg-red-500" : col.nullPercent > 5 ? "bg-yellow-500" : "bg-green-500"
                              }`}
                              style={{ width: `${Math.min(col.nullPercent, 100)}%` }}
                            />
                          </div>
                          <span className="text-xs text-gray-500 dark:text-gray-400 mt-1 block">{col.nullPercent.toFixed(1)}%</span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Statistics */}
            {metrics.estadisticas && (
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border dark:border-gray-700 overflow-hidden">
                <div className="p-4 border-b dark:border-gray-700">
                  <h3 className="font-semibold text-gray-900 dark:text-white">📈 Estadísticas Descriptivas (sin nulos)</h3>
                </div>
                <div className="overflow-x-auto p-4">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="text-left text-gray-500 dark:text-gray-400">
                        <th className="p-2">Métrica</th>
                        {Object.keys(metrics.estadisticas.media).map((col) => (
                          <th key={col} className="p-2 font-mono">{col}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {Object.entries(metrics.estadisticas).map(([metric, values]) => (
                        <tr key={metric} className="border-t dark:border-gray-700">
                          <td className="p-2 font-medium capitalize">{metric}</td>
                          {Object.entries(values).map(([, val]) => (
                            <td key={val} className="p-2 font-mono text-gray-700 dark:text-gray-300">
                              {typeof val === "number" ? val.toFixed(4) : val}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Preview */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border dark:border-gray-700 overflow-hidden">
              <div className="p-4 border-b dark:border-gray-700 flex justify-between items-center">
                <h3 className="font-semibold text-gray-900 dark:text-white">👁️ Vista Previa (10 primeras filas)</h3>
                <button
                  onClick={() => setStep("impute")}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                >
                  Continuar a Imputación →
                </button>
              </div>
              <div className="overflow-x-auto p-4 max-h-64">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="text-left text-gray-500 dark:text-gray-400 border-b dark:border-gray-700">
                      {columns.map((col) => (
                        <th key={col} className="p-2 font-mono">{col}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {previewData.slice(0, 10).map((row, i) => (
                      <tr key={i} className="border-b dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700/50">
                        {columns.map((col) => (
                          <td key={col} className="p-2 text-gray-700 dark:text-gray-300">
                            {row[col] === null || row[col] === undefined ? (
                              <span className="text-red-500 italic">NULL</span>
                            ) : (
                              String(row[col])
                            )}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* Step 3: Imputation */}
        {step === "impute" && (
          <div className="space-y-6">
            {/* Method Selector */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border dark:border-gray-700 p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">🔧 Seleccionar Método de Imputación</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {methods.map((m) => (
                  <button
                    key={m.id}
                    onClick={() => setSelectedMethod(m.id as typeof selectedMethod)}
                    className={`p-4 rounded-xl border-2 text-left transition-all ${
                      selectedMethod === m.id
                        ? "border-blue-600 bg-blue-50 dark:bg-blue-900/30"
                        : "border-gray-200 dark:border-gray-700 hover:border-blue-300"
                    }`}
                  >
                    <div className="text-3xl mb-2">{m.icon}</div>
                    <div className="font-semibold text-gray-900 dark:text-white">{m.label}</div>
                    <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">{m.desc}</div>
                  </button>
                ))}
              </div>

              {/* Method-specific params */}
              {selectedMethod === "knn" && (
                <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    K (vecinos): {knnK}
                  </label>
                  <input
                    type="range"
                    min="1"
                    max="20"
                    value={knnK}
                    onChange={(e) => setKnnK(Number(e.target.value))}
                    className="w-full h-2 bg-blue-200 dark:bg-blue-800 rounded-lg appearance-none cursor-pointer accent-blue-600"
                  />
                  <p className="text-xs text-blue-700 dark:text-blue-300 mt-1">
                    Valor más alto = más suave, más bajo = más local
                  </p>
                </div>
              )}

              {selectedMethod === "agrupada" && (
                <div className="mt-4 p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg border border-purple-200 dark:border-purple-800">
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Columna para agrupar
                  </label>
                  <select
                    value={groupBy}
                    onChange={(e) => setGroupBy(e.target.value)}
                    className="w-full md:w-1/2 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  >
                    <option value="">Seleccionar columna categórica...</option>
                    {columns
                      .filter(c => metrics?.tipos_dato[c] === "object")
                      .map(c => <option key={c} value={c}>{c}</option>)}
                  </select>
                </div>
              )}
            </div>

            {/* Run Imputation */}
            <div className="text-center">
              <button
                onClick={imputeData}
                disabled={loading}
                className="w-full md:w-1/2 mx-auto bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white font-semibold py-3 px-8 rounded-lg text-lg transition-colors"
              >
                {loading ? "⏳ Imputando..." : "✨ Aplicar Imputación"}
              </button>
            </div>
          </div>
        )}

        {/* Results */}
        {step === "impute" && newMetrics && (
          <div className="space-y-6 animate-fade-in">
            <div className="bg-green-50 dark:bg-green-900/30 border border-green-200 dark:border-green-800 rounded-xl p-6">
              <h3 className="text-lg font-semibold text-green-800 dark:text-green-300 mb-4 flex items-center gap-2">
                ✅ Imputación Completada ({selectedMethod.toUpperCase()})
              </h3>
              
              {/* Comparison */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg border border-red-200 dark:border-red-800">
                  <h4 className="font-semibold text-red-800 dark:text-red-300 mb-3 flex items-center gap-2">❌ Antes</h4>
                  {metrics && metrics.estadisticas && (
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span>Filas con nulos</span>
                        <span className="font-mono">{metrics.columnas_con_nulos ?? 0}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Varianza (promedio)</span>
                        <span className="font-mono">
                          {Object.values(metrics.estadisticas.varianza).reduce((a, b) => a + b, 0) / Object.keys(metrics.estadisticas.varianza).length}
                        </span>
                      </div>
                    </div>
                  )}
                </div>
                <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg border border-green-200 dark:border-green-800">
                  <h4 className="font-semibold text-green-800 dark:text-green-300 mb-3 flex items-center gap-2">✅ Después</h4>
                  {newMetrics && newMetrics.estadisticas && (
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span>Filas con nulos</span>
                        <span className="font-mono text-green-700">{newMetrics.valores_nulos ?? 0}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Varianza (promedio)</span>
                        <span className="font-mono">
                          {Object.values(newMetrics.estadisticas.varianza).reduce((a, b) => a + b, 0) / Object.keys(newMetrics.estadisticas.varianza).length}
                        </span>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Download */}
              <div className="mt-6 flex flex-col sm:flex-row gap-4 justify-center">
                <button
                  onClick={downloadCSV}
                  className="flex-1 sm:flex-none bg-blue-600 hover:bg-blue-700 text-white py-3 px-6 rounded-lg font-semibold transition-colors"
                >
                  📥 Descargar CSV Imputado
                </button>
                <button
                  onClick={reset}
                  className="flex-1 sm:flex-none bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-800 dark:text-gray-200 py-3 px-6 rounded-lg font-semibold transition-colors"
                >
                  🔄 Nuevo Análisis
                </button>
              </div>
            </div>

            {/* Imputed Preview */}
            {imputedData && imputedData.length > 0 && (
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border dark:border-gray-700 overflow-hidden">
                <div className="p-4 border-b dark:border-gray-700">
                  <h3 className="font-semibold text-gray-900 dark:text-white">👁️ Vista Previa Datos Imputados</h3>
                </div>
                <div className="overflow-x-auto p-4 max-h-64">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="text-left text-gray-500 dark:text-gray-400 border-b dark:border-gray-700">
                        {columns.map((col) => (
                          <th key={col} className="p-2 font-mono">{col}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {imputedData.slice(0, 10).map((row, i) => (
                        <tr key={i} className="border-b dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700/50">
                          {columns.map((col) => (
                            <td key={col} className="p-2 text-gray-700 dark:text-gray-300">
                              {row[col] === null || row[col] === undefined ? (
                                <span className="text-red-500 italic">NULL</span>
                              ) : (
                                String(row[col])
                              )}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Empty state */}
        {!file && step === "upload" && (
          <div className="text-center py-16 text-gray-500 dark:text-gray-400">
            <div className="text-6xl mb-4">📊</div>
            <h3 className="text-xl font-medium mb-2">Listo para analizar tus datos</h3>
            <p>Sube un archivo CSV o Excel para comenzar</p>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white dark:bg-gray-800 border-t dark:border-gray-700 mt-12">
        <div className="max-w-6xl mx-auto px-4 py-4 text-center text-sm text-gray-500 dark:text-gray-400">
          Powered by Next.js + Vercel Python Functions + scikit-learn
        </div>
      </footer>
    </div>
  );
}

function StatCard({ label, value, icon, color = "blue" }: { label: string; value: string | number; icon: string; color?: "blue" | "red" | "yellow" | "green" }) {
  const colors = {
    blue: "bg-blue-50 dark:bg-blue-900/30 border-blue-200 dark:border-blue-800 text-blue-700 dark:text-blue-300",
    red: "bg-red-50 dark:bg-red-900/30 border-red-200 dark:border-red-800 text-red-700 dark:text-red-300",
    yellow: "bg-yellow-50 dark:bg-yellow-900/30 border-yellow-200 dark:border-yellow-800 text-yellow-700 dark:text-yellow-300",
    green: "bg-green-50 dark:bg-green-900/30 border-green-200 dark:border-green-800 text-green-700 dark:text-green-300",
  };

  return (
    <div className={`p-4 rounded-xl border ${colors[color]}`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600 dark:text-gray-400">{label}</p>
          <p className="text-2xl font-bold mt-1">{value}</p>
        </div>
        <span className="text-3xl">{icon}</span>
      </div>
    </div>
  );
}