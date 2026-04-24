import os
import io
import time
import uuid

from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from PIL import Image

from generate import load_pipelines, generate_from_text, generate_from_image, SUPPORTED_MODELS

app = FastAPI(title="AI Image Generation API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

txt2img_pipe = None
img2img_pipe = None
config = None


class TextGenerateRequest(BaseModel):
    prompt: str
    negative_prompt: str = ""
    width: int = Field(default=512, ge=256, le=1024)
    height: int = Field(default=512, ge=256, le=1024)
    steps: int = Field(default=28, ge=1, le=50)
    guidance_scale: float = Field(default=7.0, ge=1.0, le=20.0)
    seed: int | None = None


def _save_and_respond(image, elapsed, prompt):
    os.makedirs("outputs", exist_ok=True)
    filename = f"{uuid.uuid4().hex[:8]}.png"
    image.save(f"outputs/{filename}")

    buf = io.BytesIO()
    image.save(buf, format="PNG")
    buf.seek(0)

    print(f"Tao anh trong {elapsed:.1f}s | {prompt[:50]}")
    return StreamingResponse(
        buf,
        media_type="image/png",
        headers={"X-Generation-Time": f"{elapsed:.1f}s", "X-Filename": filename},
    )


@app.on_event("startup")
def startup():
    global txt2img_pipe, img2img_pipe, config
    txt2img_pipe, img2img_pipe, config = load_pipelines()
    print("API server san sang!")


@app.post("/api/v1/generate")
def api_generate_text(req: TextGenerateRequest):
    start = time.time()
    image = generate_from_text(
        txt2img_pipe,
        prompt=req.prompt,
        negative_prompt=req.negative_prompt,
        width=req.width,
        height=req.height,
        steps=req.steps,
        guidance_scale=req.guidance_scale,
        seed=req.seed,
    )
    return _save_and_respond(image, time.time() - start, req.prompt)


@app.post("/api/v1/design")
def api_design(
    image: UploadFile = File(..., description="Anh goc (PNG/JPG/WEBP)"),
    prompt: str = Form(..., description="Prompt mo ta style mong muon"),
    negative_prompt: str = Form(default=""),
    strength: float = Form(default=0.6, ge=0.1, le=0.95),
    steps: int = Form(default=28, ge=1, le=50),
    guidance_scale: float = Form(default=7.0, ge=1.0, le=20.0),
    seed: int | None = Form(default=None),
):
    start = time.time()

    if image.content_type not in ("image/png", "image/jpeg", "image/jpg", "image/webp"):
        raise HTTPException(400, "Chi chap nhan PNG, JPG, WEBP")

    input_image = Image.open(io.BytesIO(image.file.read())).convert("RGB")

    result = generate_from_image(
        img2img_pipe,
        prompt=prompt,
        image=input_image,
        negative_prompt=negative_prompt,
        strength=strength,
        steps=steps,
        guidance_scale=guidance_scale,
        seed=seed,
    )
    return _save_and_respond(result, time.time() - start, prompt)


@app.get("/api/v1/health")
def health():
    model_id = os.getenv("MODEL_ID", "stabilityai/stable-diffusion-3.5-medium")
    return {
        "status": "ok",
        "model": model_id,
        "family": config["family"] if config else "not loaded",
        "gpu": config["device"] if config else "not loaded",
        "offload": config["offload"] if config else "not loaded",
        "pipelines": {
            "txt2img": txt2img_pipe is not None,
            "img2img": img2img_pipe is not None,
        },
    }


@app.get("/api/v1/models")
def get_models():
    current = os.getenv("MODEL_ID", "stabilityai/stable-diffusion-3.5-medium")
    return {
        "current_model": current,
        "supported_models": {
            key: {
                "name": m["name"],
                "id": m["id"],
                "vram": m["vram"],
                "quality": m["quality"],
                "speed": m["speed"],
                "note": m["note"],
                "active": m["id"] == current,
            }
            for key, m in SUPPORTED_MODELS.items()
        },
    }
