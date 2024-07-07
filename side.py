import streamlit as st
import main
import update_documents

image_path_logo = './icons/rustore-icon.svg'
st.set_page_config(page_title="Поддержка RuStore", page_icon=image_path_logo)
st.sidebar.title("Страницы")
page = st.sidebar.radio("Перейти", ["Вопрос поддержке", "Обновление документации"])

if page == "Вопрос поддержке":
    main.main()
elif page == "Обновление документации":
    update_documents.load_page2()
