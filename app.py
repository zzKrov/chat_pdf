import os
import streamlit as st
import streamlit.components.v1 as components
from PyPDF2 import PdfReader

# ============================================================
# CONFIGURACIÓN GENERAL (SIN SIDEBAR Y COMPATIBLE CON STREAMLIT CLOUD)
# ============================================================
st.set_page_config(
    page_title="Consulta de Documentos PDF // Krov Industries",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# ESTILOS VISUALES: ESMERALDA LÍQUIDO GPU Y TARJETAS SÓLIDAS
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [data-testid="stAppViewContainer"], .stApp, section.main, .block-container {
    background: transparent !important;
    background-color: transparent !important;
    color: #f1f5f9 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    overflow-x: hidden;
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
    text-shadow: 0 0 25px rgba(0, 255, 136, 0.35);
}

.sub-lead {
    text-align: center;
    color: #94a3b8;
    font-size: 0.95rem;
    margin-bottom: 1.6rem;
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
    transform: translateY(-2px) !important;
    box-shadow: 0 0 35px rgba(0, 255, 136, 0.7) !important;
}

.answer-card {
    background: rgba(6, 16, 24, 0.92);
    border-left: 4px solid #00ff88;
    padding: 18px;
    border-radius: 6px;
    margin-top: 14px;
    line-height: 1.65;
    box-shadow: 0 8px 30px rgba(0,0,0,0.6);
}
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------
# FONDO LÍQUIDO ESMERALDA EN GPU (SIN BLOQUEOS)
# ------------------------------------------------------------
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

st.markdown('<div class="brand-signature">Krov Industries · Recuperación RAG</div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">Consulta de Documentos PDF</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-lead">Indexación e interrogación de archivos PDF mediante modelos de lenguaje</div>', unsafe_allow_html=True)

col_doc, col_qa = st.columns([1, 1.3], gap="large")

with col_doc:
    st.markdown("#### 1. Carga de Documento")
    api_key = st.text_input("Clave de API de OpenAI:", type="password", value=os.environ.get("OPENAI_API_KEY", ""), placeholder="sk-...")
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key

    pdf = st.file_uploader("Selecciona el archivo PDF:", type="pdf")
    chunks = None
    if pdf:
        try:
            reader = PdfReader(pdf)
            texto = "".join([p.extract_text() or "" for p in reader.pages])
            st.info(f"Texto extraído: {len(texto):,} caracteres.")

            from langchain.text_splitter import CharacterTextSplitter
            splitter = CharacterTextSplitter(separator="\n", chunk_size=500, chunk_overlap=20)
            chunks = splitter.split_text(texto)
            st.success(f"Indexado en {len(chunks)} fragmentos.")
        except Exception as e:
            st.error(f"Error al procesar el archivo: {e}")

with col_qa:
    st.markdown("#### 2. Consulta Semántica")
    pregunta = st.text_area("Pregunta:", placeholder="¿Cuáles son los puntos clave tratados en el archivo?")
    consultar_btn = st.button("Consultar documento", use_container_width=True)

    if consultar_btn:
        key_val = os.environ.get("OPENAI_API_KEY", "").strip()
        if not key_val:
            st.warning("Introduce tu clave de API de OpenAI.")
        elif not pdf or not chunks:
            st.warning("Carga primero un archivo PDF válido.")
        elif not pregunta.strip():
            st.warning("Escribe una pregunta para consultar.")
        else:
            prog = st.progress(0, text="Generando embeddings e indexando...")
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
                prog.progress(40, text="Buscando coincidencias semánticas...")
                db = FAISS.from_texts(chunks, embeddings)
                docs = db.similarity_search(pregunta)
                prog.progress(70, text="Sintetizando respuesta...")
                llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini", openai_api_key=key_val)
                chain = load_qa_chain(llm, chain_type="stuff")
                res = chain.run(input_documents=docs, question=pregunta)
                prog.progress(100, text="Consulta completada.")

                st.markdown(f'<div class="answer-card"><b>Respuesta:</b><br>{res}</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error durante la inferencia: {e}")
