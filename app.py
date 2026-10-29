import os
import io
import html
import numpy as np
import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI

try:
    from PyPDF2 import PdfReader
except ImportError:
    from pypdf import PdfReader

# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================
st.set_page_config(
    page_title="Chat PDF // Krov Industries",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inicialización de estado
if "turns" not in st.session_state:
    st.session_state.turns = []  # Lista de dicts: {"user": ..., "assistant": ...}
if "pdf_id" not in st.session_state:
    st.session_state.pdf_id = None
if "pdf_chunks" not in st.session_state:
    st.session_state.pdf_chunks = []
if "pdf_embeddings" not in st.session_state:
    st.session_state.pdf_embeddings = None
if "pdf_name" not in st.session_state:
    st.session_state.pdf_name = ""

# ============================================================
# ESTILOS: CABECERA FIJA Y DESPLAZAMIENTO FLUIDO EN BLOQUE
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600;700&display=swap');

html, body, [data-testid="stAppViewContainer"], .stApp, section.main, .block-container {
    background: transparent !important;
    background-color: transparent !important;
    color: #f1f5f9 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

body {
    background-color: #04090e !important;
}

[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stSidebar"], section[data-testid="stSidebar"] { display: none !important; }

.brand-signature {
    text-align: center;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.18em;
    color: #00ff88;
    text-transform: uppercase;
}

.main-title {
    font-size: 2.1rem;
    font-weight: 700;
    text-align: center;
    color: #ffffff;
    margin-bottom: 0.2rem;
    text-shadow: 0 0 25px rgba(0, 255, 136, 0.35);
}

.sub-lead {
    text-align: center;
    color: #94a3b8;
    font-size: 0.92rem;
    margin-bottom: 1.5rem;
}

.block-container {
    max-width: 1250px !important;
    padding-top: 1.5rem !important;
    padding-bottom: 3rem !important;
}

/* Tarjeta informativa en panel izquierdo */
.meta-card {
    background: rgba(6, 16, 24, 0.9);
    border: 1px solid rgba(0, 255, 136, 0.25);
    border-radius: 8px;
    padding: 16px;
    margin-top: 12px;
    font-size: 0.88rem;
    line-height: 1.6;
}

/* -----------------------------------------------------------
   CAMPO DE ENTRADA FIJO EN LA PARTE SUPERIOR (STICKY)
----------------------------------------------------------- */
.sticky-input-anchor {
    position: -webkit-sticky !important;
    position: sticky !important;
    top: 0 !important;
    z-index: 999 !important;
    background: #04090e !important;
    background-color: #04090e !important;
    padding-top: 6px !important;
    padding-bottom: 12px !important;
    border-bottom: 1px solid rgba(0, 255, 136, 0.22) !important;
    margin-bottom: 16px !important;
    box-shadow: 0 12px 30px rgba(4, 9, 14, 0.98) !important;
}

div[data-testid="stForm"] {
    border: 1px solid rgba(0, 255, 136, 0.3) !important;
    background: rgba(6, 18, 28, 0.92) !important;
    border-radius: 8px !important;
    padding: 10px 14px 8px 14px !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.6) !important;
}

div[data-testid="stForm"]:focus-within {
    border-color: #00ff88 !important;
    box-shadow: 0 0 20px rgba(0, 255, 136, 0.25) !important;
}

div.stButton > button[kind="primary"], div[data-testid="stFormSubmitButton"] > button {
    border-radius: 6px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.85rem !important;
    background: linear-gradient(135deg, #00ff88 0%, #0ea5e9 100%) !important;
    color: #04090e !important;
    font-weight: 700 !important;
    border: none !important;
    padding: 0.65rem 1.2rem !important;
    box-shadow: 0 0 15px rgba(0, 255, 136, 0.3) !important;
    transition: all 0.2s ease !important;
}

div.stButton > button[kind="primary"]:hover, div[data-testid="stFormSubmitButton"] > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 0 25px rgba(0, 255, 136, 0.6) !important;
}

div.stButton > button[kind="secondary"] {
    background: rgba(10, 20, 30, 0.8) !important;
    color: #94a3b8 !important;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.8rem !important;
    padding: 0.4rem 0.8rem !important;
    border-radius: 6px !important;
}

div.stButton > button[kind="secondary"]:hover {
    border-color: #00ff88 !important;
    color: #ffffff !important;
}

/* -----------------------------------------------------------
   ANIMACIÓN DE ENTRADA Y DESPLAZAMIENTO DEL BLOQUE ENTERO
----------------------------------------------------------- */
@keyframes slideDownBlock {
    0% {
        opacity: 0;
        transform: translateY(-24px) scale(0.98);
    }
    60% {
        opacity: 0.95;
        transform: translateY(2px) scale(1.002);
    }
    100% {
        opacity: 1;
        transform: translateY(0) scale(1);
    }
}

/* El bloque contenedor completo de cada intercambio */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(6, 18, 28, 0.88) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-left: 4px solid rgba(14, 165, 233, 0.6) !important;
    border-radius: 10px !important;
    padding: 16px 20px !important;
    margin-bottom: 14px !important;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.55) !important;
    animation: slideDownBlock 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    transition: transform 0.35s ease, border-color 0.3s ease, box-shadow 0.3s ease !important;
}

/* Estilo distintivo para el primer bloque (el más nuevo en el tope) */
div[data-testid="stVerticalBlockBorderWrapper"]:first-of-type {
    border-left: 4px solid #00ff88 !important;
    border-color: rgba(0, 255, 136, 0.4) !important;
    background: rgba(6, 22, 34, 0.95) !important;
    box-shadow: 0 12px 35px rgba(0, 0, 0, 0.75), 0 0 25px rgba(0, 255, 136, 0.18) !important;
}

div[data-testid="stVerticalBlockBorderWrapper"]:not(:first-of-type):hover {
    border-left-color: #0ea5e9 !important;
    opacity: 1 !important;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.7) !important;
}

.turn-meta {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 10px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    padding-bottom: 8px;
}

.badge-latest {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.08em;
    font-weight: 700;
    background: #00ff88;
    color: #04090e;
    padding: 3px 8px;
    border-radius: 4px;
    text-transform: uppercase;
}

.badge-past {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.06em;
    font-weight: 600;
    background: rgba(14, 165, 233, 0.15);
    color: #38bdf8;
    border: 1px solid rgba(14, 165, 233, 0.3);
    padding: 3px 8px;
    border-radius: 4px;
    text-transform: uppercase;
}

.query-chip {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 0.86rem;
    color: #e2e8f0;
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.12);
    padding: 2px 10px;
    border-radius: 4px;
}
</style>
""", unsafe_allow_html=True)

# Fondo interactivo GPU
components.html(
    """
    <script>
    (function() {
        const pWin = window.parent;
        const pDoc = pWin.document;
        if (pWin.__RAG_BG_ACTIVE__) return;
        pWin.__RAG_BG_ACTIVE__ = true;

        let canvas = pDoc.getElementById('rag-lava-canvas');
        if (!canvas) {
            canvas = pDoc.createElement('canvas');
            canvas.id = 'rag-lava-canvas';
            canvas.style.cssText = 'position:fixed;top:0;left:0;width:100vw;height:100vh;pointer-events:none;z-index:0;background:#04090e;';
            pDoc.body.prepend(canvas);
        }

        const ctx = canvas.getContext('2d');
        let w = canvas.width = pWin.innerWidth;
        let h = canvas.height = pWin.innerHeight;

        pWin.addEventListener('resize', () => {
            w = canvas.width = pWin.innerWidth;
            h = canvas.height = pWin.innerHeight;
        });

        const blobs = [
            { x: w * 0.2, y: h * 0.3, r: 260, vx: 0.5, vy: 0.4, color: 'rgba(0, 255, 136, 0.14)' },
            { x: w * 0.8, y: h * 0.4, r: 290, vx: -0.4, vy: 0.5, color: 'rgba(14, 165, 233, 0.12)' },
            { x: w * 0.5, y: h * 0.75, r: 270, vx: 0.4, vy: -0.5, color: 'rgba(0, 255, 136, 0.08)' }
        ];

        function animate() {
            ctx.clearRect(0, 0, w, h);
            ctx.fillStyle = '#04090e';
            ctx.fillRect(0, 0, w, h);
            ctx.globalCompositeOperation = 'screen';

            for (let b of blobs) {
                b.x += b.vx; b.y += b.vy;
                if (b.x < -100 || b.x > w + 100) b.vx *= -1;
                if (b.y < -100 || b.y > h + 100) b.vy *= -1;

                const grad = ctx.createRadialGradient(b.x, b.y, b.r * 0.05, b.x, b.y, b.r);
                grad.addColorStop(0, b.color);
                grad.addColorStop(1, 'transparent');

                ctx.beginPath();
                ctx.arc(b.x, b.y, b.r, 0, Math.PI * 2);
                ctx.fillStyle = grad;
                ctx.fill();
            }
            ctx.globalCompositeOperation = 'source-over';
            requestAnimationFrame(animate);
        }
        animate();
    })();
    </script>
    """,
    height=0,
    width=0
)

st.markdown('<div class="brand-signature">Krov Industries · Conversación RAG</div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">Chat con Documentos PDF</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-lead">Indexación semántica con panel de lectura de respuestas prioritario</div>', unsafe_allow_html=True)

# ============================================================
# FUNCIONES AUXILIARES: CHUNKER RESILIENTE Y RAG NUMPY
# ============================================================
def dividir_texto_resiliente(paginas_texto, chunk_size=800, overlap=120):
    try:
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=overlap)
        split_fn = splitter.split_text
    except ImportError:
        try:
            from langchain.text_splitter import RecursiveCharacterTextSplitter
            splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=overlap)
            split_fn = splitter.split_text
        except ImportError:
            def split_fn(txt):
                chunks, i = [], 0
                while i < len(txt):
                    fin = min(i + chunk_size, len(txt))
                    chunks.append(txt[i:fin])
                    if fin == len(txt): break
                    i += chunk_size - overlap
                return chunks

    fragmentos = []
    for num_pag, contenido in paginas_texto:
        sub_tramos = split_fn(contenido)
        for fragmento in sub_tramos:
            limpio = fragmento.strip()
            if len(limpio) > 20:
                fragmentos.append({"texto": limpio, "pagina": num_pag})
    return fragmentos

def vectorizar_fragmentos(chunks, client):
    textos = [c["texto"] for c in chunks]
    lote_tam = 60
    todos_vectores = []
    for i in range(0, len(textos), lote_tam):
        sub_lote = textos[i:i + lote_tam]
        resp = client.embeddings.create(input=sub_lote, model="text-embedding-3-small")
        todos_vectores.extend([d.embedding for d in resp.data])
    return np.array(todos_vectores, dtype=np.float32)

def buscar_fragmentos_relevantes(query, client, chunks, vectores, k=4):
    q_vec = np.array(client.embeddings.create(input=[query], model="text-embedding-3-small").data[0].embedding, dtype=np.float32)
    normas = np.linalg.norm(vectores, axis=1) * np.linalg.norm(q_vec) + 1e-10
    similitudes = np.dot(vectores, q_vec) / normas
    mejores_indices = np.argsort(similitudes)[::-1][:k]
    return [chunks[idx] for idx in mejores_indices]

# ============================================================
# DISPOSICIÓN DE PANTALLA
# ============================================================
col_doc, col_chat = st.columns([1, 1.45], gap="large")

with col_doc:
    st.markdown("#### 1. Origen del Documento")
    api_key_input = st.text_input(
        "Clave de API de OpenAI:",
        type="password",
        value=os.environ.get("OPENAI_API_KEY", ""),
        placeholder="sk-..."
    )
    if api_key_input:
        os.environ["OPENAI_API_KEY"] = api_key_input

    pdf_file = st.file_uploader("Selecciona el archivo PDF:", type=["pdf"])

    if pdf_file:
        doc_signature = f"{pdf_file.name}_{pdf_file.size}"
        if st.session_state.pdf_id != doc_signature:
            if not api_key_input.strip():
                st.warning("Ingresa tu clave de OpenAI para procesar el archivo.")
            else:
                with st.spinner("Indexando documento en vectores..."):
                    try:
                        reader = PdfReader(pdf_file)
                        paginas = []
                        for i, pag in enumerate(reader.pages):
                            t = pag.extract_text() or ""
                            if t.strip():
                                paginas.append((i + 1, t))

                        if not paginas:
                            st.error("No se pudo extraer texto. Es posible que sea una imagen escaneada.")
                        else:
                            chunks = dividir_texto_resiliente(paginas)
                            client = OpenAI(api_key=api_key_input.strip())
                            matriz_embeddings = vectorizar_fragmentos(chunks, client)

                            st.session_state.pdf_id = doc_signature
                            st.session_state.pdf_name = pdf_file.name
                            st.session_state.pdf_chunks = chunks
                            st.session_state.pdf_embeddings = matriz_embeddings
                            st.session_state.turns = []  # Reiniciar historial para el nuevo PDF
                            st.success(f"Listo: {len(chunks)} fragmentos indexados.")
                    except Exception as err:
                        st.error(f"Error procesando el PDF: {err}")

    if st.session_state.pdf_id:
        st.markdown(
            f"""<div class="meta-card">
            <b>Documento activo:</b> {st.session_state.pdf_name}<br>
            <b>Fragmentos:</b> {len(st.session_state.pdf_chunks)} bloques semánticos<br>
            <b>Índice:</b> Cosine similarity en memoria activa
            </div>""",
            unsafe_allow_html=True
        )

        st.write("")
        if st.button("Limpiar conversación", type="secondary", use_container_width=True):
            st.session_state.turns = []
            st.rerun()

with col_chat:
    # --------------------------------------------------------
    # CAMPO DE TEXTO SIEMPRE FIJO ARRIBA (STICKY)
    # --------------------------------------------------------
    st.markdown('<div class="sticky-input-anchor">', unsafe_allow_html=True)
    st.markdown("#### 2. Chat Interactivo (Lectura Prioritaria)")

    with st.form("chat_top_form", clear_on_submit=True):
        c_input, c_btn = st.columns([4.2, 1.3], gap="small")
        with c_input:
            pregunta_usuario = st.text_input(
                "Pregunta:",
                placeholder="Escribe tu pregunta sobre el PDF y presiona Enter...",
                label_visibility="collapsed"
            )
        with c_btn:
            submitted = st.form_submit_button("Consultar ↵", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # --------------------------------------------------------
    # ARQUITECTURA DE DESPLAZAMIENTO:
    # 1. Ranura superior reservada para la nueva respuesta entrante
    # 2. Contenedor inferior para los mensajes existentes (NUNCA desaparecen)
    # --------------------------------------------------------
    slot_nueva_respuesta = st.empty()
    contenedor_historial = st.container()

    # RENDERIZAR DE INMEDIATO EL HISTORIAL COMPLETO
    # Esto asegura que el mensaje anterior permanezca visible y se desplace hacia abajo
    with contenedor_historial:
        if st.session_state.turns:
            # Los turnos existentes se muestran en orden inverso (más reciente arriba)
            for i, t in enumerate(reversed(st.session_state.turns)):
                # Si no hay una nueva consulta escribiéndose en el slot superior, el primero tiene badge 'ÚLTIMA RESPUESTA'
                badge_html = '<span class="badge-past">RESPUESTA PREVIA</span>' if (submitted and pregunta_usuario.strip()) else ('<span class="badge-latest">⚡ ÚLTIMA RESPUESTA</span>' if i == 0 else '<span class="badge-past">RESPUESTA PREVIA</span>')

                with st.container(border=True):
                    st.markdown(f"""
                    <div class="turn-meta">
                        {badge_html}
                        <span class="query-chip"><b>Tú:</b> {html.escape(t['user'])}</span>
                    </div>
                    """, unsafe_allow_html=True)
                    st.markdown(t["assistant"])
        elif not (submitted and pregunta_usuario.strip()):
            with st.container(border=True):
                st.markdown("""
                <div style="text-align: center; color: #94a3b8; padding: 12px 0;">
                    El chat está listo. Escribe tu primera pregunta en el campo superior fijo para leer la respuesta aquí.
                </div>
                """, unsafe_allow_html=True)

    # SI HAY UNA NUEVA CONSULTA: ESCRIBIR EN EL SLOT SUPERIOR (EMPUJANDO EL HISTORIAL HACIA ABAJO)
    if submitted and pregunta_usuario.strip():
        api_actual = os.environ.get("OPENAI_API_KEY", "").strip()
        if not api_actual:
            st.warning("Introduce tu clave de OpenAI en el panel izquierdo.")
        elif not st.session_state.pdf_chunks or st.session_state.pdf_embeddings is None:
            st.warning("Carga primero un archivo PDF para habilitar las consultas.")
        else:
            try:
                client = OpenAI(api_key=api_actual)
                relevantes = buscar_fragmentos_relevantes(
                    pregunta_usuario,
                    client,
                    st.session_state.pdf_chunks,
                    st.session_state.pdf_embeddings,
                    k=4
                )

                contexto = "\n\n---\n\n".join([
                    f"[Página {c['pagina']}]: {c['texto']}" for c in relevantes
                ])

                system_prompt = (
                    "Eres el analista de información de Krov Industries. Responde con precisión a la consulta "
                    "del usuario basándote rigurosamente en los fragmentos del documento PDF proporcionados abajo.\n\n"
                    "REGLAS:\n"
                    "1. Sé claro, directo y estructurado.\n"
                    "2. Cita la página o páginas relevantes donde encontraste los datos (ej. [Página 4]).\n"
                    "3. Si el contexto no contiene la información, dilo con honestidad.\n\n"
                    f"CONTEXTO DEL DOCUMENTO:\n{contexto}"
                )

                # Historial de contexto para el LLM
                mensajes_api = [{"role": "system", "content": system_prompt}]
                for t in st.session_state.turns[-3:]:
                    mensajes_api.append({"role": "user", "content": t["user"]})
                    mensajes_api.append({"role": "assistant", "content": t["assistant"]})
                mensajes_api.append({"role": "user", "content": pregunta_usuario})

                stream = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=mensajes_api,
                    temperature=0.2,
                    stream=True
                )

                # Renderizar la nueva tarjeta en la parte superior dentro de un único bloque sólido con borde
                with slot_nueva_respuesta.container():
                    with st.container(border=True):
                        st.markdown(f"""
                        <div class="turn-meta">
                            <span class="badge-latest">⚡ ÚLTIMA RESPUESTA</span>
                            <span class="query-chip"><b>Tú:</b> {html.escape(pregunta_usuario)}</span>
                        </div>
                        """, unsafe_allow_html=True)
                        nueva_respuesta = st.write_stream(stream)

                # Guardar el intercambio en el historial cronológico
                st.session_state.turns.append({
                    "user": pregunta_usuario,
                    "assistant": nueva_respuesta
                })

            except Exception as e:
                st.error(f"Error durante la inferencia: {e}")
