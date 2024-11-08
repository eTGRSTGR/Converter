import os
import google.generativeai as genai
from dotenv import load_dotenv
import streamlit as st
import tempfile
from io import BytesIO

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Configura a API key do Google Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Função para fazer o upload do arquivo para Gemini
def upload_to_gemini(file, mime_type=None):
    """Uploads the given file to Gemini."""
    uploaded_file = genai.upload_file(file, mime_type=mime_type)
    return uploaded_file

# Configuração da página do Streamlit
st.title("Transcrição de Áudio com Google Gemini")
st.write("Faça o upload do seu arquivo de áudio para transcrição.")

# Carregamento do arquivo via Streamlit
uploaded_file = st.file_uploader("Escolha um arquivo de áudio", type=["ogg", "mp3", "wav"])

if uploaded_file is not None:
    try:
        # Determina o tipo MIME do arquivo selecionado
        mime_type = uploaded_file.type

        # Salva o arquivo temporariamente em memória como BytesIO
        temp_file = BytesIO(uploaded_file.read())

        # Faz o upload do arquivo usando a função
        with st.spinner("Fazendo upload do arquivo e preparando a transcrição..."):
            audio_file = upload_to_gemini(temp_file, mime_type=mime_type)

        # Cria uma sessão de chat para transcrever o áudio
        generation_config = {
            "temperature": 2,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain",
        }

        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=generation_config,
        )

        chat_session = model.start_chat(
            history=[
                {
                    "role": "user",
                    "parts": [
                        audio_file,
                        "transcreva o áudio em texto",
                    ],
                }
            ]
        )

        # Envia a mensagem para obter a transcrição
        with st.spinner("Transcrevendo o áudio..."):
            response = chat_session.send_message("transcreva o áudio")

        # Exibe a transcrição do áudio
        st.success("Transcrição concluída!")
        st.write("### Transcrição do Áudio:")
        st.text(response.text)

    except Exception as e:
        st.error("Ocorreu um erro durante o processamento do arquivo.")
        st.write(f"Detalhes do erro: {str(e)}")

else:
    st.write("Por favor, faça o upload de um arquivo de áudio para continuar.")
