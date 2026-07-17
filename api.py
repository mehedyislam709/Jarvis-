from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Message(BaseModel):
    text: str

@app.post("/generate-response")
async def generate_response(message: Message):
    # এখানে আপনার কনভারসেশনাল ইঞ্জিনের কোড যুক্ত করতে হবে
    response_text = f"Received: {message.text}"
    return {"response": response_text}
