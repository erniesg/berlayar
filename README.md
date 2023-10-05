# berlayar.ai
Hire your own team of generative agents for marketing and software development, all you gotta do is prompt. Find your niche and build an audience, turn an idea into a feature for iteration – anytime, anywhere in the world.

## Meet Your Round-the-Clock Team

* Arthur: a tireless librarian and researcher who will build up knowledge and market intelligence for easy retrieval
* Bertrand: go from prompt-to-publish
* Kay: prompt-to-feature
* Ching Shih: router and orchestrator

## Instalation

### Embedding Image or Text using CLIP

- clone the project branch embedding_using_clip
- set your python path `export PYTHONPATH="${PYTHONPATH}:/path/to/berlayar"`
- `pip install pytest`
- run the test to make sure everything works fine and all necessary plug in has been installed
- `python -m pytest tests/integration/functional_image_embeddings.py`

### How to Use Embedding Image or Text using CLIP

- create a new file
- this is example code on using single image embedding
```
from src.models.image_embeddings import Image_Embeddings

image_embedd = Image_Embeddings()
single_image = image_embedd.embedd_images(["path/link to image 1"])
print(single_image)
```

- this is example code on using image embedding for batch of image
```
from src.models.image_embeddings import Image_Embeddings

image_embedd = Image_Embeddings()
list_of_images = ["path/link to image 1","path/link to image 2", "path/link to image 3"]
batch_image = image_embedd.embedd_images(list_of_images)
print(batch_image)
```

- this is example code on using single text embedding
```
from src.models.image_embeddings import Image_Embeddings

image_embedd = Image_Embeddings()
single_text = image_embedd.embedd_text(["this is single text"])
print(single_text)

```

- this is example code on using batch of text embedding
```
from src.models.image_embeddings import Image_Embeddings

image_embedd = Image_Embeddings()
batch_text = image_embedd.embedd_text(["Your text 1","Your text 2","Your text 3","Your text 4"])
print(batch_text)

```

### Reference
To read more about CLIP Model and configuration you can visit link below :

🤗[Hugginggface CLIP](https://huggingface.co/docs/transformers/v4.33.3/en/model_doc/clip#transformers.CLIPTextConfig)
