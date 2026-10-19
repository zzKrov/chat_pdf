import os
import streamlit as st
from PyPDF2 import PdfReader

# ============================================================
# CONFIGURACIÓN GENERAL (SIN SIDEBAR Y SIN BORDER=TRUE)
# ============================================================
st.set_page_config(
    page_title="Consulta de Documentos PDF // Krov Industries",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# ESTILOS VISUALES: OCÉANO LÍQUIDO Y TARJETAS SÓLIDAS
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [data-testid="stAppViewContainer"], .stApp {
    background-color: #04090e !important;
    color: #f1f5f9 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    overflow-x: hidden;
}

[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stSidebar"], section[data-testid="stSidebar"] { display: none !important; }

/* Fondo líquido animado en GPU */
.stApp {
    background:
        radial-gradient(circle at 15% 20%, rgba(0, 255, 136, 0.16) 0%, transparent 40%),
        radial-gradient(circle at 85% 30%, rgba(14, 165, 233, 0.16) 0%, transparent 45%),
        linear-gradient(135deg, #04090e 0%, #071a24 50%, #04090e 100%) !important;
    background-size: 200% 200% !important;
    animation: tealLava 14s ease infinite alternate !important;
}

@keyframes tealLava {
    0% { background-position: 0% 0%; }
    50% { background-position: 100% 100%; }
    100% { background-position: 0% 100%; }
}

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

/* Tarjeta sólida compatible con versiones previas de Streamlit */
.solid-rag-card {
    background: rgba(8, 20, 30, 0.88);
    border: 1px solid rgba(0, 255, 136, 0.28);
    border-radius: 8px;
    padding: 22px;
    backdrop-filter: blur(14px);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6);
    margin-bottom: 1rem;
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

.answer-box {
    background: rgba(6, 16, 24, 0.9);
    border-left: 4px solid #00ff88;
    padding: 18px;
    border-radius: 6px;
    margin-top: 14px;
    line-height: 1.65;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="brand-signature">Krov Industries · Recuperación RAG</div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">Consulta de Documentos PDF</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-lead">Indexación y respuestas contextualizadas a partir del contenido de archivos PDF</div>', unsafe_allow_html=True)

col_doc, col_qa = st.columns([1, 1.3], gap="large")

with col_doc:
    st.markdown('<div class="solid-rag-card">', unsafe_allow_html=True)
    st.markdown("#### 1. Archivo y Credenciales")
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
    st.markdown('</div>', unsafe_allow_html=True)

with col_qa:
    st.markdown('<div class="solid-rag-card">', unsafe_allow_html=True)
    st.markdown("#### 2. Pregunta al documento")
    pregunta = st.text_area("Pregunta:", placeholder="¿Cuáles son los puntos clave tratados en el archivo?")
    consultar_btn = st.button("Consultar documento", use_container_width=True)

    if consultar_btn:
        key_val = os.environ.get("OPENAI_API_KEY", "").strip()
        if not key_val:
            st.warning("Introduce tu clave de API de OpenAI en el panel izquierdo.")
        elif not pdf or not chunks:
            st.warning("Carga primero un archivo PDF válido.")
        elif not pregunta.strip():
            st.warning("Escribe una pregunta para consultar.")
        else:
            with st.spinner("Buscando en los fragmentos del documento..."):
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
                    docs = db.similarity_search(pregunta)
                    llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini", openai_api_key=key_val)
                    chain = load_qa_chain(llm, chain_type="stuff")
                    res = chain.run(input_documents=docs, question=pregunta)

                    st.markdown(f'<div class="answer-box"><b>Respuesta:</b><br>{res}</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Error durante la inferencia: {e}")
    st.markdown('</div>', unsafe_allow_html=True)
