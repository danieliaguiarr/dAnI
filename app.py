import streamlit as st
from google import genai
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
os.environ["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY", "")

st.set_page_config(page_title="✨ DANI", page_icon="✨", layout="wide")

for key in ["msgs", "chat", "busy", "pending", "profile_name", "profile_mood", "conversations", "theme", "current_file", "file_content"]:
    if key not in st.session_state:
        if key == "msgs": st.session_state[key] = []
        elif key == "chat": st.session_state[key] = None
        elif key == "busy": st.session_state[key] = False
        elif key == "pending": st.session_state[key] = None
        elif key == "profile_name": st.session_state[key] = ""
        elif key == "profile_mood": st.session_state[key] = "😀"
        elif key == "conversations": st.session_state[key] = []
        elif key == "theme": st.session_state[key] = "dark"
        elif key == "current_file": st.session_state[key] = None
        elif key == "file_content": st.session_state[key] = None

C = {
    "dark": {"bg": "#0a0a0f", "card": "#1a1a2e", "input": "#0a0a0f", "text": "#e4e4e7", "border": "#333"},
    "light": {"bg": "#f5f5f7", "card": "#ffffff", "input": "#f0f0f3", "text": "#18181b", "border": "#e4e4e7"}
}[st.session_state.theme]

st.markdown(f"""
<style>
    .stApp {{ background: {C['bg']}; }}
    .sidebar {{ width: 260px; background: {C['card']}; padding: 1rem; height: 100vh; position: fixed; left: 0; top: 0; border-right: 1px solid {C['border']}; overflow-y: auto; }}
    .main {{ margin-left: 260px; max-width: 700px; margin: 0 auto; padding: 1rem; }}
    .logo {{ font-size: 1.8rem; font-weight: bold; background: linear-gradient(90deg, #8b5cf6, #f472b6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; margin-bottom: 1rem; }}
    .new-chat {{ width: 100%; padding: 0.8rem; background: #8b5cf6; color: white; border: none; border-radius: 10px; cursor: pointer; font-weight: 600; margin-bottom: 1rem; }}
    .new-chat:hover {{ background: #7c3aed; }}
    .history-item {{ padding: 0.6rem; background: {C['input']}; border-radius: 8px; margin: 0.3rem 0; cursor: pointer; color: {C['text']}; font-size: 0.85rem; display: flex; justify-content: space-between; align-items: center; }}
    .history-item:hover {{ background: #8b5cf620; }}
    .delete-btn {{ background: none; border: none; color: #ef4444; cursor: pointer; font-size: 0.8rem; }}
    .section-title {{ color: #8b5cf6; font-size: 0.8rem; font-weight: 600; margin: 1rem 0 0.5rem; }}
    .msg {{ display: flex; gap: 0.5rem; margin: 0.6rem 0; }}
    .msg-user {{ flex-direction: row-reverse; }}
    .avatar {{ width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.9rem; }}
    .avatar-user {{ background: #8b5cf6; }}
    .avatar-ai {{ background: #06b6d4; }}
    .bubble {{ padding: 0.7rem 1rem; border-radius: 15px; max-width: 80%; word-wrap: break-word; }}
    .bubble-user {{ background: linear-gradient(135deg, #8b5cf6, #7c3aed); color: white; }}
    .bubble-ai {{ background: {C['card']}; color: {C['text']}; border: 1px solid {C['border']}; }}
    .file-preview {{ text-align: center; margin: 0.5rem 0; }}
    .file-preview img {{ max-width: 100%; border-radius: 10px; }}
    .dot {{ width: 6px; height: 6px; background: #8b5cf6; border-radius: 50%; display: inline-block; animation: pulse 1s infinite; }}
    .dot:nth-child(2) {{ animation-delay: 0.2s; }}
    .dot:nth-child(3) {{ animation-delay: 0.4s; }}
    @keyframes pulse {{ 0%, 100% {{ opacity: 0.4; }} 50% {{ opacity: 1; }} }}
    .greeting {{ text-align: center; color: #71717a; font-size: 0.9rem; margin-bottom: 0.5rem; }}
    .toolbar {{ display: flex; gap: 0.5rem; margin-bottom: 1rem; flex-wrap: wrap; }}
    .tool-btn {{ padding: 0.4rem 0.8rem; background: {C['card']}; border: 1px solid {C['border']}; border-radius: 20px; color: {C['text']}; cursor: pointer; font-size: 0.8rem; }}
    .stTextInput > div > div > input {{ background: {C['input']}; color: {C['text']}; border: 1px solid {C['border']}; }}
    .stButton > button {{ background: #8b5cf6; color: white; border: none; }}
    .mode-toggle {{ position: fixed; bottom: 1rem; left: 1rem; font-size: 1.5rem; cursor: pointer; }}
    .pin-btn {{ position: fixed; top: 1rem; right: 1rem; font-size: 1.2rem; cursor: pointer; }}
    .analyze-btn {{ background: #06b6d4; color: white; border: none; padding: 0.5rem 1rem; border-radius: 8px; cursor: pointer; margin-top: 0.5rem; }}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    if st.button("+ Nova Conversa", use_container_width=True):
        st.session_state.msgs = []
        st.session_state.chat = None
        st.session_state.current_file = None
        st.session_state.file_content = None
        st.rerun()
    
    st.markdown(f'<div class="section-title">📁 Enviar Imagem</div>', unsafe_allow_html=True)
    image_types = ["png", "jpg", "jpeg", "webp", "gif"]
    uploaded_file = st.file_uploader("", type=image_types)
    
    if uploaded_file:
        st.session_state.current_file = uploaded_file.name
        st.session_state.file_content = uploaded_file.read()
        
        st.image(uploaded_file, caption=uploaded_file.name, use_container_width=True)
        
        if st.button("🔍 Analisar Imagem", use_container_width=True):
            with st.spinner("Analisando..."):
                try:
                    client = genai.Client()
                    from google.genai import types
                    image_data = uploaded_file.read()
                    uploaded_file.seek(0)
                    
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=[
                            types.Content(
                                parts=[
                                    types.Part(inline_data=types.Blob(data=image_data, mime_type=uploaded_file.type)),
                                    types.Part(text="Analise esta imagem e descreva o que você vê com detalhes.")
                                ]
                            )
                        ]
                    )
                    
                    st.session_state.msgs.append({
                        "role": "user", 
                        "content": f"📷 Imagem: {uploaded_file.name}"
                    })
                    st.session_state.msgs.append({
                        "role": "assistant", 
                        "content": response.text
                    })
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro: {str(e)}")
        
        if st.button("🗑️ Remover imagem"):
            st.session_state.current_file = None
            st.session_state.file_content = None
            st.rerun()
    
    st.markdown(f'<div class="section-title">📄 Arquivos (texto)</div>', unsafe_allow_html=True)
    doc_file = st.file_uploader("", type=["pdf", "txt", "doc"], key="doc_uploader")
    if doc_file:
        st.success(f"📎 {doc_file.name}")
        st.session_state.current_doc = doc_file

    st.markdown(f'<div class="section-title">💬 Histórico</div>', unsafe_allow_html=True)
    
    search = st.text_input("🔍 Buscar...", key="search_history")
    filtered_convs = [c for c in st.session_state.conversations if search.lower() in str(c["messages"]).lower()] if search else st.session_state.conversations
    
    for i, conv in enumerate(reversed(filtered_convs[-8:])):
        col1, col2 = st.columns([4, 1])
        with col1:
            if st.button(f"💬 {conv['date']}", key=f"hist_{i}"):
                st.session_state.msgs = conv["messages"].copy()
                st.rerun()
        with col2:
            if st.button("🗑️", key=f"del_{i}"):
                st.session_state.conversations.remove(conv)
                st.rerun()
    
    if st.button("⭐ Fixar conversa"):
        if st.session_state.msgs:
            st.session_state.pinned = st.session_state.msgs.copy()
            st.success("Fixado!")

st.markdown(f'<div class="pin-btn">{"📌" if not st.session_state.get("pinned") else "📍"}</div>', unsafe_allow_html=True)
if st.session_state.get("pinned") and st.button("📌 Carregar"):
    st.session_state.msgs = st.session_state.pinned.copy()
    st.rerun()

st.markdown(f'<div class="mode-toggle">{"🌙" if st.session_state.theme == "light" else "☀️"}</div>', unsafe_allow_html=True)
if st.button("🌙" if st.session_state.theme == "light" else "☀️"):
    st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
    st.rerun()

with st.expander("⚙️ Perfil"):
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.profile_name = st.text_input("Seu nome:", value=st.session_state.profile_name)
    with col2:
        st.markdown("Humor:", unsafe_allow_html=True)
        moods = ["😀", "😎", "🤩", "😄", "🥳", "🤔", "😴", "🔥"]
        cols = st.columns(8)
        for i, m in enumerate(moods):
            if cols[i].button(m, key=f"mood_{i}"):
                st.session_state.profile_mood = m
                st.rerun()
    st.markdown(f"**Humor:** {st.session_state.profile_mood}")

st.markdown('<div class="main">', unsafe_allow_html=True)

greetings = {"😀": "Olá! Que bom te ver! 😊", "😎": "E aí! Curtindo? 😎", "🤩": "Uau, animado! ✨", "😄": "Hello! 😄", "🥳": "Party! 🎉", "🤔": "Hmm... 💭", "😴": "Zzz... ☕", "🔥": "Quente! 🔥"}
user_name = st.session_state.profile_name or "amigo"
st.markdown(f'<div class="greeting">{greetings.get(st.session_state.profile_mood, "Olá!")} {user_name}!</div>', unsafe_allow_html=True)
st.markdown('<div class="logo">✨ DANI</div>', unsafe_allow_html=True)

if not os.getenv("GEMINI_API_KEY"):
    st.error("Configure GEMINI_API_KEY no arquivo .env")
    st.stop()

for msg in st.session_state.msgs:
    st.markdown(f'<div class="msg {"msg-user" if msg["role"]=="user" else ""}"><div class="avatar {"avatar-user" if msg["role"]=="user" else "avatar-ai"}">{"😎" if msg["role"]=="user" else "✨"}</div><div class="bubble {"bubble-user" if msg["role"]=="user" else "bubble-ai"}">{msg["content"]}</div></div>', unsafe_allow_html=True)

if st.session_state.busy:
    st.markdown('<div class="msg"><div class="avatar avatar-ai">✨</div><div class="bubble bubble-ai"><span class="dot"></span><span class="dot"></span><span class="dot"></span></div></div>', unsafe_allow_html=True)

if prompt := st.chat_input("Digite..."):
    st.session_state.msgs.append({"role": "user", "content": prompt})
    st.session_state.pending = prompt
    st.session_state.busy = True
    st.rerun()

if st.session_state.busy and st.session_state.pending:
    p = st.session_state.pending
    st.session_state.pending = None
    r = ""
    
    context = f"Conversando com {user_name}. "
    
    try:
        if st.session_state.chat is None:
            st.session_state.client = genai.Client()
            st.session_state.chat = st.session_state.client.chats.create(model="gemini-2.5-flash")
        r = st.session_state.chat.send_message(context + p).text
    except Exception as e:
        r = f"Ops! Erro 😅"
        st.session_state.chat = None
    
    st.session_state.msgs.append({"role": "assistant", "content": r})
    st.session_state.busy = False
    st.rerun()

if st.button("💾 Salvar"):
    if st.session_state.msgs:
        st.session_state.conversations.append({
            "date": datetime.now().strftime("%d/%m %H:%M"),
            "msgs": len(st.session_state.msgs),
            "messages": st.session_state.msgs.copy()
        })
        st.success("Salvo!")

st.markdown('</div>', unsafe_allow_html=True)