# legal-information-retrieval
An NLP-driven web application using Flask and Sentence Transformers (all-MiniLM-L6-v2) to semantically map user complaints to relevant Indian legal acts.
# Legal Information Retrieval System for Indian Laws

## 📌 Project Overview
An AI and NLP-driven assistance platform designed to analyze user complaints and map them semantically to the correct Indian legal acts. This project simplifies legal lookups for common citizens using state-of-the-art transformer models.

## 🛠️ Technical Stack
* **Backend Framework:** Python, Flask
* **Machine Learning & NLP:** SentenceTransformers (`all-MiniLM-L6-v2`), PyTorch, Cosine Similarity
* **Database:** SQLite3
* **Frontend:** HTML, CSS, JavaScript

## 🚀 Core Features
* **Semantic Search:** Uses vector embeddings to find the best matching legal act based on context rather than just keyword matching.
* **Multilingual Translation:** Integrated with `deep-translator` to support localized user input.
* **Custom Virtual Keyboard:** Includes a built-in Tamil keyboard layout for seamless regional language support.
