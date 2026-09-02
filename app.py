import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import streamlit as st
from dotenv import load_dotenv

from utils.extractor import extract_text_from_file
from utils.chunker import split_text_into_chunks
from utils.translator import translate_chunk_gemini
from utils.exporter import export_to_pdf, export_to_docx, export_to_markdown, export_to_txt, create_zip_of_pdfs
from utils.i18n import t, DOMAIN_MAPPING
from utils.theme import get_theme_css

# Cargar variables de entorno si existen
load_dotenv()

# Inicialización de estado en sesión
if "documents" not in st.session_state:
    st.session_state.documents = {}

if "language" not in st.session_state:
    st.session_state.language = "es"

if "theme" not in st.session_state:
    st.session_state.theme = "dark"

# Configuración de página
st.set_page_config(
    page_title="Academic Paper Multi-Translator | Gemini",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------- BARRA LATERAL (CONFIGURACIÓN) -----------------
with st.sidebar:
    # Selector de Idioma y Tema en la parte superior
    col_lang, col_theme = st.columns(2)
    
    with col_lang:
        lang_idx = 0 if st.session_state.language == "es" else 1
        selected_lang_label = st.selectbox(
            "🌐 Idioma / Language",
            options=["🇪🇸 Español", "🇺🇸 English"],
            index=lang_idx,
            label_visibility="collapsed"
        )
        st.session_state.language = "es" if "Español" in selected_lang_label else "en"

    with col_theme:
        theme_idx = 0 if st.session_state.theme == "dark" else 1
        theme_options = [
            t("theme_dark", st.session_state.language),
            t("theme_light", st.session_state.language)
        ]
        selected_theme_label = st.selectbox(
            "🎨 Tema / Theme",
            options=theme_options,
            index=theme_idx,
            label_visibility="collapsed"
        )
        st.session_state.theme = "dark" if ("Oscuro" in selected_theme_label or "Dark" in selected_theme_label) else "light"

    lang = st.session_state.language
    current_theme = st.session_state.theme

    st.title(t("sidebar_title", lang))
    
    env_api_key = os.getenv("GEMINI_API_KEY", "")
    api_key = st.text_input(
        t("api_key_label", lang),
        value=env_api_key,
        type="password",
        help=t("api_key_help", lang)
    )
    
    model_preset = st.selectbox(
        t("model_label", lang),
        options=[
            "gemini-3.5-flash-lite (Flash-Lite: Mínima Latencia y Rápido)" if lang == "es" else "gemini-3.5-flash-lite (Flash-Lite: Lowest Latency & Fast)",
            "gemini-3.1-flash-lite (Flash-Lite: Ultra Ligero)" if lang == "es" else "gemini-3.1-flash-lite (Flash-Lite: Ultra Lightweight)",
            "gemini-3.8-flash (Flash: Última Versión)" if lang == "es" else "gemini-3.8-flash (Flash: Latest Version)",
            "gemini-3.7-flash (Flash: Alto Rendimiento)" if lang == "es" else "gemini-3.7-flash (Flash: High Performance)",
            "gemini-3.6-flash (Flash)",
            "gemini-3.5-flash (Flash)",
            "Otro (Escribir ID personalizado)" if lang == "es" else "Other (Enter custom ID)"
        ],
        index=0,
        help=t("model_help", lang)
    )
    
    if "Otro" in model_preset or "Other" in model_preset:
        model_choice = st.text_input(t("custom_model_label", lang), value="gemini-3.5-flash-lite")
    else:
        model_choice = model_preset.split(" ")[0]

    domain_options = t("domains", lang)
    academic_domain = st.selectbox(
        t("domain_label", lang),
        options=domain_options,
        index=0
    )
    # Convertir a texto estándar en español para el prompt
    domain_for_prompt = DOMAIN_MAPPING.get(academic_domain, academic_domain)

    st.markdown(f"### {t('speed_section', lang)}")
    
    concurrency = st.slider(
        t("concurrency_label", lang),
        min_value=1,
        max_value=10,
        value=5,
        help=t("concurrency_help", lang)
    )
    
    chunk_size = st.slider(
        t("chunk_size_label", lang),
        min_value=500,
        max_value=3000,
        value=1500,
        step=250,
        help=t("chunk_size_help", lang)
    )

    with st.expander(t("advanced_options", lang)):
        temperature = st.slider(t("temperature_label", lang), min_value=0.0, max_value=1.0, value=0.2, step=0.05)
        custom_glossary = st.text_area(
            t("glossary_label", lang),
            placeholder=t("glossary_placeholder", lang),
            height=100
        )

# Inyección de estilos de modo oscuro / claro
st.markdown(get_theme_css(current_theme), unsafe_allow_html=True)

# ----------------- ENCABEZADO -----------------
st.title(t("main_title", lang))
st.caption(f"⚡ {t('main_subtitle', lang)}")
st.markdown(t("main_desc", lang))

# ----------------- CARGA DE MÚLTIPLES ARCHIVOS -----------------
uploaded_files = st.file_uploader(
    t("upload_label", lang),
    type=["pdf", "docx", "txt", "md", "tex"],
    accept_multiple_files=True
)

col_act1, col_act2 = st.columns([2, 1])

with col_act1:
    if uploaded_files:
        if st.button(t("btn_load_chunk", lang), type="primary", use_container_width=True):
            with st.spinner(t("spinner_extracting", lang)):
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
                            st.warning(t("empty_file_warn", lang, filename=file.name))
                    except Exception as e:
                        st.error(t("file_error", lang, filename=file.name, error=str(e)))
            st.success(t("files_loaded_success", lang, count=len(st.session_state.documents)))
            st.rerun()

with col_act2:
    if st.session_state.documents:
        if st.button(t("btn_clear_all", lang), use_container_width=True):
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
    col_m1.metric(t("metric_docs", lang), total_docs)
    col_m2.metric(t("metric_docs_translated", lang), f"{completed_docs} / {total_docs}")
    col_m3.metric(t("metric_total_chunks", lang), total_all_chunks)
    col_m4.metric(t("metric_chunks_translated", lang), f"{translated_all_chunks} / {total_all_chunks}")

    st.write("")
    col_btn_start, col_btn_zip = st.columns([2, 1])

    with col_btn_start:
        start_batch = st.button(t("btn_start_translation", lang), type="primary", use_container_width=True)

    # ----------------- LÓGICA CONCURRENTE / PARALELA -----------------
    if start_batch:
        if not api_key:
            st.error(t("warn_no_api_key", lang))
        else:
            # Recolectar todos los bloques pendientes
            pending_tasks = []
            for doc_name, doc_data in st.session_state.documents.items():
                for chunk in doc_data["chunks"]:
                    if chunk["id"] not in doc_data["translations"]:
                        pending_tasks.append((doc_name, chunk))

            if not pending_tasks:
                st.info(t("info_all_done", lang))
            else:
                progress_bar = st.progress(translated_all_chunks / total_all_chunks if total_all_chunks > 0 else 0)
                status_placeholder = st.empty()
                status_placeholder.info(
                    t("status_processing", lang, count=len(pending_tasks), threads=concurrency)
                )

                def worker_translate(doc_name, chunk_obj):
                    res = translate_chunk_gemini(
                        chunk_text=chunk_obj["text"],
                        api_key=api_key,
                        model_name=model_choice,
                        domain=domain_for_prompt,
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
                                t(
                                    "status_chunk_done",
                                    lang,
                                    cid=c_id,
                                    name=d_name,
                                    done=completed_count,
                                    total=total_all_chunks,
                                    elapsed=elapsed
                                )
                            )
                        except Exception as e:
                            st.session_state.documents[d_name]["status"] = "error"
                            st.session_state.documents[d_name]["error"] = str(e)
                            status_placeholder.error(
                                t("status_chunk_error", lang, name=d_name, cid=c_id, error=str(e))
                            )

                # Marcar documentos completos
                for doc_name, doc_data in st.session_state.documents.items():
                    if len(doc_data["translations"]) == len(doc_data["chunks"]):
                        doc_data["status"] = "completed"

                total_time = round(time.time() - start_time, 1)
                status_placeholder.success(t("status_success", lang, total_time=total_time))
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
                label=t("btn_download_all_zip", lang, count=len(ready_pdfs)),
                data=zip_data,
                file_name="papers_traducidos_es.zip",
                mime="application/zip",
                use_container_width=True
            )

    # ----------------- DETALLE Y DESCARGA POR DOCUMENTO -----------------
    st.divider()
    st.subheader(t("section_docs", lang))

    for doc_name, doc_data in st.session_state.documents.items():
        n_chunks = len(doc_data["chunks"])
        n_trans = len(doc_data["translations"])
        is_fully_done = (n_trans == n_chunks and n_chunks > 0)
        
        if is_fully_done:
            status_label = t("status_done", lang)
        elif n_trans > 0:
            status_label = t("status_in_progress", lang, done=n_trans, total=n_chunks)
        else:
            status_label = t("status_pending", lang)
        
        with st.expander(f"📄 {doc_name} — {status_label} ({doc_data['word_count']} {t('words_count', lang)})", expanded=not is_fully_done):
            
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
                        label=t("btn_dl_pdf", lang),
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
                        label=t("btn_dl_docx", lang),
                        data=docx_buf,
                        file_name=f"{doc_data['base_name']}_es.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        key=f"docx_dl_{doc_name}",
                        use_container_width=True
                    )
                
                # 3. Markdown
                with col_d3:
                    st.download_button(
                        label=t("btn_dl_md", lang),
                        data=export_to_markdown(full_doc_translated),
                        file_name=f"{doc_data['base_name']}_es.md",
                        mime="text/markdown",
                        key=f"md_dl_{doc_name}",
                        use_container_width=True
                    )
            else:
                st.info(t("ready_to_translate", lang))

            # Vista de bloques (Original vs Traducción)
            st.write(f"#### {t('block_comparison', lang)}")
            for chunk in doc_data["chunks"]:
                cid = chunk["id"]
                c_done = cid in doc_data["translations"]
                c_icon = "✅" if c_done else "⏳"
                block_title_str = t("block_title", lang, cid=cid, words=chunk['word_count'])
                
                with st.expander(f"{c_icon} {block_title_str}", expanded=False):
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown(f"**{t('label_original', lang)}**")
                        st.text_area(f"orig_{doc_name}_{cid}", value=chunk["text"], height=160, disabled=True, label_visibility="collapsed")
                    with c2:
                        st.markdown(f"**{t('label_translation', lang)}**")
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
                            st.info(t("block_pending_info", lang))
