import os
import time
import random
from typing import Optional, List, Dict

try:
    from google import genai
    from google.genai import types
    GENAI_CLIENT_AVAILABLE = True
except ImportError:
    GENAI_CLIENT_AVAILABLE = False
    import google.generativeai as legacy_genai

# Cache de clientes
_CLIENT_CACHE = {}

def get_genai_client(api_key: str):
    """Obtiene o crea una instancia reutilizable del cliente Gemini."""
    if api_key not in _CLIENT_CACHE:
        if GENAI_CLIENT_AVAILABLE:
            _CLIENT_CACHE[api_key] = genai.Client(api_key=api_key)
        else:
            legacy_genai.configure(api_key=api_key)
            _CLIENT_CACHE[api_key] = True
    return _CLIENT_CACHE[api_key]

DEFAULT_SYSTEM_INSTRUCTION = """Eres un traductor académico experto especializado en traducir artículos científicos y técnicos (papers) del inglés al español.

Pautas críticas para la traducción:
1. Precisión y rigor científico: Emplea un lenguaje académico, formal, fluido y natural en español.
2. Términos técnicos: Utiliza la terminología científica estándar en español. Si un término en inglés es el estándar de la industria/área (o no tiene traducción directa), consérvalo o colócalo entre paréntesis si ayuda a la claridad.
3. Citas y referencias: Conserva intactas las citas bibliográficas como [1], [1, 2], [1-3], (Smith et al., 2021), etc.
4. Ecuaciones y LaTeX: No alteres fórmulas matemáticas, variables o código LaTeX (ej. $E=mc^2$, \\begin{equation}...\\end{equation}).
5. Estructura y formato: Mantén la estructura de párrafos, encabezados, listas y puntuación.
6. Salida limpia: Devuelve ÚNICAMENTE la traducción en español, sin preámbulos, notas del traductor ni comentarios adicionales.
"""

# Modelos ordenados por velocidad y baja saturación (Gemini 3.x)
FALLBACK_MODELS = [
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-3.8-flash",
    "gemini-3.7-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash"
]

def translate_chunk_gemini(
    chunk_text: str,
    api_key: str,
    model_name: str = "gemini-3.5-flash-lite",
    domain: str = "General Académico",
    custom_glossary: Optional[str] = None,
    temperature: float = 0.2,
    max_retries: int = 4
) -> str:
    """
    Traduce un bloque de texto académico usando Gemini con reintentos inteligentes
    y respaldo automático ante sobrecarga (503 / 429).
    """
    if not chunk_text.strip():
        return ""

    context_prompt = f"Área de especialidad / Dominio: {domain}\n"
    if custom_glossary and custom_glossary.strip():
        context_prompt += f"Glosario / Instrucciones específicas:\n{custom_glossary.strip()}\n\n"

    user_prompt = f"""{context_prompt}Traduce el siguiente fragmento de un paper del inglés al español respetando las pautas académicas:

--- INICIO DEL TEXTO EN INGLÉS ---
{chunk_text}
--- FIN DEL TEXTO EN INGLÉS ---

Traducción al español:"""

    client = get_genai_client(api_key)

    # Lista de modelos a intentar: el seleccionado primero, luego los de respaldo
    models_to_try = [model_name] + [m for m in FALLBACK_MODELS if m != model_name]

    last_exception = None

    for current_model in models_to_try:
        for attempt in range(max_retries):
            try:
                if GENAI_CLIENT_AVAILABLE:
                    response = client.models.generate_content(
                        model=current_model,
                        contents=user_prompt,
                        config=types.GenerateContentConfig(
                            system_instruction=DEFAULT_SYSTEM_INSTRUCTION,
                            temperature=temperature,
                        )
                    )
                    if response and response.text:
                        return response.text.strip()
                    raise ValueError("Respuesta vacía del modelo.")
                else:
                    model = legacy_genai.GenerativeModel(
                        model_name=current_model,
                        system_instruction=DEFAULT_SYSTEM_INSTRUCTION,
                        generation_config={"temperature": temperature}
                    )
                    response = model.generate_content(user_prompt)
                    if response and response.text:
                        return response.text.strip()
                    raise ValueError("Respuesta vacía del modelo.")

            except Exception as e:
                err_msg = str(e).lower()
                last_exception = e
                
                # Si es error 503 (Unavailable) o 429 (Rate limit)
                is_overload = "503" in err_msg or "unavailable" in err_msg or "high demand" in err_msg or "429" in err_msg or "quota" in err_msg
                
                if is_overload:
                    # Espera con backoff exponencial y jitter aleatorio
                    wait_time = (1.5 ** attempt) + random.uniform(0.5, 1.5)
                    time.sleep(wait_time)
                    # Si ya reintentó varias veces en este modelo, pasar al siguiente modelo de respaldo
                    if attempt >= 2:
                        break
                elif "404" in err_msg or "not_found" in err_msg:
                    # Modelo no encontrado, pasar directamente al respaldo
                    break
                else:
                    if attempt < max_retries - 1:
                        time.sleep(1.0 + random.uniform(0.2, 0.8))
                    else:
                        break

    raise RuntimeError(f"Error al traducir el bloque tras intentar modelos alternativos: {str(last_exception)}")
