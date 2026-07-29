from typing import List
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from langchain_core.documents import Document


class LangChainChunker:
    """
    Header-aware chunker using LangChain text splitters.
    Splits markdown by headings (#, ##, ###) followed by RecursiveCharacterTextSplitter.
    """

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 80):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        # Headers to split by
        self.headers_to_split_on = [
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
        ]
        self.header_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=self.headers_to_split_on,
            strip_headers=False
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )

    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """
        Splits a list of raw LangChain documents into smaller retrievable chunk Documents.
        """
        chunked_docs = []

        for doc in documents:
            filename = doc.metadata.get("filename", "unknown.md")
            
            # First split by markdown headers
            header_splits = self.header_splitter.split_text(doc.page_content)

            # Preserve source metadata across header splits
            for split in header_splits:
                split.metadata["filename"] = filename
                split.metadata["source"] = filename
                
                # Format section header label
                headers = [v for k, v in split.metadata.items() if k.startswith("Header")]
                sec_header = " > ".join(headers) if headers else "General"
                split.metadata["section_header"] = sec_header

            # Further split long sections using RecursiveCharacterTextSplitter
            sub_splits = self.text_splitter.split_documents(header_splits)
            
            for sub_split in sub_splits:
                # Prepend source tag to page_content for context awareness
                fn = sub_split.metadata.get("filename", "")
                sec = sub_split.metadata.get("section_header", "General")
                sub_split.page_content = f"[{fn} > {sec}]\n{sub_split.page_content}"
                chunked_docs.append(sub_split)

        return chunked_docs
