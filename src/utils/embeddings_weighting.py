import torch
from typing import Dict, Optional, Tuple

def compute_weighted_embeddings(image_embedding: torch.Tensor,
                                metadata_embedding: Optional[torch.Tensor] = None,
                                audio_embedding: Optional[torch.Tensor] = None,
                                metadata_columns: Optional[Dict[str, str]] = None) -> Tuple[torch.Tensor, Dict[str, float]]:

    image_weight = 1/3  # Default equal weights for all three modalities
    meta_weight = 1/3
    audio_weight = 1/3

    filled_meta_cols = len([col for col in metadata_columns.values() if col])

    # If there's no metadata and no audio, weight image as 1
    if filled_meta_cols == 0 and audio_embedding is None:
        image_weight = 1
        meta_weight = 0
        audio_weight = 0
    elif filled_meta_cols > 0 and audio_embedding is None:
        meta_weight = (filled_meta_cols / len(metadata_columns)) / 3
        image_weight = 1 - meta_weight
        audio_weight = 0
    elif filled_meta_cols == 0 and audio_embedding is not None:
        image_weight = 0.5
        audio_weight = 0.5
        meta_weight = 0

    combined_embedding = (image_embedding * image_weight)

    if metadata_embedding is not None:
        combined_embedding += (metadata_embedding * meta_weight)

    if audio_embedding is not None:
        combined_embedding += (audio_embedding * audio_weight)

    return combined_embedding, {"image": image_weight, "metadata": meta_weight, "audio": audio_weight}
