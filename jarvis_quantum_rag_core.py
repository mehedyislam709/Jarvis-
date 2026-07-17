import os
import sys
import json
import time
import logging
import math
import uuid
import tempfile
from datetime import datetime
import numpy as np

# Advanced Cognitive & Semantic Vector Database Engines
try:
    import faiss
    from sentence_transformers import SentenceTransformer
    SEMANTIC_SUPPORT = True
except ImportError:
    SEMANTIC_SUPPORT = False
    logging.critical("[FATAL] Core AI dependencies missing. Run: pip install faiss-cpu sentence-transformers")

# Logging configurations
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] (Core Engine) %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("jarvis_quantum_core.log", encoding="utf-8")
    ]
)

# =====================================================================
#         MODULE 1: QUANTUM VECTOR DATABASE & TEMPORAL DECAY
# =====================================================================
class JarvisQuantumMemory:
    """
    An advanced high-dimensional vector space engine featuring temporal decay 
    and cognitive reinforcement algorithms for semantic long-term memory.
    """
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", db_dir: str = "jarvis_quantum_memory"):
        self.db_dir = os.path.abspath(db_dir)
        self.metadata_path = os.path.join(self.db_dir, "quantum_meta.json")
        self.index_path = os.path.join(self.db_dir, "quantum_faiss.bin")
        
        os.makedirs(self.db_dir, exist_ok=True)

        if SEMANTIC_SUPPORT:
            logging.info(f"[Core Init] Booting sentence encoder: {model_name}")
            self.encoder = SentenceTransformer(model_name)
            self.dimension = self.encoder.get_sentence_embedding_dimension()
        else:
            self.encoder = None
            self.dimension = 384

        self.metadata = []
        self.index = None
        self._load_or_build_vault()

    def _load_or_build_vault(self):
        """Restores memory index from file or builds a new multi-dimensional space."""
        if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
            try:
                with open(self.metadata_path, "r", encoding="utf-8") as f:
                    self.metadata = json.load(f)
                if SEMANTIC_SUPPORT:
                    self.index = faiss.read_index(self.index_path)
                logging.info(f"[Database Vault] Successfully restored {len(self.metadata)} relational memories.")
            except Exception as e:
                logging.error(f"[Database Vault] Reconstruction error: {e}. Generating new matrix.")
                self._build_fresh_index()
        else:
            self._build_fresh_index()

    def _build_fresh_index(self):
        self.metadata = []
        if SEMANTIC_SUPPORT:
            # IndexFlatIP + Normalize vectors = Cosine Similarity (More accurate for text)
            self.index = faiss.IndexFlatIP(self.dimension)
            logging.info("[Database Vault] New High-Dimensional Cosine Similarity index established.")

    def save_vault(self):
        """Saves current memory index files to disk using Atomic Writes to prevent corruption."""
        if not SEMANTIC_SUPPORT or self.index is None:
            return
        try:
            # Atomic save for FAISS Index
            temp_index_fd, temp_index_path = tempfile.mkstemp(dir=self.db_dir)
            os.close(temp_index_fd)
            faiss.write_index(self.index, temp_index_path)
            os.replace(temp_index_path, self.index_path)

            # Atomic save for JSON Metadata
            temp_meta_fd, temp_meta_path = tempfile.mkstemp(dir=self.db_dir)
            os.close(temp_meta_fd)
            with open(temp_meta_path, "w", encoding="utf-8") as f:
                json.dump(self.metadata, f, indent=4, ensure_ascii=False)
            os.replace(temp_meta_path, self.metadata_path)

            logging.info("[Database Vault] Secured index structures atomically synced to storage.")
        except Exception as e:
            logging.error(f"[Database Vault] Write-to-disk error: {e}")

    def commit_memory(self, content: str, category: str = "general_cognition", auto_save: bool = True):
        """Embeds memory into vector space with secure normalization and dynamic ID mapping."""
        if not SEMANTIC_SUPPORT or self.index is None or not content.strip():
            return

        timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Vector encoding & L2 Normalization for Cosine Similarity
        vector = self.encoder.encode([content])[0].astype('float32')
        vector_matrix = np.array([vector])
        faiss.normalize_L2(vector_matrix)
        
        self.index.add(vector_matrix)
        
        self.metadata.append({
            "id": str(uuid.uuid4()),
            "faiss_idx": self.index.ntotal - 1,
            "content": content.strip(),
            "category": category,
            "timestamp": timestamp_str,
            "reinforcement_index": 1.0
        })
        
        if auto_save:
            self.save_vault()
        logging.info(f"[Memory Committed] [{category}] Cached: '{content[:50]}...'")

    def retrieve_context(self, query: str, limit: int = 3) -> list:
        """Queries the vector index and applies an optimized temporal decay filter."""
        if not SEMANTIC_SUPPORT or self.index is None or len(self.metadata) == 0:
            return []

        query_vector = self.encoder.encode([query])[0].astype('float32')
        query_matrix = np.array([query_vector])
        faiss.normalize_L2(query_matrix)

        # IndexFlatIP returns Inner Product (Higher is closer/more similar)
        similarities, indices = self.index.search(query_matrix, limit)
        
        matched_memories = []
        now = datetime.now()

        # Quick lookup map for FAISS index to metadata position
        meta_map = {meta["faiss_idx"]: (pos, meta) for pos, meta in enumerate(self.metadata)}

        for idx, pos in enumerate(indices[0]):
            if pos != -1 and pos in meta_map:
                meta_pos, meta = meta_map[pos]
                
                # Dynamic Decay Logic
                mem_time = datetime.strptime(meta["timestamp"], "%Y-%m-%d %H:%M:%S")
                time_difference_days = max((now - mem_time).days, 0) # Handle 0 days safely
                
                # Logarithmic decay formula
                decay_modifier = meta["reinforcement_index"] / math.log(time_difference_days + math.e)
                
                # For Inner Product, we multiply by decay modifier to prioritize strong/fresh items
                adjusted_score = float(similarities[0][idx]) * decay_modifier

                # Reinforce search history
                self.metadata[meta_pos]["reinforcement_index"] += 0.05
                
                matched_memories.append({
                    "content": meta["content"],
                    "category": meta["category"],
                    "timestamp": meta["timestamp"],
                    "similarity_score": float(similarities[0][idx]),
                    "decayed_score": adjusted_score
                })
        
        self.save_vault()
        # Sort descending (Higher decayed score means better/fresher match)
        matched_memories.sort(key=lambda x: x["decayed_score"], reverse=True)
        return matched_memories


# =====================================================================
#             MODULE 2: PERSONAL DOCUMENT INDEXER (RAG)
# =====================================================================
class QuantumDocumentIndexer:
    """RAG Pipeline with enhanced security filters and batch vector injection."""
    def __init__(self, memory_core: JarvisQuantumMemory):
        self.memory = memory_core
        self.allowed_extensions = {'.txt', '.md', '.json', '.log'}

    def generate_sliding_chunks(self, text: str, chunk_size: int = 400, overlap: int = 80) -> list:
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size - overlap):
            chunk_data = " ".join(words[i : i + chunk_size])
            if chunk_data.strip():
                chunks.append(chunk_data)
        return chunks

    def ingest_local_file(self, path: str):
        """Securely reads allowed files and pushes chunks in a single disk-write batch."""
        safe_path = os.path.abspath(path)
        if not os.path.exists(safe_path):
            logging.error(f"[RAG System] File source not found: '{safe_path}'")
            return

        filename = os.path.basename(safe_path)
        _, ext = os.path.splitext(filename)
        
        if ext.lower() not in self.allowed_extensions:
            logging.error(f"[Security Warning] Blocked ingestion of unsupported file type: {ext}")
            return

        try:
            with open(safe_path, "r", encoding="utf-8", errors="ignore") as file:
                raw_data = file.read()

            chunks = self.generate_sliding_chunks(raw_data)
            logging.info(f"[RAG System] Fragmented file '{filename}' into {len(chunks)} nodes.")

            for index, chunk in enumerate(chunks):
                identity_tag = f"File Source: {filename} (Node {index+1})"
                formatted_chunk = f"[{identity_tag}] {chunk}"
                # Disable auto_save for batch operations to maximize I/O performance
                self.memory.commit_memory(formatted_chunk, category="rag_knowledge_base", auto_save=False)
            
            # Save once after the entire batch is committed
            self.memory.save_vault()
            logging.info(f"[RAG System] Ingestion complete. Knowledge node '{filename}' is now online.")
        except Exception as e:
            logging.error(f"[RAG System] Ingestion failure on '{filename}': {e}")


# =====================================================================
#                        MAIN COGNITIVE PORTAL
# =====================================================================
class JarvisCognitionConsole:
    def __init__(self):
        self.memory = JarvisQuantumMemory()
        self.indexer = QuantumDocumentIndexer(self.memory)

    def run_console(self):
        while True:
            print("\n" + "="*60)
            print("        JARVIS QUANTUM INTEGRATION COGNITIVE CORE        ")
            print("="*60)
            print("1. Speak to Jarvis (Commit Dynamic Conversational Memory)")
            print("2. Retrieve Cognitive Matches (RAG Semantic Vector Search)")
            print("3. Ingest Personal Knowledge Document (.txt or .md files)")
            print("4. View All Stored Memories & Temporal Stamps")
            print("5. System Core Shutdown")
            print("-" * 60)
            
            choice = input("Select an option (1-5): ").strip()
            
            if choice == '1':
                raw_input = input("\nEnter Statement: ").strip()
                if raw_input:
                    self.memory.commit_memory(raw_input, category="conversational_interaction")
                    print("\n[Jarvis]: Understood. This memory has been securely stored.")
                    
            elif choice == '2':
                query = input("\nQuery Search Core: ").strip()
                if query:
                    results = self.memory.retrieve_context(query, limit=3)
                    print("\n--- RETRIEVED SEMANTIC CONTEXTS (Ranked by Temporal Decay) ---")
                    if not results:
                        print("No matches detected.")
                    for index, match in enumerate(results, 1):
                        print(f"\n[{index}] Timestamp: {match['timestamp']} (Decayed Score: {match['decayed_score']:.4f})")
                        print(f"    Raw Similarity: {match['similarity_score']:.4f}")
                        print(f"    Data Content: {match['content']}")
                        
            elif choice == '3':
                target_path = input("\nEnter local text file path: ").strip()
                if target_path:
                    if not os.path.exists(target_path):
                        create_prompt = input("Target path not found. Create dummy testing file? (y/n): ").strip().lower()
                        if create_prompt == 'y':
                            with open(target_path, "w", encoding="utf-8") as f:
                                f.write("Today on Saturday, July 18, 2026, the Jarvis AI architecture was updated successfully.")
                            print(f"[System Log] Sample testing file created at: {target_path}")
                    
                    self.indexer.ingest_local_file(target_path)
                    
            elif choice == '4':
                print("\n--- ALL RECORDED SEMANTIC MEMORY LAYERS ---")
                if not self.memory.metadata:
                    print("Cognitive database is empty.")
                for entry in self.memory.metadata:
                    print(f"[{entry['timestamp']}] [FAISS ID: {entry['faiss_idx']}] [{entry['category'].upper()}] (Strength: {entry['reinforcement_index']:.2f}): {entry['content']}")
                    
            elif choice == '5':
                print("\nInitiating secure system shutdown...")
                self.memory.save_vault()
                break


if __name__ == "__main__":
    if not SEMANTIC_SUPPORT:
        sys.exit(1)
        
    core_mainframe = JarvisCognitionConsole()
    core_mainframe.run_console()
