from transformers import CLIPModel, CLIPProcessor, CLIPVisionModel, CLIPTextModel, CLIPTextConfig,CLIPVisionConfig
from PIL import Image
import torch
import requests
from typing import List

class Image_Embeddings():

    def embedd_images(self,image_path: List[str]):
        config = CLIPVisionConfig(hidden_size=768,intermediate_size=3072,projection_dim=512, num_hidden_layers=12, num_attention_heads=12, num_channels=3,image_size=224, patch_size=32, hidden_act="quick_gelu", layer_norm_eps=0.00001, attention_dropout=0, initializer_range=0.02, initializer_factor=1)
        model = CLIPVisionModel(config).from_pretrained("openai/clip-vit-base-patch32")
        processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        path_list=[]
        for path in image_path:
            if path.__contains__('http'):
                path_list.append(Image.open(requests.get(path, stream=True).raw))
            else:
                path_list.append(Image.open(path))
        

        inputs = processor(images=path_list, return_tensors="pt")
        with torch.no_grad():
            outputs = model(**inputs)
            image_features = outputs.pooler_output
        
        #convert the tensor to a NumPy array
        vector_result = image_features.numpy().flatten()
        return vector_result
        


    def embedd_text(self,texts:List[str]):
        config = CLIPTextConfig(vocab_size=49408, hidden_size=512, intermediate_size=2048, projection_dim=512,num_hidden_layers=12, num_attention_heads=8,max_position_embeddings=77,hidden_act="quick_gelu", layer_norm_eps=0.00001,attention_dropout=0,initializer_range=0.02, initializer_factor=1, pad_token_id=1, bos_token_id=49406,eos_token_id=49407)
        model = CLIPTextModel(config).from_pretrained("openai/clip-vit-base-patch32")
        processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        text_list=[]
        for text in texts:
            text_list.append(text)
        
        inputs = processor(text=text_list,padding=True, return_tensors="pt")
        with torch.no_grad():
            outputs = model(**inputs)
            text_features = outputs.pooler_output
        
        vector_result = text_features.numpy().flatten()
        return vector_result
    


    def embedd_image_and_text(self,image_path:List[str], texts:List[str]):
        model=CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

        path_list=[]
        for path in image_path:
            if path.__contains__('http'):
                path_list.append(Image.open(requests.get(path, stream=True).raw))
            else:
                path_list.append(Image.open(path))
        

        text_list=[]
        for text in texts:
            text_list.append(text)

        inputs = processor(text=text_list, images=path_list, return_tensors="pt", padding=True)

        with torch.no_grad():
            outputs = model(**inputs)
            image_features = outputs.image_embeds
            text_features = outputs.text_embeds

            image_vector_result = image_features.numpy().flatten()
            text_vector_result = text_features.numpy().flatten()
            return image_vector_result
            