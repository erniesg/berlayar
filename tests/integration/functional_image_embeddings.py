import pytest
import numpy as np
from src.models.image_embeddings import Image_Embeddings

def test_single_image_embeddings():
    image_embedd = Image_Embeddings()
    single_image = image_embedd.embedd_images(["http://images.cocodataset.org/val2017/000000039769.jpg"])
    
    assert single_image is not None, "Embedding single image is failed"
    assert isinstance(single_image,np.ndarray),"Embedding single image is not return vector value"
    
    

def test_batch_image_embeddings():
    image_embedd = Image_Embeddings()
    list_of_images = ["https://img.freepik.com/free-photo/high-angle-man-holding-corn-dog_23-2149929396.jpg?w=1380&t=st=1696179386~exp=1696179986~hmac=6422c2bee3b62388f3ce0b4cb5247eb86604291716b24b026c4b36fefd303ddb",
                      "https://img.freepik.com/free-photo/top-view-food-banquet_23-2149893441.jpg?w=1380&t=st=1696179463~exp=1696180063~hmac=3510d65c8a52d01cff058c260c1aa5cff382c04b94f44669c788ab08acb54fd8",
                      "https://img.freepik.com/free-photo/friends-partying-outdoors-side-view_23-2149412445.jpg?w=1380&t=st=1696179492~exp=1696180092~hmac=456c43c9f15a0be6966006c06bd4687598d851f0a2d527540a8edb5254696f84",
                      "https://img.freepik.com/free-photo/side-view-women-eating-noodles_23-2149734520.jpg?w=1380&t=st=1696179515~exp=1696180115~hmac=ecc804658ce81a8b497437430d9de5aa08dd9212f4805fdb58a3557bad6d69c4"]
    batch_image = image_embedd.embedd_images(list_of_images)
    assert batch_image is not None, "Embedding batch of images is failed"
    assert isinstance(batch_image, np.ndarray), "Embedding batch of images is not return vector"

def test_single_text_embeddings():
    image_embedd = Image_Embeddings()
    single_text = image_embedd.embedd_text(["this is text for testing"])
    assert single_text is not None, "Embedding single text is failed"
    assert isinstance(single_text, np.ndarray),"Embedding Single Text is not return a vector"

def test_batch_text_embeddings():
    image_embedd = Image_Embeddings()
    batch_text = image_embedd.embedd_text(["this is text for testing",
                                            "this is second text",
                                            "this is third text",
                                            "this is the fourth text"])
    assert batch_text is not None, "Embedding single text is failed"
    assert isinstance(batch_text, np.ndarray),"Embedding batch of Text is not return a vector"