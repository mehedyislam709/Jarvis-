import os
import logging
import uuid
import shutil
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, HTTPException
from PIL import Image
import pytesseract

# Configure Secure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s | [OCR-SERVICE] | %(levelname)s | %(message)s")

app = FastAPI(title="Jarvis OCR Service", version="2.0.0")

# Security Configuration: Define strict paths and limits
UPLOAD_DIR = Path("./jarvis_vault/ocr_temp")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB Limit

@app.post("/process_screen")
async def process_screen(file: UploadFile = File(...)):
    """Processes screen captures with memory safety and strict validation."""
    
    # 1. Validate File Extension
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=415, detail="Unsupported file format.")

    # 2. Secure File Handling (Using UUID to prevent collisions & traversal)
    file_id = f"{uuid.uuid4()}{ext}"
    file_path = UPLOAD_DIR / file_id
    
    try:
        # Save file with size check
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="File too large.")
            
        with open(file_path, "wb") as buffer:
            buffer.write(content)
        
        # 3. OCR Processing
        logging.info(f"Processing OCR for file: {file_id}")
        img = Image.open(file_path)
        text = pytesseract.image_to_string(img)
        
        return {"status": "success", "text": text.strip()}

    except Exception as e:
        logging.error(f"OCR Pipeline Failure: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal processing error.")
        
    finally:
        # 4. Atomic Cleanup (Ensures file is removed even if OCR fails)
        if file_path.exists():
            os.remove(file_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000)
