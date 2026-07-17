import os
import sys
import json
import time
import logging
import math
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
        self.db_dir = db_dir
        self.metadata_path = os.path.join(db_dir, "quantum_meta.json")
        self.index_path = os.path.join(db_dir, "quantum_faiss.bin")
        
        if not os.path.exists(self.db_dir):
            os.makedirs(self.db_dir)

        # High-Performance Embedding Encoder
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
            # We use FlatL2 for precise Euclidean distance calculation in vector space
            self.index = faiss.IndexFlatL2(self.dimension)
            logging.info("[Database Vault] New High-Dimensional FAISS index established.")

    def save_vault(self):
        """Saves current memory index files to disk securely."""
        if not SEMANTIC_SUPPORT or self.index is None:
            return
        try:
            faiss.write_index(self.index, self.index_path)
            with open(self.metadata_path, "w", encoding="utf-8") as f:
                json.dump(self.metadata, f, indent=4, ensure_ascii=False)
            logging.info("[Database Vault] Secured index structures synced to hard-drive storage.")
        except Exception as e:
            logging.error(f"[Database Vault] Write-to-disk error: {e}")

    def commit_memory(self, content: str, category: str = "general_cognition"):
        """
        Embeds a raw memory context into the vector space and attaches
        importance metrics and temporal timestamps.
        """
        if not SEMANTIC_SUPPORT or self.index is None:
            return

        timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Calculate high-dimensional vector embeddings
        vector = self.encoder.encode([content])[0].astype('float32')
        vector_matrix = np.array([vector])
        
        self.index.add(vector_matrix)
        self.metadata.append({
            "id": len(self.metadata),
            "content": content,
            "category": category,
            "timestamp": timestamp_str,
            "reinforcement_index": 1.0  # Fresh memories start with standard cognitive strength
        })
        self.save_vault()
        logging.info(f"[Memory Committed] [{category}] Successfully cached: '{content[:50]}...'")

    def retrieve_context(self, query: str, limit: int = 3) -> list:
        """
        Queries the vector index for semantic matches and applies a 
        temporal decay filter (newer memories carry higher priority).
        """
        if not SEMANTIC_SUPPORT or self.index is None or len(self.metadata) == 0:
            return []

        # Vector conversion of query
        query_vector = self.encoder.encode([query])[0].astype('float32')
        query_matrix = np.array([query_vector])

        # Nearest Neighbors search inside FAISS
        distances, indices = self.index.search(query_matrix, limit)
        
        matched_memories = []
        now = datetime.now()

        for idx, pos in enumerate(indices[0]):
            if pos != -1 and pos < len(self.metadata):
                meta = self.metadata[pos]
                
                # Dynamic Decay Logic
                mem_time = datetime.strptime(meta["timestamp"], "%Y-%m-%d %H:%M:%S")
                time_difference_days = max((now - mem_time).days, 1)
                
                # Math decay formula: decay = original_strength / ln(days_passed + e)
                decay_modifier = meta["reinforcement_index"] / math.log(time_difference_days + math.e)
                adjusted_score = float(distances[0][idx]) * (2.0 - decay_modifier)

                # Reinforce search history (Slightly bump weight for repeatedly queried memories)
                self.metadata[pos]["reinforcement_index"] += 0.1
                
                matched_memories.append({
                    "content": meta["content"],
                    "category": meta["category"],
                    "timestamp": meta["timestamp"],
                    "original_distance": float(distances[0][idx]),
                    "decayed_score": adjusted_score
                })
        
        self.save_vault()
        # Sort memories to bring chronologically optimal matches first
        matched_memories.sort(key=lambda x: x["decayed_score"])
        return matched_memories


# =====================================================================
#             MODULE 2: PERSONAL DOCUMENT INDEXER (RAG)
# =====================================================================
class QuantumDocumentIndexer:
    """
    RAG Pipeline: Reads local file directories, parses textual components,
    breaks them down into semantic chunks, and indexes them into Vector Memory.
    """
    def __init__(self, memory_core: JarvisQuantumMemory):
        self.memory = memory_core

    def generate_sliding_chunks(self, text: str, chunk_size: int = 400, overlap: int = 80) -> list:
        """Splits raw text files into overlapping segments to avoid missing context."""
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size - overlap):
            chunk_data = " ".join(words[i : i + chunk_size])
            if chunk_data.strip():
                chunks.append(chunk_data)
        return chunks

    def ingest_local_file(self, path: str):
        """Reads file data and pushes them into Jarvis's cognitive vectors."""
        if not os.path.exists(path):
            logging.error(f"[RAG System] File source not found: '{path}'")
            return

        filename = os.path.basename(path)
        try:
            with open(path, "r", encoding="utf-8") as file:
                raw_data = file.read()

            chunks = self.generate_sliding_chunks(raw_data)
            logging.info(f"[RAG System] Fragmented file '{filename}' into {len(chunks)} contextual nodes.")

            for index, chunk in enumerate(chunks):
                identity_tag = f"File Source: {filename} (Node {index+1})"
                formatted_chunk = f"[{identity_tag}] {chunk}"
                self.memory.commit_memory(formatted_chunk, category="rag_knowledge_base")
                
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
        """CLI Terminal controller running concurrently with the UI."""
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
                    print("\n[Jarvis]: Understood. This memory has been securely stored in the database.")
                    
            elif choice == '2':
                query = input("\nQuery Search Core: ").strip()
                if query:
                    results = self.memory.retrieve_context(query, limit=3)
                    print("\n--- RETRIEVED SEMANTIC CONTEXTS (Ranked by Temporal Decay) ---")
                    if not results:
                        print("No matches detected.")
                    for index, match in enumerate(results, 1):
                        print(f"\n[{index}] Timestamp: {match['timestamp']} (Decayed Score: {match['decayed_score']:.4f})")
                        print(f"    Data Content: {match['content']}")
                        
            elif choice == '3':
                target_path = input("\nEnter local text file path: ").strip()
                if target_path:
                    # Self-creating sample logic for quick environment verification
                    if not os.path.exists(target_path):
                        create_prompt = input("Target path not found. Create dummy testing file? (y/n): ").strip().lower()
                        if create_prompt == 'y':
                            with open(target_path, "w", encoding="utf-8") as f:
                                f.write("Today on Friday, July 17, 2026, the Jarvis AI completed its major architecture transition. "
                                        "The new cognitive system now utilizes quantum vector databases.")
                            print(f"[System Log] Sample testing file created at: {target_path}")
                    
                    self.indexer.ingest_local_file(target_path)
                    
            elif choice == '4':
                print("\n--- ALL RECORDED SEMANTIC MEMORY LAYERS ---")
                if not self.memory.metadata:
                    print("Cognitive database is empty.")
                for entry in self.memory.metadata:
                    print(f"[{entry['timestamp']}] [{entry['category'].upper()}] (Strength: {entry['reinforcement_index']:.1f}): {entry['content']}")
                    
            elif choice == '5':
                print("\nInitiating secure system shutdown...")
                self.memory.save_vault()
                break


# =====================================================================
#                         SYSTEM MAIN START
# =====================================================================
if __name__ == "__main__":
    if not SEMANTIC_SUPPORT:
        sys.exit(1)
        
    core_mainframe = JarvisCognitionConsole()
    core_mainframe.run_console()
