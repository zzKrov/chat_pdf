import os
import streamlit as st
import streamlit.components.v1 as components
from PyPDF2 import PdfReader

# ============================================================
# CONFIGURACIÓN GENERAL (SIN SIDEBAR)
# ============================================================
st.set_page_config(
    page_title="Consulta de Documentos PDF // Krov Industries",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# ESTILOS VISUALES: ESMERALDA LÍQUIDO Y RESPLANDOR
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

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
    font-size: 2.2rem;
    font-weight: 700;
    text-align: center;
    color: #ffffff;
    margin-bottom: 0.2rem;
    text-shadow: 0 0 25px rgba(0, 255, 136, 0.4);
}

.sub-lead {
    text-align: center;
    color: #94a3b8;
    font-size: 0.95rem;
    margin-bottom: 1.6rem;
}

.rag-panel {
    background: rgba(8, 20, 30, 0.88);
    border: 1px solid rgba(0, 255, 136, 0.28);
    border-radius: 8px;
    padding: 22px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6);
    margin-bottom: 1.2rem;
}

div.stButton > button {
    border-radius: 6px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.88rem !important;
    background: linear-gradient(135deg, #00ff88 0%, #0ea5e9 100%) !important;
    color: #04090e !important;
    font-weight: 700 !important;
    border: none !important;
    padding: 0.75rem 1.6rem !important;
    box-shadow: 0 0 20px rgba(0, 255, 136, 0.35) !important;
    transition: all 0.25s ease !important;
}

div.stButton > button:hover {
    transform: translateY(-2px) scale(1.02) !important;
    box-shadow: 0 0 35px rgba(0, 255, 136, 0.7) !important;
}

.answer-card {
    background: rgba(6, 16, 24, 0.92);
    border-left: 4px solid #00ff88;
    padding: 20px;
    border-radius: 6px;
    margin-top: 14px;
    line-height: 1.7;
    box-shadow: 0 8px 25px rgba(0,0,0,0.5);
}
</style>
""", unsafe_allow_html=True)

# Fondo interactivo esmeralda animado (Cero Lag)
components.html(
    """
    <script>
    (function() {
        const pWin = window.parent;
        const pDoc = pWin.document;
        if (pWin.__RAG_BG_INIT__) return;
        pWin.__RAG_BG_INIT__ = true;

        let canvas = pDoc.getElementById('rag-fluid-canvas');
        if (!canvas) {
            canvas = pDoc.createElement('canvas');
            canvas.id = 'rag-fluid-canvas';
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

        const orbs = [
            { x: w * 0.2, y: h * 0.3, r: 260, vx: 0.5, vy: 0.4, color: 'rgba(0, 255, 136, 0.16)' },
            { x: w * 0.75, y: h * 0.4, r: 280, vx: -0.4, vy: 0.5, color: 'rgba(14, 165, 233, 0.15)' },
            { x: w * 0.5, y: h * 0.8, r: 240, vx: 0.4, vy: -0.5, color: 'rgba(0, 255, 200, 0.12)' }
        ];

        function loop() {
            ctx.clearRect(0, 0, w, h);
            ctx.fillStyle = '#04090e';
            ctx.fillRect(0, 0, w, h);
            ctx.globalCompositeOperation = 'screen';

            for (let b of orbs) {
                b.x += b.vx;
                b.y += b.vy;
                if (b.x < -100 || b.x > w + 100) b.vx *= -1;
                if (b.y < -100 || b.y > h + 100) b.vy *= -1;

                const g = ctx.createRadialGradient(b.x, b.y, 10, b.x, b.y, b.r);
                g.addColorStop(0, b.color);
                g.addColorStop(1, 'transparent');
                ctx.beginPath();
                ctx.arc(b.x, b.y, b.r, 0, Math.PI * 2);
                ctx.fillStyle = g;
                ctx.fill();
            }
            requestAnimationFrame(loop);
        }
        loop();
    })();
    </script>
    """,
    height=0,
    width=0
)

st.markdown('<div class="brand-signature">Krov Industries · Recuperación Semántica</div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">Consulta de Documentos PDF</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-lead">Indexación y respuestas contextualizadas a partir del contenido de archivos PDF</div>', unsafe_allow_html=True)

col_doc, col_qa = st.columns([1, 1.3], gap="large")

with col_doc:
    st.markdown('<div class="rag-panel">', unsafe_allow_html=True)
    st.markdown("#### 1. Archivo y Clave OpenAI")
    api_key_input = st.text_input(
        "Clave de API de OpenAI:",
        type="password",
        value=os.environ.get("OPENAI_API_KEY", ""),
        placeholder="sk-..."
    )
    if api_key_input:
        os.environ["OPENAI_API_KEY"] = api_key_input

    pdf_file = st.file_uploader("Selecciona el archivo PDF:", type="pdf")
    chunks = None

    if pdf_file is not None:
        try:
            reader = PdfReader(pdf_file)
            texto = "".join([p.extract_text() or "" for p in reader.pages])
            st.info(f"Texto extraído: {len(texto):,} caracteres.")

            from langchain.text_splitter import CharacterTextSplitter
            splitter = CharacterTextSplitter(separator="\n", chunk_size=500, chunk_overlap=20)
            chunks = splitter.split_text(texto)
            st.success(f"Documento fragmentado en {len(chunks)} bloques de búsqueda.")
        except Exception as e:
            st.error(f"Error al procesar el archivo: {e}")
    st.markdown('</div>', unsafe_allow_html=True)

with col_qa:
    st.markdown('<div class="rag-panel">', unsafe_allow_html=True)
    st.markdown("#### 2. Pregunta al documento")
    pregunta = st.text_area("Pregunta:", placeholder="¿Cuáles son los puntos clave tratados en el archivo?")
    consultar_btn = st.button("Consultar documento", use_container_width=True)

    if consultar_btn:
        key_val = os.environ.get("OPENAI_API_KEY", "").strip()
        if not key_val:
            st.warning("Introduce tu clave de API de OpenAI en el campo del panel izquierdo.")
        elif not pdf_file or not chunks:
            st.warning("Carga primero un archivo PDF para indexarlo.")
        elif not pregunta.strip():
            st.warning("Escribe una pregunta para consultar.")
        else:
            prog = st.progress(0, text="Indexando vectores con FAISS...")
            try:
                try:
                    from langchain_community.embeddings import OpenAIEmbeddings
                    from langchain_community.vectorstores import FAISS
                    from langchain_community.chat_models import ChatOpenAI
                except ImportError:
                    from langchain.embeddings import OpenAIEmbeddings
                    from langchain.vectorstores import FAISS
                    from langchain.llms import OpenAI as ChatOpenAI

                from langchain.chains.question_answering import load_qa_chain

                embeddings = OpenAIEmbeddings(openai_api_key=key_val)
                db = FAISS.from_texts(chunks, embeddings)
                prog.progress(50, text="Buscando coincidencias semánticas...")

                docs = db.similarity_search(pregunta)
                llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini", openai_api_key=key_val)
                chain = load_qa_chain(llm, chain_type="stuff")
                
                prog.progress(80, text="Sintetizando respuesta...")
                res = chain.run(input_documents=docs, question=pregunta)
                prog.progress(100, text="Consulta completada.")

                st.markdown(f'<div class="answer-card"><b>Respuesta:</b><br><br>{res}</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error durante la inferencia: {e}")
    st.markdown('</div>', unsafe_allow_html=True)
