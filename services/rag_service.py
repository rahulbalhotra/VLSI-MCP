import sqlite3
import json
import os
import numpy as np
from typing import List, Dict, Any, Optional
from services.embedding_service import EmbeddingService

class RAGService:
    def __init__(self, db_path: str, embedding_service: EmbeddingService):
        self.db_path = db_path
        self.emb = embedding_service
        self._init_db()

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # Table for storing documents
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS spec_chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                protocol TEXT,
                document_name TEXT,
                section TEXT,
                content TEXT,
                embedding BLOB
            )
        """)
        conn.commit()
        conn.close()

    def add_chunk(self, protocol: str, document_name: str, section: str, content: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Calculate embedding
        vector = self.emb.get_embedding(content)
        vector_blob = np.array(vector, dtype=np.float32).tobytes()

        cursor.execute(
            "INSERT INTO spec_chunks (protocol, document_name, section, content, embedding) VALUES (?, ?, ?, ?, ?)",
            (protocol, document_name, section, content, vector_blob)
        )
        conn.commit()
        conn.close()

    def search_spec(self, query: str, protocol: Optional[str] = None, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Performs semantic search over protocol chunks.
        """
        query_vector = self.emb.get_embedding(query)
        query_arr = np.array(query_vector, dtype=np.float32)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if protocol:
            cursor.execute("SELECT id, protocol, document_name, section, content, embedding FROM spec_chunks WHERE protocol = ?", (protocol,))
        else:
            cursor.execute("SELECT id, protocol, document_name, section, content, embedding FROM spec_chunks")

        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return []

        results = []
        for r_id, prot, doc, sec, content, emb_blob in rows:
            emb_arr = np.frombuffer(emb_blob, dtype=np.float32)
            # Compute Cosine Similarity
            dot = np.dot(query_arr, emb_arr)
            norm_q = np.linalg.norm(query_arr)
            norm_e = np.linalg.norm(emb_arr)
            similarity = float(dot / (norm_q * norm_e)) if norm_q > 0 and norm_e > 0 else 0.0

            results.append({
                "protocol": prot,
                "document_name": doc,
                "section": sec,
                "content": content,
                "score": similarity
            })

        # Sort by similarity score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    def populate_mock_data(self):
        """
        Populates mock data if database is empty.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM spec_chunks")
        cnt = cursor.fetchone()[0]
        conn.close()

        if cnt > 0:
            return

        mock_data = [
            {
                "protocol": "AXI",
                "document_name": "AMBA_AXI_Spec.pdf",
                "section": "A3.1.1 AXI Write Handshake",
                "content": "A write transaction starts when the master asserts the AWVALID signal and provides the address, control information, and write data. The write transaction completes when the slave asserts BVALID to acknowledge receipt of all write data."
            },
            {
                "protocol": "AXI",
                "document_name": "AMBA_AXI_Spec.pdf",
                "section": "A3.1.2 Handshake dependency",
                "content": "AWVALID must not depend on AWREADY. The master must assert AWVALID without waiting for the slave to assert AWREADY. However, the slave can wait for AWVALID to be asserted before asserting AWREADY."
            },
            {
                "protocol": "APB",
                "document_name": "AMBA_APB_Spec.pdf",
                "section": "B2.1 Operating States",
                "content": "The APB state machine has three states: IDLE, SETUP, and ACCESS. During SETUP, PSEL is asserted and PENABLE is deasserted. In the ACCESS state, both PSEL and PENABLE are asserted."
            },
            {
                "protocol": "PCIe",
                "document_name": "PCIe_Express_Base_5.pdf",
                "section": "4.2.1 Transaction Layer Packets",
                "content": "TLPs are used to communicate transactions between devices. TLP types include Memory Read, Memory Write, Configuration Read, Configuration Write, and Messages. Memory Write is a non-posted transaction."
            }
        ]

        for chunk in mock_data:
            self.add_chunk(chunk["protocol"], chunk["document_name"], chunk["section"], chunk["content"])
