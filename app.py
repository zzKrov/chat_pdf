import os
import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain

# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================
st.set_page_config(
    page_title="RAG sobre Documentos PDF // Krov Industries",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# LÍNEA BASE VISUAL: ESMERALDA TÉCNICO Y OCEANIC TEAL
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap');

html, body, [data-testid="stAppViewContainer"], .stApp {
    background-color: #04090e !important;
    color: #f1f5f9 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    overflow-x: hidden;
}

[data-testid="stHeader"] { background: transparent !important; }

/* 1. Malla continua de gradientes */
.stApp {
    background: linear-gradient(135deg, #04090e 0%, #061922 30%, #09262f 60%, #040b12 100%) !important;
    background-size: 300% 300% !important;
    animation: tealShift 18s ease infinite alternate !important;
}

@keyframes tealShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* 2. Fluidos orgánicos */
.fluid-teal-1 {
    position: fixed;
    top: 15%;
    left: -120px;
    width: 520px;
    height: 520px;
    background: radial-gradient(circle, rgba(0, 255, 136, 0.12) 0%, rgba(14, 165, 233, 0.04) 55%, transparent 75%);
    border-radius: 40% 60% 70% 30% / 50% 60% 40% 50%;
    filter: blur(85px);
    animation: tealDrift1 20s infinite alternate ease-in-out;
    pointer-events: none;
    z-index: 0;
}

.fluid-teal-2 {
    position: fixed;
    bottom: 5%;
    right: -100px;
    width: 560px;
    height: 560px;
    background: radial-gradient(circle, rgba(14, 165, 233, 0.12) 0%, rgba(0, 255, 136, 0.03) 55%, transparent 75%);
    border-radius: 60% 40% 50% 50% / 40% 50% 60% 50%;
    filter: blur(90px);
    animation: tealDrift2 24s infinite alternate ease-in-out;
    pointer-events: none;
    z-index: 0;
}

@keyframes tealDrift1 {
    0% { transform: translate(0, 0) scale(1); }
    50% { transform: translate(110px, 60px) scale(1.15); }
    100% { transform: translate(30px, 130px) scale(0.95); }
}

@keyframes tealDrift2 {
    0% { transform: translate(0, 0) scale(1); }
    50% { transform: translate(-100px, -70px) scale(1.2); }
    100% { transform: translate(-20px, -110px) scale(0.9); }
}

.brand-signature {
    text-align: center;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.18em;
    color: #00ff88;
    text-transform: uppercase;
    margin-bottom: 2px;
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
    margin-bottom: 1.8rem;
}

.rag-card {
    background: rgba(8, 20, 28, 0.85);
    border: 1px solid rgba(0, 255, 136, 0.25);
    border-left: 4px solid #00ff88;
    border-radius: 8px;
    padding: 22px;
    backdrop-filter: blur(14px);
    box-shadow: 0 10px 35px rgba(0, 0, 0, 0.6);
}

div.stButton > button {
    border-radius: 6px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.85rem !important;
    background: linear-gradient(135deg, #00ff88 0%, #0ea5e9 100%) !important;
    color: #04090e !important;
    font-weight: 700 !important;
    border: none !important;
    padding: 0.75rem 1.6rem !important;
    box-shadow: 0 0 20px rgba(0, 255, 136, 0.35) !important;
    transition: all 0.25s ease !important;
}

div.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 0 30px rgba(0, 255, 136, 0.6) !important;
}
</style>

<div class="fluid-teal-1"></div>
<div class="fluid-teal-2"></div>
""", unsafe_allow_html=True)

# ============================================================
# BARRA LATERAL (AUTENTICACIÓN)
# ============================================================
with st.sidebar:
    st.markdown("### Configuración de Conexión")
    ke = st.text_input(
        'Clave de API de OpenAI',
        type="password",
        value=os.environ.get("OPENAI_API_KEY", "")
    )
    if ke:
        os.environ['OPENAI_API_KEY'] = ke

st.markdown('<div class="brand-signature">Krov Industries · Recuperación Semántica</div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">Generación Aumentada por Recuperación (RAG)</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-lead">Indexación vectorial y consulta contextual sobre documentos PDF</div>', unsafe_allow_html=True)

col_doc, col_qa = st.columns([1, 1.3], gap="large")

with col_doc:
    st.markdown('<div class="rag-card">', unsafe_allow_html=True)
    st.markdown("### 1. Carga del Documento")
    pdf = st.file_uploader("Seleccionar archivo PDF:", type="pdf")
    
    if pdf is not None:
        try:
            pdf_reader = PdfReader(pdf)
            text = "".join([page.extract_text() or "" for page in pdf_reader.pages])
            st.info(f"Texto extraído: {len(text):,} caracteres.")

            text_splitter = CharacterTextSplitter(
                separator="\n",
                chunk_size=500,
                chunk_overlap=20,
                length_function=len
            )
            chunks = text_splitter.split_text(text)
            st.success(f"Documento dividido en {len(chunks)} fragmentos.")
        except Exception as e:
            st.error(f"Error al procesar el archivo: {e}")
            chunks = None
    else:
        chunks = None
    st.markdown('</div>', unsafe_allow_html=True)

with col_qa:
    st.markdown('<div class="rag-card">', unsafe_allow_html=True)
    st.markdown("### 2. Consulta Semántica")
    user_question = st.text_area("Pregunta sobre el contenido:", placeholder="¿Cuáles son las conclusiones principales del texto?")
    preguntar_btn = st.button("Consultar documento", use_container_width=True)

    if preguntar_btn and pdf is not None and chunks and os.environ.get("OPENAI_API_KEY"):
        with st.spinner("Recuperando fragmentos y generando respuesta..."):
            try:
                embeddings = OpenAIEmbeddings()
                knowledge_base = FAISS.from_texts(chunks, embeddings)
                docs = knowledge_base.similarity_search(user_question)
                llm = OpenAI(temperature=0, model_name="gpt-4o-mini")
                chain = load_qa_chain(llm, chain_type="stuff")
                response = chain.run(input_documents=docs, question=user_question)

                st.markdown("#### Respuesta Generada:")
                st.write(response)
            except Exception as e:
                st.error(f"Error durante la inferencia: {e}")
    elif preguntar_btn and not os.environ.get("OPENAI_API_KEY"):
        st.warning("Introduce una clave de API de OpenAI en el panel lateral.")
    elif preguntar_btn and pdf is None:
        st.warning("Carga primero un archivo PDF para habilitar la consulta.")
    st.markdown('</div>', unsafe_allow_html=True)
