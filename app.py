import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import streamlit as st
from dotenv import load_dotenv

from utils.extractor import extract_text_from_file
from utils.chunker import split_text_into_chunks
from utils.translator import translate_chunk_gemini
from utils.exporter import export_to_pdf, export_to_docx, export_to_markdown, export_to_txt, create_zip_of_pdfs

# Cargar variables de entorno si existen
load_dotenv()

st.set_page_config(
    page_title="Academic Paper Multi-Translator | Gemini",
    page_icon="⚡",
    layout="wide"
)

# Inicialización de estado en sesión
if "documents" not in st.session_state:
    st.session_state.documents = {}

# ----------------- BARRA LATERAL (CONFIGURACIÓN) -----------------
with st.sidebar:
    st.title("⚙️ Configuración")
    
    env_api_key = os.getenv("GEMINI_API_KEY", "")
    api_key = st.text_input(
        "Gemini API Key:",
        value=env_api_key,
        type="password",
        help="Obtén tu clave en Google AI Studio (aistudio.google.com)"
    )
    
    model_preset = st.selectbox(
        "Modelo de Gemini:",
        options=[
            "gemini-3.5-flash-lite (Flash-Lite: Mínima Latencia y Rápido)",
            "gemini-3.1-flash-lite (Flash-Lite: Ultra Ligero)",
            "gemini-3.8-flash (Flash: Última Versión)",
            "gemini-3.7-flash (Flash: Alto Rendimiento)",
            "gemini-3.6-flash (Flash)",
            "gemini-3.5-flash (Flash)",
            "Otro (Escribir ID personalizado)"
        ],
        index=0,
        help="Modelos activos en Google AI Studio. Los modelos Flash-Lite son los más veloces y con menor saturación."
    )
    
    if "Otro" in model_preset:
        model_choice = st.text_input("ID del modelo personalizado:", value="gemini-3.5-flash-lite")
    else:
        model_choice = model_preset.split(" ")[0]

    academic_domain = st.selectbox(
        "Área Científica / Dominio:",
        options=[
            "General Académico",
            "Ciencias de la Computación e IA",
            "Medicina y Ciencias de la Salud",
            "Ingeniería y Tecnología",
            "Física y Matemáticas",
            "Biología y Biotecnología",
            "Economía y Negocios",
            "Ciencias Sociales y Humanidades"
        ],
        index=0
    )

    st.markdown("### ⚡ Optimización de Velocidad")
    
    concurrency = st.slider(
        "Procesamiento en Paralelo (Hilos concurrentes):",
        min_value=1,
        max_value=10,
        value=5,
        help="Traduce múltiples bloques a la vez. 4 a 6 hilos acelera el proceso hasta 5x."
    )
    
    chunk_size = st.slider(
        "Tamaño de Bloque (palabras):",
        min_value=500,
        max_value=3000,
        value=1500,
        step=250,
        help="Bloques más grandes (1500-2000 palabras) reducen el número de llamadas a la API y aceleran la traducción."
    )

    with st.expander("🛠️ Opciones Avanzadas"):
        temperature = st.slider("Temperatura:", min_value=0.0, max_value=1.0, value=0.2, step=0.05)
        custom_glossary = st.text_area(
            "Glosario o instrucciones especiales:",
            placeholder="Ejemplo:\n- 'fine-tuning' -> 'ajuste fino'\n- 'transformer' -> mantener 'transformer'",
            height=100
        )

# ----------------- ENCABEZADO -----------------
st.title("📚 Traductor Masivo Ultra-Rápido de Papers (Inglés ➔ Español)")
st.markdown(
    "Sube **múltiples papers en paralelo**, procesados en **bloques concurrentes** con **Google Gemini Flash** "
    "y descarga los resultados como **PDFs formateados al español**."
)

# ----------------- CARGA DE MÚLTIPLES ARCHIVOS -----------------
uploaded_files = st.file_uploader(
    "Selecciona uno o varios papers (PDF, DOCX, TXT, MD, LaTeX):",
    type=["pdf", "docx", "txt", "md", "tex"],
    accept_multiple_files=True
)

col_act1, col_act2 = st.columns([2, 1])

with col_act1:
    if uploaded_files:
        if st.button("📂 Cargar y Segmentar Archivos", type="primary", use_container_width=True):
            with st.spinner("Extrayendo y segmentando documentos..."):
                for file in uploaded_files:
                    base_name = file.name.rsplit('.', 1)[0]
                    try:
                        extracted = extract_text_from_file(file, file.name)
                        if extracted.strip():
                            chunks = split_text_into_chunks(extracted, max_words_per_chunk=chunk_size)
                            st.session_state.documents[file.name] = {
                                "base_name": base_name,
                                "raw_text": extracted,
                                "word_count": len(extracted.split()),
                                "chunks": chunks,
                                "translations": {},
                                "status": "pending",
                                "error": None
                            }
                        else:
                            st.warning(f"El archivo '{file.name}' está vacío o no contiene texto extraíble.")
                    except Exception as e:
                        st.error(f"Error procesando '{file.name}': {str(e)}")
            st.success(f"Se han cargado {len(st.session_state.documents)} documento(s) correctamente.")
            st.rerun()

with col_act2:
    if st.session_state.documents:
        if st.button("🗑️ Limpiar Todo", use_container_width=True):
            st.session_state.documents = {}
            st.rerun()

# ----------------- PANEL DE CONTROL Y TRADUCCIÓN PARALELA -----------------
if st.session_state.documents:
    st.divider()
    
    total_docs = len(st.session_state.documents)
    completed_docs = sum(1 for d in st.session_state.documents.values() if d["status"] == "completed")
    total_all_chunks = sum(len(d["chunks"]) for d in st.session_state.documents.values())
    translated_all_chunks = sum(len(d["translations"]) for d in st.session_state.documents.values())
    
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.metric("Documentos", total_docs)
    col_m2.metric("Documentos traducidos", f"{completed_docs} / {total_docs}")
    col_m3.metric("Bloques totales", total_all_chunks)
    col_m4.metric("Bloques traducidos", f"{translated_all_chunks} / {total_all_chunks}")

    st.write("")
    col_btn_start, col_btn_zip = st.columns([2, 1])

    with col_btn_start:
        start_batch = st.button("⚡ Iniciar Traducción Ultra-Rápida en Paralelo", type="primary", use_container_width=True)

    # ----------------- LÓGICA CONCURRENTE / PARALELA -----------------
    if start_batch:
        if not api_key:
            st.error("⚠️ Por favor ingresa tu Gemini API Key en la barra lateral antes de traducir.")
        else:
            # Recolectar todos los bloques pendientes
            pending_tasks = []
            for doc_name, doc_data in st.session_state.documents.items():
                for chunk in doc_data["chunks"]:
                    if chunk["id"] not in doc_data["translations"]:
                        pending_tasks.append((doc_name, chunk))

            if not pending_tasks:
                st.info("Todos los bloques ya han sido traducidos.")
            else:
                progress_bar = st.progress(translated_all_chunks / total_all_chunks if total_all_chunks > 0 else 0)
                status_placeholder = st.empty()
                status_placeholder.info(f"🚀 Procesando {len(pending_tasks)} bloques en paralelo usando {concurrency} hilos...")

                def worker_translate(doc_name, chunk_obj):
                    res = translate_chunk_gemini(
                        chunk_text=chunk_obj["text"],
                        api_key=api_key,
                        model_name=model_choice,
                        domain=academic_domain,
                        custom_glossary=custom_glossary,
                        temperature=temperature
                    )
                    return doc_name, chunk_obj["id"], res

                completed_count = translated_all_chunks
                start_time = time.time()

                with ThreadPoolExecutor(max_workers=concurrency) as executor:
                    futures = {
                        executor.submit(worker_translate, d_name, c_obj): (d_name, c_obj["id"])
                        for d_name, c_obj in pending_tasks
                    }

                    for future in as_completed(futures):
                        d_name, c_id = futures[future]
                        try:
                            _, _, trans_text = future.result()
                            st.session_state.documents[d_name]["translations"][c_id] = trans_text
                            completed_count += 1
                            progress_bar.progress(completed_count / total_all_chunks)
                            
                            elapsed = round(time.time() - start_time, 1)
                            status_placeholder.info(
                                f"⚡ Traducido Bloque {c_id} de '{d_name}' | Progreso: {completed_count}/{total_all_chunks} bloques ({elapsed}s transcurridos)"
                            )
                        except Exception as e:
                            st.session_state.documents[d_name]["status"] = "error"
                            st.session_state.documents[d_name]["error"] = str(e)
                            status_placeholder.error(f"❌ Error en '{d_name}' (Bloque {c_id}): {str(e)}")

                # Marcar documentos completos
                for doc_name, doc_data in st.session_state.documents.items():
                    if len(doc_data["translations"]) == len(doc_data["chunks"]):
                        doc_data["status"] = "completed"

                total_time = round(time.time() - start_time, 1)
                status_placeholder.success(f"🎉 ¡Traducción masiva completada en solo {total_time} segundos!")
                time.sleep(1)
                st.rerun()

    # ----------------- DESCARGA MASIVA (ZIP DE PDFs) -----------------
    with col_btn_zip:
        ready_pdfs = []
        for doc_name, doc_data in st.session_state.documents.items():
            if doc_data["translations"]:
                ordered_blocks = [
                    doc_data["translations"].get(c["id"], f"[Bloque {c['id']} pendiente]")
                    for c in doc_data["chunks"]
                ]
                full_text = "\n\n".join(ordered_blocks)
                pdf_bytes = export_to_pdf(full_text, doc_data["base_name"]).getvalue()
                ready_pdfs.append((f"{doc_data['base_name']}_es.pdf", pdf_bytes))

        if ready_pdfs:
            zip_data = create_zip_of_pdfs(ready_pdfs)
            st.download_button(
                label=f"📦 Descargar Todos los PDFs (.ZIP) [{len(ready_pdfs)}]",
                data=zip_data,
                file_name="papers_traducidos_es.zip",
                mime="application/zip",
                use_container_width=True
            )

    # ----------------- DETALLE Y DESCARGA POR DOCUMENTO -----------------
    st.divider()
    st.subheader("📑 Documentos y Descargas de PDFs")

    for doc_name, doc_data in st.session_state.documents.items():
        n_chunks = len(doc_data["chunks"])
        n_trans = len(doc_data["translations"])
        is_fully_done = (n_trans == n_chunks and n_chunks > 0)
        
        status_label = "✅ Traducido" if is_fully_done else (f"⏳ {n_trans}/{n_chunks} bloques" if n_trans > 0 else "⚪ En espera")
        
        with st.expander(f"📄 {doc_name} — {status_label} ({doc_data['word_count']} palabras)", expanded=not is_fully_done):
            
            if doc_data["translations"]:
                ordered_blocks = [
                    doc_data["translations"].get(c["id"], f"[Bloque {c['id']} pendiente]")
                    for c in doc_data["chunks"]
                ]
                full_doc_translated = "\n\n".join(ordered_blocks)

                col_d1, col_d2, col_d3 = st.columns(3)
                
                # 1. PDF
                with col_d1:
                    pdf_buf = export_to_pdf(full_doc_translated, doc_data["base_name"])
                    st.download_button(
                        label="📥 Descargar PDF (.pdf)",
                        data=pdf_buf,
                        file_name=f"{doc_data['base_name']}_es.pdf",
                        mime="application/pdf",
                        key=f"pdf_dl_{doc_name}",
                        use_container_width=True
                    )
                
                # 2. Word DOCX
                with col_d2:
                    docx_buf = export_to_docx(full_doc_translated, doc_data["base_name"])
                    st.download_button(
                        label="📄 Descargar Word (.docx)",
                        data=docx_buf,
                        file_name=f"{doc_data['base_name']}_es.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        key=f"docx_dl_{doc_name}",
                        use_container_width=True
                    )
                
                # 3. Markdown
                with col_d3:
                    st.download_button(
                        label="📝 Descargar Markdown (.md)",
                        data=export_to_markdown(full_doc_translated),
                        file_name=f"{doc_data['base_name']}_es.md",
                        mime="text/markdown",
                        key=f"md_dl_{doc_name}",
                        use_container_width=True
                    )
            else:
                st.info("Documento listo para ser traducido.")

            # Vista de bloques (Original vs Traducción)
            st.write("#### Comparación Bloque por Bloque")
            for chunk in doc_data["chunks"]:
                cid = chunk["id"]
                c_done = cid in doc_data["translations"]
                c_icon = "✅" if c_done else "⏳"
                
                with st.expander(f"{c_icon} Bloque {cid} ({chunk['word_count']} palabras)", expanded=False):
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown("**Original (Inglés):**")
                        st.text_area(f"orig_{doc_name}_{cid}", value=chunk["text"], height=160, disabled=True, label_visibility="collapsed")
                    with c2:
                        st.markdown("**Traducción (Español):**")
                        if c_done:
                            edited = st.text_area(
                                f"trans_{doc_name}_{cid}",
                                value=doc_data["translations"][cid],
                                height=160,
                                key=f"area_{doc_name}_{cid}",
                                label_visibility="collapsed"
                            )
                            doc_data["translations"][cid] = edited
                        else:
                            st.info("Bloque pendiente de traducción.")
