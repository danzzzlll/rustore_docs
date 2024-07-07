from utils.ranking import  *

def get_documents(query, existing_pipeline, RAG, content_old, meta):
    raw_results = existing_pipeline.query(query, k=20)
    seq = {i['content']: i['index'] for i in raw_results}
    documents_as_strings = [i['content'] for i in raw_results] # поиск делаем только по пассажу
    contents = RAG.rerank(query=query, documents=documents_as_strings, k=5)
    indexes = [seq.get(elem['content']) for elem in contents]
    
    context1 = content_old[indexes[0]]
    meta1 = meta[indexes[0]]
    
    context2 = content_old[indexes[1]]
    meta2 = meta[indexes[1]]
    
    context3 = content_old[indexes[2]]
    meta3 = meta[indexes[2]]
    
    prompt = f"""
        Вопрос:{query}
        Ответь на вопрос, используя контекст
        '{context1}. Ссылка: {meta1.get('current_url', '-')}',
        '{context2}. Ссылка: {meta2.get('current_url', '-')}',
        '{context3}. Ссылка: {meta3.get('current_url', '-')}'
        Ответ:
        
    """
    return prompt, context1, meta1, context2, meta2, context3, meta3