from typing import List
import base64
from internal.open_ai import valuate_item, OPEN_AI_CLIENT, SHORT_ANSWER_TO_JSON_PROMPT, SHORT_ANSWER_TO_TEXT_PROMPT

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from openai import OpenAI

app = FastAPI()

PROMPT_TO_AI = SHORT_ANSWER_TO_TEXT_PROMPT

# app.mount("/static", StaticFiles(directory="static"), name="static")
# app.mount("/", StaticFiles(directory="static", html=True), name="static")

@app.get("/")
def read_index():
    return FileResponse("static/multiupload.html")

@app.post("/upload-images")
async def upload_images(files: List[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="No files.")

    content_blocks = [
        {"type": "text", "text": PROMPT_TO_AI},
    ]
    filenames = []

    for f in files:
        ct = (f.content_type or "").lower()
        if not ct.startswith("image/"):
            raise HTTPException(status_code=415, detail=f"Unknown file type: {ct or 'unknown'} (wymagane image/*)")

        data = await f.read()
        b64 = base64.b64encode(data).decode("utf-8")
        data_url = f"data:{ct};base64,{b64}"

        content_blocks.append({"type": "text", "text": f"FILENAME:{f.filename}"})
        content_blocks.append({"type": "image_url", "image_url": {"url": data_url}})
        filenames.append(f.filename)

    chat = OPEN_AI_CLIENT.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": content_blocks}],
        temperature=0
    )

    result_text = chat.choices[0].message.content

    return JSONResponse(
        content={
            # "model": "gpt-4o-mini",
            "response": result_text.removeprefix("```html").removesuffix("```").strip()
        }
    )

