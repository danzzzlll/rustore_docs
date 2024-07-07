import streamlit as st
import os
from update_docs.split_docs import split
from update_docs.parse_json import parse
from update_docs.update import update_indexes

def load_page2():
    st.title("Обновление документации")
    st.write("Для обновления файлов нажмите на кнопку 'Обновить документацию'")

    # Button to update documents
    if st.button("Обновить документацию"):
        with st.spinner("Обрабатываем JSON файлы..."):
            parse()
        st.success("Documents updated successfully.")
        with st.spinner("Разделяем документы на фрагменты..."):
            split()
        st.success("Documents splitted successfully.")
        with st.spinner("Обновляем индексы..."):
            update_indexes()
        st.success("Indexes updates successfully.")
            

    # Example content for the second page
#     st.markdown("""
#     ## Additional Information
#     Here you can provide more information related to your app.
#     """)

# Replace 'path_to_your_script.py' with the actual path to your script
