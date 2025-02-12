__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import pandas as pd
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# 🔹 데이터 로드
df = pd.read_csv("/home/ibmuser03/tala-docker/data/accident_datas.csv")

# 🔹 RAG 모델 로드 (ChromaDB)
persist_directory = "/home/ibmuser03/tala-docker/app/chroma_accidents"
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")  # ✅ 최신 패키지 적용
vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embeddings)  # ✅ 최신 패키지 적용

vectorstore.persist()