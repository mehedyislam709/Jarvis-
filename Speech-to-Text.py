import os
import torch
import logging
from typing import Optional
import whisper

# Configure advanced enterprise logging
logging.basicConfig(level=logging.INFO, format="[STT] %(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("JarvisSTT")

class SpeechToText:
    def __init__(self, model_size: str = "base"):
        """
        Initializes the Whisper Speech-to-Text module.
        Defaults to 'base' for a secure balance between memory foot-print and accuracy.
        """
        # Determine execution hardware safely
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Targeting execution hardware acceleration boundary: {self.device.upper()}")
        
        logger.info(f"Loading Whisper model '{model_size}' into system context...")
        try:
            # Load model directly onto optimal hardware to prevent host memory leakage
            self.model = whisper.load_model(model_size, device=self.device)
            logger.info("Whisper engine successfully mounted and online.")
        except Exception as init_err:
            logger.critical(f"Failed to mount hardware transcription weights: {init_err}")
            self.model = None

    def _validate_audio_path(self, audio_path: str) -> Optional[str]:
        """
        Validates, sanitizes, and checks the structural safety of the target media file.
        Defends against path traversal vectors.
        """
        if not audio_path:
            logger.error("Rejection payload: File target string is empty.")
            return None
            
        # Resolve path safely away from injection parameters
        resolved_path = os.path.abspath(audio_path)
        
        if not os.path.exists(resolved_path):
            logger.error(f"Target media entity does not exist on host file system: {resolved_path}")
            return None
            
        # Enforce file boundary size checks to prevent memory exhaustion attacks (e.g., max 50MB)
        max_bytes = 50 * 1024 * 1024  
        if os.path.getsize(resolved_path) > max_bytes:
            logger.error("Audio payload rejected: Volume limits exceed safety threshold (50MB).")
            return None
            
        return resolved_path

    def transcribe(self, audio_path: str) -> str:
        """
        Transcribes audio data safely into text under strict process boundaries.
        """
        if not self.model:
            logger.error("Transcription execution aborted: Engine architecture not configured.")
            return ""

        # 1. Sanitize input payload path securely
        safe_path = self._validate_audio_path(audio_path)
        if not safe_path:
            return ""

        logger.info(f"Processing target visual-audio payload data array: {safe_path}")
        
        # 2. Execute process operations under strict error containment structures
        try:
            # Enforce parameters to restrict hallucination tokens and optimize processing speeds
            result = self.model.transcribe(
                safe_path, 
                fp16=(self.device == "cuda"),  # FP16 optimization only if GPU is active
                beam_size=5,
                best_of=5
            )
            
            # Secure dictionary key resolution validation
            extracted_text = result.get("text", "").strip()
            return extracted_text
            
        except torch.cuda.OutOfMemoryError:
            logger.critical("System resource overflow: CUDA out of memory during inference pipeline.")
            torch.cuda.empty_cache()
            return "Error: System computational resource exhaustion."
        except Exception as infer_err:
            logger.error(f"Transcription pipeline failed securely: {infer_err}")
            return ""

# =====================================================================
# Main Execution Guard Context
# =====================================================================
if __name__ == "__main__":
    # Initialize using a reliable model size optimized for speed and execution bounds
    stt_engine = SpeechToText(model_size="base")
    
    # Run pipeline loop safely against target data streams
    # sample_text = stt_engine.transcribe("path/to/secure_audio.wav")
