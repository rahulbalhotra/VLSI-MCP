import sqlite3
import os
import json
from typing import List, Dict, Any, Optional
from services.embedding_service import EmbeddingService
import numpy as np

class RegressionService:
    def __init__(self, db_path: str, embedding_service: EmbeddingService):
        self.db_path = db_path
        self.emb = embedding_service
        self._init_db()

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Table for regression runs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS regression_runs (
                run_id TEXT PRIMARY KEY,
                timestamp TEXT,
                commit_hash TEXT,
                total_properties INTEGER,
                passed_properties INTEGER,
                failed_properties INTEGER,
                vacuous_properties INTEGER,
                runtime_seconds REAL,
                status TEXT,
                failures_json TEXT
            )
        """)

        # Table for bug database
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bugs (
                bug_id TEXT PRIMARY KEY,
                summary TEXT,
                module TEXT,
                root_cause TEXT,
                fix_details TEXT,
                embedding BLOB
            )
        """)
        conn.commit()
        conn.close()

    def log_run(
        self,
        run_id: str,
        timestamp: str,
        commit_hash: str,
        total: int,
        passed: int,
        failed: int,
        vacuous: int,
        runtime: float,
        status: str,
        failures: List[str]
    ):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """INSERT OR REPLACE INTO regression_runs 
            (run_id, timestamp, commit_hash, total_properties, passed_properties, failed_properties, vacuous_properties, runtime_seconds, status, failures_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (run_id, timestamp, commit_hash, total, passed, failed, vacuous, runtime, status, json.dumps(failures))
        )
        conn.commit()
        conn.close()

    def add_bug(self, bug_id: str, summary: str, module: str, root_cause: str, fix_details: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Calculate semantic embedding
        vector = self.emb.get_embedding(summary + " " + root_cause)
        vector_blob = np.array(vector, dtype=np.float32).tobytes()

        cursor.execute(
            "INSERT OR REPLACE INTO bugs (bug_id, summary, module, root_cause, fix_details, embedding) VALUES (?, ?, ?, ?, ?, ?)",
            (bug_id, summary, module, root_cause, fix_details, vector_blob)
        )
        conn.commit()
        conn.close()

    def search_bug(self, query: str, top_k: int = 2) -> List[Dict[str, Any]]:
        query_vector = self.emb.get_embedding(query)
        query_arr = np.array(query_vector, dtype=np.float32)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT bug_id, summary, module, root_cause, fix_details, embedding FROM bugs")
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return []

        results = []
        for bug_id, summary, module, root_cause, fix, emb_blob in rows:
            emb_arr = np.frombuffer(emb_blob, dtype=np.float32)
            # Cosine similarity
            dot = np.dot(query_arr, emb_arr)
            norm_q = np.linalg.norm(query_arr)
            norm_e = np.linalg.norm(emb_arr)
            similarity = float(dot / (norm_q * norm_e)) if norm_q > 0 and norm_e > 0 else 0.0

            results.append({
                "bug_id": bug_id,
                "summary": summary,
                "module": module,
                "root_cause": root_cause,
                "fix_details": fix,
                "score": similarity
            })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    def get_regression_summary(self, run_id_a: str, run_id_b: str) -> Dict[str, Any]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT run_id, status, failures_json, runtime_seconds FROM regression_runs WHERE run_id IN (?, ?)", (run_id_a, run_id_b))
        rows = cursor.fetchall()
        conn.close()

        run_data = {r[0]: {"status": r[1], "failures": json.loads(r[2]), "runtime": r[3]} for r in rows}
        
        if run_id_a not in run_data or run_id_b not in run_data:
            return {"error": f"One or both run IDs not found: {run_id_a}, {run_id_b}"}

        a = run_data[run_id_a]
        b = run_data[run_id_b]

        failures_a = set(a["failures"])
        failures_b = set(b["failures"])

        new_failures = list(failures_b - failures_a)
        resolved_failures = list(failures_a - failures_b)
        runtime_diff = b["runtime"] - a["runtime"]

        return {
            "runs_compared": [run_id_a, run_id_b],
            "new_failures": new_failures,
            "resolved_failures": resolved_failures,
            "runtime_diff_seconds": runtime_diff,
            "trends": {
                "status_change": f"{a['status']} -> {b['status']}",
                "failure_count_change": f"{len(failures_a)} -> {len(failures_b)}"
            }
        }

    def populate_mock_data(self):
        """
        Populates mock bugs and runs.
        """
        # Populate runs
        self.log_run("run_2026_07_17", "2026-07-17T02:00:00", "a4b123d", 10, 8, 2, 0, 15.3, "failed", ["p_fifo_overflow", "p_axi_handshake"])
        self.log_run("run_2026_07_18", "2026-07-18T02:00:00", "f7e890c", 10, 9, 1, 0, 14.1, "failed", ["p_fifo_overflow"])

        # Populate bugs
        self.add_bug(
            "BUG-001",
            "FIFO overflow on back-to-back write transactions",
            "fifo",
            "The full signal is asserted one cycle late when back-to-back writes occur while the FIFO has exactly one slot left.",
            "Add lookahead check to assert full signal when count == DEPTH - 1 and write is active without read."
        )
        self.add_bug(
            "BUG-002",
            "AXI ready signal asserted without valid address",
            "axi_slave",
            "The slave asserted AWREADY immediately on reset, violating the handshake protocol.",
            "Modify state machine to keep AWREADY deasserted until AWVALID is seen."
        )
