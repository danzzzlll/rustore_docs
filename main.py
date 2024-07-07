import utils.generatives
import os
from utils.get_prompt import get_documents
from utils.config import GenerationConfig
from utils.ranking import MyExistingRetrievalPipeline
from ragatouille import RAGPretrainedModel
import streamlit as st
import joblib

@st.cache_resource
def load_model():
    utils.generatives.get_os()
    model_path = 'mistralai/Mistral-7B-Instruct-v0.2'
    solar = utils.generatives.Mistral("mistral", model_path)
    giga = utils.generatives.GigaApi("gigachat")
    
    pipeline = MyExistingRetrievalPipeline()
    pipeline.load_index('./indexes/indexes_cp.index', 
                        './indexes/collection_cp.pkl', 
                        './indexes/bm_cp.pkl')

    RAG = RAGPretrainedModel.from_pretrained("antoinelouis/colbert-xm")
    
    return solar, giga, pipeline, RAG


@st.cache_resource
def load_df():
    df = joblib.load('./indexes/content_new.pkl')
    meta = joblib.load('./indexes/meta.pkl')
    return df, meta

def process_query(query, pipeline, RAG, model, df, meta):
    prompt, context1, meta1, context2, meta2, context3, meta3 = get_documents(query, pipeline, RAG, df, meta)
    model.config_prompt(system_prompt=GenerationConfig.system_prompt)
    try:
        answer = model.inference(prompt, max_new_tokens=1000)
    except:
        answer = model.inference(prompt)
    return answer, context1, meta1, context2, meta2, context3, meta3


def display_collapsible_docs(docs, doc_type):
    for i, doc in enumerate(docs):
        metadata = doc['metadata']
        header = metadata.get('h1_text', '')
        url = metadata.get('current_url', '')
        section = metadata.get('doc_section', '')
        date = metadata.get('parse_date', '')
        
        page_content = doc['page_content']
        page_content = doc['page_content'].replace('\n', '  \n') 

        doc_title = f"""Фрагмент {i + 1}. {header}  \n Ссылка: {url}  \n Раздел: {section}. Дата парсинга: {date}  \n"""
        content = f"{doc_title}{page_content}"
        with st.expander(f"{doc_type} №{i + 1}", expanded=False):
            st.markdown(content)


def display_chat_message(content, user, avatar):
    st.chat_message(user, avatar=avatar).markdown(content)


def main():
    image_path = './icons/Frame 5.png'
    image_path_mis = './icons/wrLf5yaGC6ng4XME70w6Z.webp'
#     image_path_logo = './rustore-icon.svg'
#     st.set_page_config(page_title="Поддержка RuStore", page_icon=image_path_logo)
    st.title("Поддержка RuStore")

    solar, giga, pipeline, RAG = load_model()
    df, meta = load_df()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Введите ваш вопрос"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.spinner("Получение ответа GigaChat Pro"):
            answer, context1, meta1, context2, meta2, context3, meta3 = process_query(prompt, pipeline, RAG, giga, df, meta)
            st.session_state.messages.append({"role": "assistant", "content": answer})

            docs = [{"metadata": meta1, "page_content": context1}, {"metadata": meta2, "page_content": context2}, {"metadata": meta3, "page_content": context3}]
            display_collapsible_docs(docs, "Документ")
            display_chat_message(f"#### Ответ GigaChat \n{answer}", "assistant", avatar=image_path)
            
        with st.spinner("Получение ответа Mistral"):
            answer, context1, meta1, context2, meta2, context3, meta3 = process_query(prompt, pipeline, RAG, solar, df, meta)
            st.session_state.messages.append({"role": "assistant", "content": answer})

            display_chat_message(f"#### Ответ Mistral \n{answer}", "assistant", avatar=image_path_mis)

if __name__ == "__main__":
    main()
