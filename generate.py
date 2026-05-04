import torch
import os
import sys
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

SUPPORTED_MODELS = {
    "sd35-medium": {
        "id": "stabilityai/stable-diffusion-3.5-medium",
        "family": "sd3",
        "name": "Stable Diffusion 3.5 Medium",
        "vram": "~8 GB",
        "quality": "Cao",
        "speed": "Nhanh",
        "note": "Can bang giua chat luong va toc do. Khuyen nghi.",
    },
    "sd35-large": {
        "id": "stabilityai/stable-diffusion-3.5-large",
        "family": "sd3",
        "name": "Stable Diffusion 3.5 Large",
        "vram": "~12 GB",
        "quality": "Rat cao",
        "speed": "Cham",
        "note": "Chat luong tot nhat nhung can nhieu VRAM.",
    },
    "sdxl": {
        "id": "stabilityai/stable-diffusion-xl-base-1.0",
        "family": "sdxl",
        "name": "Stable Diffusion XL 1.0",
        "vram": "~7 GB",
        "quality": "Cao",
        "speed": "Nhanh",
        "note": "He sinh thai ControlNet lon nhat. Khong can HF token.",
    },
    "sd15": {
        "id": "stable-diffusion-v1-5/stable-diffusion-v1-5",
        "family": "sd15",
        "name": "Stable Diffusion 1.5",
        "vram": "~4 GB",
        "quality": "Trung binh",
        "speed": "Rat nhanh",
        "note": "Nhe, chay tot tren GTX 1650. Nhieu LoRA/model custom.",
    },
    "flux-schnell": {
        "id": "black-forest-labs/FLUX.1-schnell",
        "family": "flux",
        "name": "FLUX.1 Schnell",
        "vram": "~12 GB",
        "quality": "Rat cao",
        "speed": "Nhanh (4 steps)",
        "note": "Model moi nhat, chat luong cao. Apache 2.0, khong can token.",
    },
    "flux-dev": {
        "id": "black-forest-labs/FLUX.1-dev",
        "family": "flux",
        "name": "FLUX.1 Dev",
        "vram": "~12 GB",
        "quality": "Rat cao",
        "speed": "Trung binh (20-50 steps)",
        "note": "Chat luong tot hon Schnell. Can HF token, non-commercial license.",
    },
}


def list_models():
    print("\n=== DANH SACH MODEL HO TRO ===\n")
    for key, m in SUPPORTED_MODELS.items():
        print(f"  [{key}]")
        print(f"    Ten:       {m['name']}")
        print(f"    HF ID:     {m['id']}")
        print(f"    VRAM:      {m['vram']}")
        print(f"    Chat luong: {m['quality']}")
        print(f"    Toc do:    {m['speed']}")
        print(f"    Ghi chu:   {m['note']}")
        print()
    print("Cach doi model: sua MODEL_ID trong file .env")
    print("Vi du: MODEL_ID=stabilityai/stable-diffusion-xl-base-1.0")


def _resolve_model_id():
    model_id = os.getenv("MODEL_ID", "stabilityai/stable-diffusion-3.5-medium")
    for m in SUPPORTED_MODELS.values():
        if m["id"] == model_id:
            return model_id, m["family"], m["name"]
    return model_id, _guess_family(model_id), model_id


def _guess_family(model_id):
    mid = model_id.lower()
    if "flux" in mid:
        return "flux"
    if "stable-diffusion-3" in mid:
        return "sd3"
    if "stable-diffusion-xl" in mid or "sdxl" in mid:
        return "sdxl"
    return "sd15"


def _get_pipeline_classes(family):
    if family == "sd3":
        from diffusers import StableDiffusion3Pipeline, StableDiffusion3Img2ImgPipeline
        return StableDiffusion3Pipeline, StableDiffusion3Img2ImgPipeline
    elif family == "sdxl":
        from diffusers import StableDiffusionXLPipeline, StableDiffusionXLImg2ImgPipeline
        return StableDiffusionXLPipeline, StableDiffusionXLImg2ImgPipeline
    elif family == "flux":
        from diffusers import FluxPipeline, FluxImg2ImgPipeline
        return FluxPipeline, FluxImg2ImgPipeline
    else:
        from diffusers import StableDiffusionPipeline, StableDiffusionImg2ImgPipeline
        return StableDiffusionPipeline, StableDiffusionImg2ImgPipeline


def get_device_config():
    if not torch.cuda.is_available():
        return {"device": "cpu", "dtype": torch.float32, "offload": "sequential"}

    vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024 ** 3)
    name = torch.cuda.get_device_name(0)
    print(f"GPU: {name} | VRAM: {vram_gb:.1f} GB")

    if vram_gb >= 10:
        return {"device": "cuda", "dtype": torch.float16, "offload": "model"}
    else:
        return {"device": "cuda", "dtype": torch.float32, "offload": "sequential"}


def _get_token():
    token = os.getenv("HF_TOKEN")
    if not token or token == "hf_your_token_here":
        return None
    return token


def _apply_offload(pipe, config):
    if config["offload"] == "sequential":
        pipe.enable_sequential_cpu_offload()
        print("Mode: Sequential CPU offload (cham nhung tiet kiem VRAM)")
    elif config["offload"] == "model":
        pipe.enable_model_cpu_offload()
        print("Mode: Model CPU offload (nhanh)")
    pipe.enable_attention_slicing()


def _get_model_vram(model_id):
    for m in SUPPORTED_MODELS.values():
        if m["id"] == model_id:
            try:
                return float(m["vram"].replace("~", "").replace("GB", "").strip())
            except ValueError:
                return 8.0
    return 8.0


def load_pipelines():
    config = get_device_config()
    token = _get_token()
    model_id, family, name = _resolve_model_id()
    Txt2ImgClass, Img2ImgClass = _get_pipeline_classes(family)

    vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024 ** 3) if torch.cuda.is_available() else 0
    model_vram = _get_model_vram(model_id)
    if model_vram >= vram_gb and config["offload"] == "model":
        config["offload"] = "sequential"
        print(f"  Model can {model_vram}GB, GPU chi co {vram_gb:.0f}GB -> chuyen sang sequential offload")

    print(f"Dang tai model: {name}")
    print(f"  HF ID: {model_id}")
    print(f"  Family: {family}")
    print(f"  (Lan dau tai se mat vai phut, lan sau load tu cache)")

    dtype = torch.bfloat16 if family == "flux" else config["dtype"]
    load_kwargs = {"torch_dtype": dtype}
    if token:
        load_kwargs["token"] = token

    txt2img = Txt2ImgClass.from_pretrained(model_id, **load_kwargs)
    if hasattr(txt2img, "safety_checker"):
        txt2img.safety_checker = None
    _apply_offload(txt2img, config)

    img2img = Img2ImgClass.from_pretrained(model_id, **load_kwargs)
    if hasattr(img2img, "safety_checker"):
        img2img.safety_checker = None
    _apply_offload(img2img, config)

    print(f"Da tai xong: {name} (txt2img + img2img)")
    config["family"] = family
    return txt2img, img2img, config


def generate_from_text(pipe, prompt, negative_prompt="", width=512, height=512,
                       steps=28, guidance_scale=7.0, seed=None):
    generator = None
    if seed is not None:
        generator = torch.Generator("cpu").manual_seed(seed)

    is_flux = "Flux" in type(pipe).__name__
    kwargs = {
        "prompt": prompt,
        "width": width,
        "height": height,
        "num_inference_steps": steps,
        "guidance_scale": guidance_scale,
        "generator": generator,
    }
    if not is_flux and negative_prompt:
        kwargs["negative_prompt"] = negative_prompt

    return pipe(**kwargs).images[0]


def generate_from_image(pipe, prompt, image, negative_prompt="",
                        strength=0.6, steps=28, guidance_scale=7.0, seed=None):
    generator = None
    if seed is not None:
        generator = torch.Generator("cpu").manual_seed(seed)

    if isinstance(image, str):
        image = Image.open(image)
    image = image.convert("RGB")

    is_flux = "Flux" in type(pipe).__name__
    kwargs = {
        "prompt": prompt,
        "image": image,
        "strength": strength,
        "num_inference_steps": steps,
        "guidance_scale": guidance_scale,
        "generator": generator,
    }
    if not is_flux and negative_prompt:
        kwargs["negative_prompt"] = negative_prompt

    return pipe(**kwargs).images[0]


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--list-models":
        list_models()
        return

    txt2img, img2img, config = load_pipelines()
    os.makedirs("outputs", exist_ok=True)

    prompt = "a modern house exterior, cream walls, terracotta roof, photorealistic"
    print(f"\n[txt2img] Prompt: '{prompt}'")
    image = generate_from_text(txt2img, prompt)
    image.save("outputs/test_txt2img.png")
    print("Luu tai: outputs/test_txt2img.png")

    print(f"\n[img2img] Dung anh vua tao lam input, ap style moi...")
    styled = generate_from_image(
        img2img,
        prompt="Japanese zen style exterior, dark wood panels, stone garden, minimalist",
        image="outputs/test_txt2img.png",
        strength=0.6,
    )
    styled.save("outputs/test_img2img.png")
    print("Luu tai: outputs/test_img2img.png")


if __name__ == "__main__":
    main()
