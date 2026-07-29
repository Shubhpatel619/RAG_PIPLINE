import re
from typing import List, Dict, Any


class MarkdownChunker:
    """
    Header-aware chunker for Markdown documents.
    Splits documents into semantic units based on headings while preserving metadata.
    """

    def __init__(self, max_chunk_size: int = 600, overlap: int = 100):
        self.max_chunk_size = max_chunk_size
        self.overlap = overlap

    def chunk_document(self, doc: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Splits a single document dictionary into a list of chunk dictionaries.
        """
        content = doc.get("content", "")
        filename = doc.get("filename", "")
        doc_id = doc.get("doc_id", "")
        doc_title = doc.get("title", "")

        if not content:
            return []

        # Regex to split by markdown headers (# Header, ## Header, ### Header)
        header_pattern = re.compile(r'^(#{1,3}\s+.+)$', re.MULTILINE)
        splits = header_pattern.split(content)

        raw_sections = []
        current_header = doc_title

        i = 0
        while i < len(splits):
            part = splits[i].strip()
            if not part:
                i += 1
                continue

            if header_pattern.match(part):
                current_header = part.lstrip('#').strip()
                # If there's subsequent content for this header
                if i + 1 < len(splits) and not header_pattern.match(splits[i + 1]):
                    body = splits[i + 1].strip()
                    if body:
                        raw_sections.append((current_header, body))
                    i += 2
                else:
                    i += 1
            else:
                raw_sections.append((current_header, part))
                i += 1

        chunks = []
        chunk_idx = 0

        for section_header, section_text in raw_sections:
            # If section text is under max_chunk_size, keep as single chunk
            if len(section_text) <= self.max_chunk_size:
                chunk_id = f"{doc_id}_chunk_{chunk_idx}"
                chunks.append({
                    "chunk_id": chunk_id,
                    "doc_id": doc_id,
                    "filename": filename,
                    "title": doc_title,
                    "section_header": section_header,
                    "text": f"[{filename} > {section_header}]\n{section_text}"
                })
                chunk_idx += 1
            else:
                # Split longer section into overlapping sub-chunks by line or word
                words = section_text.split()
                sub_chunks = []
                start = 0
                step = max(1, self.max_chunk_size // 6 - self.overlap // 6)
                
                while start < len(words):
                    end = min(len(words), start + (self.max_chunk_size // 6))
                    chunk_words = words[start:end]
                    sub_chunks.append(" ".join(chunk_words))
                    if end >= len(words):
                        break
                    start += step

                for sub_text in sub_chunks:
                    chunk_id = f"{doc_id}_chunk_{chunk_idx}"
                    chunks.append({
                        "chunk_id": chunk_id,
                        "doc_id": doc_id,
                        "filename": filename,
                        "title": doc_title,
                        "section_header": section_header,
                        "text": f"[{filename} > {section_header}]\n{sub_text}"
                    })
                    chunk_idx += 1

        return chunks

    def chunk_documents(self, docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Chunks multiple documents."""
        all_chunks = []
        for doc in docs:
            all_chunks.extend(self.chunk_document(doc))
        return all_chunks
