import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import torch
import clip
from PIL import Image

# =========================
# Load CLIP model once
# =========================
device = "cuda" if torch.cuda.is_available() else "cpu"

model, preprocess = clip.load("ViT-B/32", device=device)


# =========================
# Feature extraction (CLIP)
# =========================
def extract_features(img_path):

    image_input = preprocess(Image.open(img_path).convert("RGB")).unsqueeze(0).to(device)

    with torch.no_grad():
        features = model.encode_image(image_input)

    # Normalize for better cosine similarity stability
    features = features / features.norm(dim=-1, keepdim=True)

    return features.cpu().numpy().flatten()


# =========================
# Similar image search
# =========================
def find_similar_image(uploaded_image_path, portfolios):

    uploaded_features = extract_features(uploaded_image_path)

    best_match = None
    highest_similarity = -1  # safer than 0

    for portfolio in portfolios:

        try:

            if not portfolio.image:
                continue

            portfolio_features = extract_features(portfolio.image.path)

            similarity = cosine_similarity(
                [uploaded_features],
                [portfolio_features]
            )[0][0]

            if similarity > highest_similarity:
                highest_similarity = similarity
                best_match = portfolio

        except Exception:
            continue

        # Reject weak matches
        # SIMILARITY_THRESHOLD = 0.75

        # if highest_similarity < SIMILARITY_THRESHOLD:
        #     return None

    return best_match