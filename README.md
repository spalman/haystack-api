# haystack-API
A simple REST API based on [FastAPI](https://fastapi.tiangolo.com/) for [Haystack](https://haystack.deepset.ai) to:

-   search answers in texts ([extractive QA](https://github.com/deepset-ai/haystack/blob/master/rest_api/controller/search.py))
-   semantic search in texts

Docker image is also available at [DockerHub](https://hub.docker.com/r/spalman/qa-api). 

## How to use
Application using already precomputed **Retrievers** and **Embeddings** (stored in SQLite).
1. For each precomputed dataset upload next files: **retriever.pt.zip, faiss.index, haystack_faiss.db**. Files downloaded from Google Drive via ID, so each file must be shared with anyone with the link.
**Link example:**
`https://drive.google.com/file/d/1dI0LZ9ylqTIh916RYGRTRw00uEWR/view?usp=sharing`  
Where ID is `1dI0LZ9ylqTIh916RYGRTRw00uEWR`.<br/>
To check downloaded and ready to use models: `curl -X 'GET http://localhost:8000/datasets -H 'accept: application/json'`
2. After all files successfuly uploaded, there are two pipelines availeble: 
    - **QA** 
    ```sh
        curl -X 'POST'  http://localhost:8000/models/{DATASET-NAME}/doc-qa'` \  
        -H 'accept: application/json' \
        -H 'Content-Type: application/json' \
        -d '{
        "questions": ["QUESTION"],
        "top_k_reader": 5,
        "top_k_retriever": 5
        }
    ```
    `top_k_retriever`: identifies the top-k candidates documents for a given query from a large collection of documents.
    `top_k_reader`: The reader takes multiple passages of text as input and returns top-k answers.
    - **Semantic Search**.
    ```sh
    curl -X 'POST' \
      'http://localhost:8000/models/{DATASET-NAME}/semanticsearch' \
      -H 'accept: application/json' \
      -H 'Content-Type: application/json' \
      -d '{
      "questions": [
        "string"
          ],
          "top_k_reader": 5,
          "top_k_retriever": 5
        }
    ```
Test data can be found here: [Melanin-NLP](https://drive.google.com/drive/folders/1VmiDQmgnbr9BKhHPcJKZl9t7TsSW1PPq?usp=sharing)
