# 📚 Traductor Masivo de Papers Científicos con Streamlit & Gemini (Inglés ➔ Español)

Aplicación web desarrollada en **Streamlit** diseñada para procesar y traducir **múltiples artículos científicos y papers de forma simultánea** del **inglés al español** mediante **segmentación por bloques lógicos** y la API de **Google Gemini**. Genera como resultado final **documentos PDF traducidos y formateados con estilo académico**.

---

## 🌟 Características Principales

- **Carga Masiva de Archivos**: Sube múltiples papers a la vez en formatos `.pdf`, `.docx`, `.txt`, `.md` o `.tex` (LaTeX).
- **Traducción en Bloques (`Chunking`)**: Segmenta cada paper por párrafos y secciones para no perder coherencia ni exceder límites de tokens.
- **Salida Directa en PDF**:
  - Generación de **PDFs traducidos al español** con tipografía, márgenes y títulos académicos con `ReportLab`.
  - Botón para descargar **todos los PDFs traducidos en un único archivo ZIP (.zip)**.
  - Descargas individuales por archivo en **PDF (.pdf)**, **Word (.docx)** y **Markdown (.md)**.
- **Prompt Académico Especializado**:
  - Preserva citas bibliográficas (`[1]`, `(Smith et al., 2021)`).
  - Preserva fórmulas y código LaTeX (`$E=mc^2$`).
  - Adaptación por disciplina científica (IA/Computación, Medicina, Física, Ingeniería, etc.) y glosario personalizado.
- **Cola de Procesamiento en Lote**:
  - Barra de progreso global con indicador de archivo y bloque en tiempo real.
  - Control de pausas y reintentos para respetar límites de cuota (rate limits de Gemini).
- **Vista Comparativa y Edición**: Revisa y ajusta el texto traducido bloque por bloque antes de exportar.

---

## 🚀 Instalación y Puesta en Marcha

### 1. Activar tu entorno virtual
```bash
cd /home/lenzhit/unt/proyecto-investigacion
python3 -m venv venv
source venv/bin/activate
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Configurar tu API Key de Gemini
Obtén tu clave gratuita en [Google AI Studio](https://aistudio.google.com/). Puedes:
- Ingresarla directamente en la barra lateral de la app.
- O guardarla en un archivo `.env`:
  ```bash
  cp .env.example .env
  # Edita .env y coloca tu GEMINI_API_KEY
  ```

### 4. Ejecutar la aplicación
```bash
streamlit run app.py
```
