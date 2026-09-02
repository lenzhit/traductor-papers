import re
from typing import List, Dict

def split_text_into_chunks(text: str, max_words_per_chunk: int = 1000) -> List[Dict[str, any]]:
    """
    Divide un texto largo en bloques lógicos (párrafos y oraciones)
    respetando el límite aproximado de palabras por bloque.
    """
    if not text.strip():
        return []

    # Dividir por párrafos principales
    raw_paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    
    chunks = []
    current_chunk = []
    current_word_count = 0

    for paragraph in raw_paragraphs:
        p_words = len(paragraph.split())
        
        # Si el párrafo por sí solo supera el tamaño máximo, dividirlo por oraciones
        if p_words > max_words_per_chunk:
            sentences = re.split(r'(?<=[.!?])\s+', paragraph)
            for sentence in sentences:
                s_words = len(sentence.split())
                if current_word_count + s_words > max_words_per_chunk and current_chunk:
                    chunk_text = "\n\n".join(current_chunk)
                    chunks.append({
                        "id": len(chunks) + 1,
                        "text": chunk_text,
                        "word_count": len(chunk_text.split())
                    })
                    current_chunk = []
                    current_word_count = 0
                
                current_chunk.append(sentence)
                current_word_count += s_words
        else:
            if current_word_count + p_words > max_words_per_chunk and current_chunk:
                chunk_text = "\n\n".join(current_chunk)
                chunks.append({
                    "id": len(chunks) + 1,
                    "text": chunk_text,
                    "word_count": len(chunk_text.split())
                })
                current_chunk = []
                current_word_count = 0

            current_chunk.append(paragraph)
            current_word_count += p_words

    # Agregar el remanente
    if current_chunk:
        chunk_text = "\n\n".join(current_chunk)
        chunks.append({
            "id": len(chunks) + 1,
            "text": chunk_text,
            "word_count": len(chunk_text.split())
        })

    return chunks
