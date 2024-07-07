import pandas as pd
from ranking import MyExistingRetrievalPipeline

def name():
    data = pd.read_csv(path_to_csv_data)

    existing_pipeline = MyExistingRetrievalPipeline()
    existing_pipeline.index_documents(data, batch_size=1024)

    index_path = 'path_for_index.index'
    collection_path = 'path_for_collection.pkl'
    bm_path = 'path_for_bm.pkl'

    existing_pipeline.save_index(index_path, collection_path, bm_path)

if __name__ == "__main__":
    main()