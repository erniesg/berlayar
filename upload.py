import csv
import os
from docarray import dataclass
from docarray import Document, DocumentArray
from docarray.typing import Image, Text


@dataclass
class Artwork:
    image: Image
    title: Text
    artist: Text
    dating: Text
    place: Text
    description: Text
    medium: Text

image_folder = 'raw_data/img/artic_topartworks_public'


def convert_to_docarray(filename):
    existing_images = os.listdir(image_folder)

    artworks = DocumentArray()

    with open(filename) as csvfile:
        csv_reader = csv.DictReader(csvfile, delimiter=',')
        for row in csv_reader:
            image_file = f'{row["id"]}.jpg'
            if image_file in existing_images:
                artwork = Artwork(
                    image=f'{image_folder}/{image_file}',
                    title=row['title'],
                    artist=row['artist_title'],
                    dating=row['date_display'],
                    place=row['place_of_origin'],
                    description=row['alt_text'],
                    medium=row['medium_display'],
                )
                doc = Document(artwork)
                artworks.append(doc)

    artworks.save_binary('artic_topartworks_public.docarray')

def push_all():
    da = DocumentArray.load_binary(f'artic_topartworks_public.docarray')
    da.push(name='artic_topartworks_public')


convert_to_docarray('raw_data/csv/artic_topartworks_public.csv')
push_all()