# **Crypto Detective - Cryptocurrency Fraud Investigation System** 🕵️‍♂️

This project is a **Retrieval-Augmented Generation (RAG) system** designed for cryptocurrency fraud investigations. It enables investigators to retrieve relevant evidence from case files, analyze blockchain-related fraud, and generate investigation reports using **FastAPI, Qdrant, OpenAI embeddings, and Gradio UI**.

---

## **1. Architecture** 🏗️
### **System Overview**
🔹 **Data Storage**: Case files are stored in `.txt` format and embedded into a **Qdrant vector database**.  
🔹 **Retrieval System**: Uses **text embeddings** (OpenAI) to find similar documents based on queries.  
🔹 **Reranking System**: Assigns confidence scores to retrieved evidence.  
🔹 **Report Generation**: Uses **GPT-4** to summarize findings in a structured investigative report.  
🔹 **UI**: Allows users to interact via **Gradio-based UI**.  

---

## **2. Set Up Conda Environment** 🛠️
1️⃣ Install **Conda** (if not already installed).  
2️⃣ Run the following command to create and activate the environment:

```sh
make setup
```
**What this does:**
- Creates a new virtual environment: `crypto_detective`
- Installs required dependencies (`pip install -r requirements.txt`)
- Sets up environment variables

> **Note:** Activate the environment manually after setup:  
> ```sh
> conda activate crypto_detective
> ```

---

## **3. Setup Qdrant Vector Database (via Docker)** 🛢️
1️⃣ Ensure **Docker** is installed on your system.  
2️⃣ Run the following command to start Qdrant:

```sh
docker run -d --name qdrant -p 6333:6333 qdrant/qdrant
```
This will:
- Pull the latest **Qdrant container** if not already available.
- Run Qdrant on **port 6333** for vector storage and retrieval.

---

## **4. Load Data into Qdrant** 📥
Once Qdrant is running, load case files into the **vector database**:

```sh
make load_data
```

After successful execution, you can inspect stored vectors using the **Qdrant UI**.

![qdrant_ui](/assets/qdrant_ui.png)

---

## **5. Run FastAPI Backend** 🚀
To start the **FastAPI server**, run:

```sh
make fastapi
```
This launches the API service, which handles **query retrieval, reranking, and LLM-based report generation**.

You can access the FastAPI documentation at:

📌 **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)  

📌 **Redoc UI**: [http://localhost:8000/redoc](http://localhost:8000/redoc)  

![fastapi](/assets/fastapi.png)

---

## **6. Run Gradio UI** 🎨
To start the **Gradio web interface**, run:

```sh
make gradio_ui
```

This will launch a **web-based investigation tool**, where users can:
- **Enter queries**
- **View retrieved evidence**
- **See confidence scores**
- **Access the generated investigation report**

![gradio-ui](/assets/gradio-ui.png)

---

## **7. Environment Variables Setup** 🔐
Ensure the following environment variables are set:

```sh
open_api_key: "xxxxxxxxxxx"
embedding_model: "text-embedding-ada-002"
gpt_model: "gpt-4o"
tokenizer: "cl100k_base"

chunk_size: 512
chunk_overlap: 50

top_k: 10
top_rerank: 10
top_k_retrieval: 10  

strategy: "multi-step"
data_dir: "./data/"

rerank_weight_vector: 0.45  
rerank_weight_llm: 0.55 
filter_enabled: true  

logging_file: ./logs/logging_file.log


qdrant_host: "localhost"  
qdrant_port: 6333  
qdrant_collection: "crypto_case_vectors" 
embedding_dim: 1536



aws_access_key_id: "xxxxxxxxx"
aws_secret_access_key: "xxxxxxxxxxxx"
region: "ap-southeast-1"
bucket: "s3://xxxxxxxxxxxx"
```

You can also store these in a `config_example.yaml` file.

---

## **8. Example Queries & Usage**
### **Example Investigation Queries**
- 🔍 `"Find transactions related to the Binance exchange hack in 2024"`
- 🔍 `"Which methods were used to launder stolen funds?"`
- 🔍 `"How was Tornado Cash involved in recent crypto fraud cases?"`

### **Expected Outputs**
- **Relevant case evidence** (retrieved from Qdrant)
- **Confidence scores** for evidence
- **AI-generated report** summarizing findings
- **Downloadable report from S3**










