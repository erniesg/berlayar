import torch
from typing import Dict, Optional, Tuple

def compute_weighted_embeddings(image_embedding: torch.Tensor, metadata_embedding: Optional[torch.Tensor] = None, metadata_columns: Optional[Dict[str, str]] = None) -> Tuple[torch.Tensor, Dict[str, float]]:
    image_weight = 0.5
    meta_weight = 0.5

    # If there's no metadata, weight image as 1
    if metadata_embedding is None:
        image_weight = 1
        meta_weight = 0
    else:
        # Adjust meta_weight based on filled metadata columns
        filled_meta_cols = len([col for col in metadata_columns.values() if col])
        meta_weight *= filled_meta_cols / len(metadata_columns)
        image_weight = 1 - meta_weight

    if metadata_embedding is None:
        combined_embedding = image_embedding * image_weight
    else:
        combined_embedding = (image_embedding * image_weight) + (metadata_embedding * meta_weight)

    weights = {
        'image_weight': image_weight,
        'metadata_weight': meta_weight
    }

    return combined_embedding, weights

# You can add more functions and logic here as needed for other modalities or more complex scenarios
