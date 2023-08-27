from abc import ABC, abstractmethod

class GitRepoSource(DataSource):
    def ingest(self):
        # Logic to clone/pull git repos and filter relevant files.
        pass

    def get_metadata(self):
        # Extract metadata specific to git repositories.
        pass

class PDFSource(DataSource):
    def ingest(self):
        # Logic to ingest PDFs.
        pass

    def get_metadata(self):
        # Extract metadata specific to PDF files.
        pass

class ZipArchiveSource(DataSource):
    def ingest(self):
        # Logic to ingest and unpack ZIP archives.
        pass

    def get_metadata(self):
        # Extract metadata specific to ZIP archives and their contents.
        pass
