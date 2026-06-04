import pandas as pd
from sentence_transformers import SentenceTransformer, util
import torch

# ---------------- LOAD DATASET ---------------- #

df = pd.read_csv("dataset.csv")
df.columns = df.columns.str.strip()

df = df.dropna(subset=[
    "Act Name",
    "Typical Complaints / Requests",
    "Authority to Approach"
])

# Combine text for semantic search
df["combined_text"] = (
    df["Act Name"].astype(str) + " " +
    df["Typical Complaints / Requests"].astype(str)
)

# ---------------- LOAD MODEL ---------------- #

model = SentenceTransformer("all-MiniLM-L6-v2")

# Encode dataset ONCE (performance optimization)
dataset_embeddings = model.encode(
    df["combined_text"].tolist(),
    convert_to_tensor=True
)

# ---------------- CATEGORY SYSTEM ---------------- #

CATEGORIES = [
    "Cyber Crime",
    "Women Safety",
    "Consumer Complaint",
    "Property Dispute",
    "Banking Fraud",
    "Employment Issue",
    "Police Complaint",
    "Harassment",
    "Land Issue",
    "Financial Dispute"
]

# Encode categories once
category_embeddings = model.encode(
    CATEGORIES,
    convert_to_tensor=True
)


def predict_category(user_issue):
    user_embedding = model.encode(user_issue, convert_to_tensor=True)
    similarities = util.cos_sim(user_embedding, category_embeddings)[0]
    best_index = similarities.argmax().item()
    return CATEGORIES[best_index]


# ---------------- MAIN PREDICTION ---------------- #

def predict_act(user_issue):

    # Step 1: Generate category
    predicted_category = predict_category(user_issue)

    # Step 2: Semantic similarity search
    user_embedding = model.encode(user_issue, convert_to_tensor=True)

    similarities = util.cos_sim(
        user_embedding,
        dataset_embeddings
    )[0]

    best_index = similarities.argmax().item()

    return {
        "category": predicted_category,
        "act": df.iloc[best_index]["Act Name"],
        "authority": df.iloc[best_index]["Authority to Approach"],
        "explanation": df.iloc[best_index]["Typical Complaints / Requests"]
    }
