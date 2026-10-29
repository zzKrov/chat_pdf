import os
import io
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

# Inicialización de estado de sesión
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pdf_id" not in st.session_state:
    st.session_state.pdf_id = None
if "pdf_chunks" not in st.session_state:
    st.session_state.pdf_chunks = []
if "pdf_embeddings" not in st.session_state:
    st.session_state.pdf_embeddings = None
if "pdf_name" not in st.session_state:
    st.session_state.pdf_name = ""

# ============================================================
# ESTILOS VISUALES: ESMERALDA LÍQUIDO GPU Y CHAT MODERNO
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

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
    padding-bottom: 2rem !important;
}

/* Tarjeta informativa */
.meta-card {
    background: rgba(6, 16, 24, 0.9);
    border: 1px solid rgba(0, 255, 136, 0.25);
    border-radius: 8px;
    padding: 16px;
    margin-top: 12px;
    font-size: 0.88rem;
    line-height: 1.6;
}

/* Personalización de los mensajes de chat */
[data-testid="stChatMessage"] {
    background: rgba(6, 16, 24, 0.85) !important;
    border: 1px solid rgba(0, 255, 136, 0.15) !important;
    border-radius: 8px !important;
    margin-bottom: 0.8rem !important;
    padding: 12px 16px !important;
}

[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    border-color: rgba(14, 165, 233, 0.35) !important;
    background: rgba(8, 22, 36, 0.85) !important;
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
</style>
""", unsafe_allow_html=True)

# Fondo interactivo líquido esmeralda
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
st.markdown('<div class="sub-lead">Indexación vectorial y consulta interactiva con memoria contextual</div>', unsafe_allow_html=True)

# ============================================================
# FUNCIONES AUXILIARES: CHUNKER RESILIENTE Y RAG EN NUMPY
# ============================================================
def dividir_texto_resiliente(paginas_texto, chunk_size=800, overlap=120):
    """Divide el texto preservando el número de página original sin fallos de importación."""
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
    """Genera embeddings por lotes usando text-embedding-3-small."""
    textos = [c["texto"] for c in chunks]
    lote_tam = 60
    todos_vectores = []
    for i in range(0, len(textos), lote_tam):
        sub_lote = textos[i:i + lote_tam]
        resp = client.embeddings.create(input=sub_lote, model="text-embedding-3-small")
        todos_vectores.extend([d.embedding for d in resp.data])
    return np.array(todos_vectores, dtype=np.float32)

def buscar_fragmentos_relevantes(query, client, chunks, vectores, k=4):
    """Búsqueda de máxima similitud coseno vectorial."""
    q_vec = np.array(client.embeddings.create(input=[query], model="text-embedding-3-small").data[0].embedding, dtype=np.float32)
    normas = np.linalg.norm(vectores, axis=1) * np.linalg.norm(q_vec) + 1e-10
    similitudes = np.dot(vectores, q_vec) / normas
    mejores_indices = np.argsort(similitudes)[::-1][:k]
    return [chunks[idx] for idx in mejores_indices]

# ============================================================
# INTERFAZ DIVIDIDA
# ============================================================
col_doc, col_chat = st.columns([1, 1.4], gap="large")

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
        # Solo procesar e indexar si es un documento nuevo
        if st.session_state.pdf_id != doc_signature:
            if not api_key_input.strip():
                st.warning("Ingresa tu clave de OpenAI para procesar el archivo.")
            else:
                with st.spinner("Leyendo y vectorizando PDF..."):
                    try:
                        reader = PdfReader(pdf_file)
                        paginas = []
                        for i, pag in enumerate(reader.pages):
                            t = pag.extract_text() or ""
                            if t.strip():
                                paginas.append((i + 1, t))

                        if not paginas:
                            st.error("No se pudo extraer texto. Es posible que el PDF sea una imagen escaneada sin OCR.")
                        else:
                            chunks = dividir_texto_resiliente(paginas)
                            client = OpenAI(api_key=api_key_input.strip())
                            matriz_embeddings = vectorizar_fragmentos(chunks, client)

                            # Guardar en sesión
                            st.session_state.pdf_id = doc_signature
                            st.session_state.pdf_name = pdf_file.name
                            st.session_state.pdf_chunks = chunks
                            st.session_state.pdf_embeddings = matriz_embeddings
                            st.session_state.messages = [
                                {
                                    "role": "assistant",
                                    "content": f"He analizado e indexado **{pdf_file.name}** ({len(paginas)} páginas, {len(chunks)} fragmentos). ¿Qué información necesitas consultar?"
                                }
                            ]
                            st.success(f"Indexación completada: {len(chunks)} fragmentos listos.")
                    except Exception as err:
                        st.error(f"Error procesando el PDF: {err}")

    # Información del PDF actual indexado
    if st.session_state.pdf_id:
        st.markdown(
            f"""<div class="meta-card">
            <b>Documento activo:</b> {st.session_state.pdf_name}<br>
            <b>Fragmentos vectoriales:</b> {len(st.session_state.pdf_chunks)} bloques<br>
            <b>Memoria:</b> Similitud coseno en memoria GPU/RAM
            </div>""",
            unsafe_allow_html=True
        )

        st.write("")
        if st.button("Limpiar conversación", type="secondary", use_container_width=True):
            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": f"Conversación reiniciada. ¿Qué otra duda tienes sobre **{st.session_state.pdf_name}**?"
                }
            ]
            st.rerun()

with col_chat:
    st.markdown("#### 2. Chat Interactivo")

    # Mostrar historial de mensajes
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Entrada de pregunta
    pregunta_usuario = st.chat_input("Escribe tu pregunta sobre el documento...")

    if pregunta_usuario:
        api_actual = os.environ.get("OPENAI_API_KEY", "").strip()

        if not api_actual:
            st.warning("Por favor introduce tu clave de OpenAI en el panel izquierdo.")
        elif not st.session_state.pdf_chunks or st.session_state.pdf_embeddings is None:
            st.warning("Carga primero un archivo PDF para habilitar el chat.")
        else:
            # 1. Registrar y mostrar pregunta del usuario
            st.session_state.messages.append({"role": "user", "content": pregunta_usuario})
            with st.chat_message("user"):
                st.markdown(pregunta_usuario)

            # 2. Recuperación RAG y generación de respuesta en streaming
            with st.chat_message("assistant"):
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
                        "Eres el analista de información de Krov Industries. Responde la consulta del usuario "
                        "basándote con fidelidad en los fragmentos del documento PDF proporcionados abajo.\n\n"
                        "REGLAS OBLIGATORIAS:\n"
                        "1. Sé claro, directo y riguroso.\n"
                        "2. Cita la página o páginas relevantes donde encontraste la información (ej. [Página 4]).\n"
                        "3. Si el contexto no contiene la respuesta, indícalo con precisión sin inventar datos.\n\n"
                        f"CONTEXTO EXTRAÍDO DEL PDF:\n{contexto}"
                    )

                    mensajes_api = [{"role": "system", "content": system_prompt}]
                    # Historial reciente para memoria conversacional
                    for m in st.session_state.messages[-5:]:
                        mensajes_api.append({"role": m["role"], "content": m["content"]})

                    stream = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=mensajes_api,
                        temperature=0.2,
                        stream=True
                    )

                    respuesta = st.write_stream(stream)
                    st.session_state.messages.append({"role": "assistant", "content": respuesta})

                except Exception as e:
                    st.error(f"Error en la inferencia: {e}")
