import pandas as pd
import joblib
from utils.ranking import MyExistingRetrievalPipeline

def save_file(file, file_name):
    joblib.dump(file, file_name)

def get_df(pikle_file):

    data = joblib.load(pikle_file)

    languages = []
    dates = []
    urls = []
    sections = []
    headers = []
    contents = []
    metas = []

    # Extract data from each Document
    for doc in data:
        languages.append(doc.metadata.get('language', 'ru'))
        dates.append(doc.metadata.get('parse_date', 'date'))
        urls.append(doc.metadata.get('current_url', 'url'))
        sections.append(doc.metadata.get('doc_section', 'doc'))
        headers.append(doc.metadata.get('h1_text', 'head'))
        contents.append(doc.page_content)
        metas.append(doc.metadata)

    # Create DataFrame
    df = pd.DataFrame({
        'Language': languages,
        'Dates': dates,
        'Urls': urls,
        'Meta': metas,
        'Section': sections,
        'Header': headers,
        'Content': contents
    })  

    save_file(df['Meta'].tolist(), './indexes_upd/meta.pkl')
    df['Meta'] = " Parse date: " + df['Dates'] + " Url: " + df['Urls'] + " Section: " + df['Section'] + " Header " + df['Header']
    df['Full_Content'] = df['Header'] + ' ' + df['Content']
    save_file(df['Full_Content'].tolist(), './indexes_upd/content_new.pkl')
    
    return df

def update_indexes():

    df = get_df(pikle_file="./parser/processed_langchain_docs.pkl")

    index_pipeline = MyExistingRetrievalPipeline()
    index_pipeline.index_documents(df, batch_size=512)

    index_pipeline.save_index(index_file_path="./indexes_upd/indexes_cp.index", 
                              map_file_path="./indexes_upd/collection_cp.pkl", 
                              doc_texts_path="./indexes_upd/bm_cp.pkl"
                            )




