from google.cloud import storage

def make_blob_public(bucket_name, blob_name):
    """Makes a blob publicly accessible."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    blob.make_public()

    print(f"The file {blob_name} is now publicly accessible at {blob.public_url}")

def upload_to_gcs(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to Google Cloud Storage."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    # Make the blob publicly viewable.
    blob.make_public()

    print(f"File {source_file_name} uploaded to {destination_blob_name}.")

    return blob.public_url

def read_file_from_gcs(bucket_name, blob_name):
    """Reads a file from Google Cloud Storage."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    # Download the file's contents as a bytes object
    file_contents = blob.download_as_string()

    return file_contents.decode("utf-8")
