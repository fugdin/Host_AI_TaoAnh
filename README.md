# AI Image Generation API

API server tao anh bang AI, ho tro nhieu model (Stable Diffusion, FLUX).
Chay tren may noi bo voi GPU NVIDIA.

## Yeu cau he thong

| Thanh phan | Toi thieu | Khuyen nghi |
|------------|-----------|-------------|
| GPU | NVIDIA 4GB VRAM | RTX 5070 12GB |
| RAM | 16GB | 32GB |
| O cung | SSD 30GB trong | SSD 50GB trong |
| OS | Windows 10/11 | Windows 11 |

---

## Huong dan cai dat tu A-Z

### Buoc 1: Kiem tra va cai NVIDIA Driver

Kiem tra driver da cai chua:
```
nvidia-smi
```

Neu hien thong tin GPU (ten GPU, CUDA version) -> da co, **bo qua buoc nay**.

Neu bao loi "khong tim thay lenh" -> tai driver tai:
https://www.nvidia.com/drivers
- Chon dung model GPU (vd: RTX 5070)
- Tai va cai dat, restart may

---

### Buoc 2: Kiem tra va cai Python 3.10

Kiem tra Python da cai chua:
```
python --version
```
hoac:
```
py -3.10 --version
```

Neu hien `Python 3.10.x` -> da co, **bo qua buoc nay**.

Neu chua co hoac version khac (3.12, 3.14...) -> tai Python 3.10:
https://www.python.org/downloads/release/python-31011/
- Chon **Windows installer (64-bit)**
- Khi cai, **TICH CHON "Add Python to PATH"**
- Neu may da co Python version khac, dung `py -3.10` thay cho `python`

---

### Buoc 3: Kiem tra va cai Git

Kiem tra Git da cai chua:
```
git --version
```

Neu hien `git version x.x.x` -> da co, **bo qua buoc nay**.

Neu chua co -> tai tai: https://git-scm.com/download/win
- Cai dat mac dinh, next het

---

### Buoc 4: Clone repo

Mo CMD, di chuyen den thu muc muon luu (vd: o D):
```
D:
mkdir Thuc_Tap
cd Thuc_Tap
git clone https://github.com/YOUR_USERNAME/Host_AI_TaoAnh.git
cd Host_AI_TaoAnh
```

---

### Buoc 5: Tao Virtual Environment

```
py -3.10 -m venv venv
```

Kich hoat venv:
```
venv\Scripts\activate
```

Khi thanh cong, dau dong CMD se hien `(venv)`.

---

### Buoc 6: Cai PyTorch voi CUDA

Kiem tra phien ban CUDA GPU ho tro:
```
nvidia-smi
```
Xem dong "CUDA Version" o goc tren phai. Thuong la 12.x.

Cai PyTorch (CUDA 12.1):
```
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

**Luu y:** File nang ~2.4GB, doi 10-20 phut tuy mang.

Kiem tra cai thanh cong:
```
python -c "import torch; print(torch.__version__); print('CUDA:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0))"
```

Ket qua mong muon:
```
2.5.1+cu121
CUDA: True
GPU: NVIDIA GeForce RTX 5070
```

---

### Buoc 7: Cai cac thu vien con lai

```
pip install diffusers transformers accelerate safetensors sentencepiece protobuf fastapi "uvicorn[standard]" python-dotenv python-multipart
```

Kiem tra:
```
python -c "import diffusers; import fastapi; print('OK')"
```

---

### Buoc 8: Cau hinh .env

Copy file mau:
```
copy .env.example .env
```

Mo file `.env` bang Notepad va sua:
```
HF_HOME=D:/AI_Models/huggingface
HF_TOKEN=hf_your_token_here
MODEL_ID=stabilityai/stable-diffusion-3.5-medium
```

**HF_HOME**: Thu muc luu model AI (nen de o dia co nhieu dung luong, KHONG de o C).

**HF_TOKEN**: Lay tai https://huggingface.co/settings/tokens
- Tao token moi (Read access)
- Chi can cho model SD 3.5 (can chap nhan license truoc tai trang model)
- SDXL, SD 1.5, FLUX Schnell KHONG can token

**MODEL_ID**: Chon model muon dung (xem bang ben duoi).

---

### Buoc 9: Chay server

```
uvicorn server:app --host 0.0.0.0 --port 8000
```

Lan dau chay se tu dong tai model tu HuggingFace (~5-12GB tuy model).
Doi 5-30 phut tuy mang. Lan sau chay se load tu cache, nhanh hon nhieu.

Khi thay dong nay la thanh cong:
```
API server san sang!
Uvicorn running on http://0.0.0.0:8000
```

---

### Buoc 10: Test API

Mo trinh duyet, truy cap:
```
http://localhost:8000/docs
```

**Test tao anh (txt2img):**
1. Click `POST /api/v1/generate` -> Try it out
2. Nhap:
```json
{
  "prompt": "a modern house exterior, white walls, photorealistic",
  "steps": 20,
  "width": 512,
  "height": 512
}
```
3. Click Execute, doi 5-15 giay (RTX 5070)

**Test bien doi anh (img2img):**
1. Click `POST /api/v1/design` -> Try it out
2. Upload anh nha + nhap prompt style
3. strength: 0.6 (giu cau truc, doi style)
4. Click Execute

---

## Danh sach model ho tro

| Key | Model | VRAM | Chat luong | Toc do | Can token? |
|-----|-------|------|-----------|--------|------------|
| sd35-medium | SD 3.5 Medium | ~8 GB | Cao | Nhanh | Co |
| sd35-large | SD 3.5 Large | ~12 GB | Rat cao | Cham | Co |
| sdxl | SD XL 1.0 | ~7 GB | Cao | Nhanh | Khong |
| sd15 | SD 1.5 | ~4 GB | Trung binh | Rat nhanh | Khong |
| flux-schnell | FLUX.1 Schnell | ~12 GB | Rat cao | Nhanh (4 steps) | Khong |
| flux-dev | FLUX.1 Dev | ~12 GB | Rat cao | Trung binh | Co |

**Doi model:** Sua `MODEL_ID` trong file `.env`:
```
MODEL_ID=black-forest-labs/FLUX.1-schnell
```

Restart server sau khi doi.

**Xem danh sach model:**
```
python generate.py --list-models
```

**Khuyen nghi cho RTX 5070 (12GB VRAM):**
- Bat dau voi `sd35-medium` (can bang chat luong va toc do)
- Test `flux-schnell` (chat luong cao, chi 4 steps)
- Thu `sd35-large` neu muon chat luong tot nhat

---

## API Endpoints

| Method | Endpoint | Mo ta |
|--------|----------|-------|
| POST | /api/v1/generate | Tao anh tu text (txt2img) |
| POST | /api/v1/design | Bien doi anh theo style (img2img) |
| GET | /api/v1/health | Kiem tra trang thai server |
| GET | /api/v1/models | Xem danh sach model ho tro |

**Trang test API:** http://localhost:8000/docs

---

## Cho may khac trong mang truy cap

Khi server chay voi `--host 0.0.0.0`, may khac cung mang co the goi API.

1. Tim IP may chay server:
```
ipconfig
```
Xem dong `IPv4 Address` (vd: `192.168.1.100`)

2. Tu may khac, goi API bang:
```
http://192.168.1.100:8000/api/v1/health
```

3. Neu khong truy cap duoc:
   - Kiem tra Windows Firewall: cho phep Python truy cap Private + Public network
   - Kiem tra router: tat AP Isolation (neu dung WiFi)

---

## Cau truc thu muc

```
Host_AI_TaoAnh/
├── .env                 # Config (KHONG push len git)
├── .env.example         # File mau
├── .gitignore
├── requirements.txt     # Danh sach thu vien
├── generate.py          # Core: load model + tao anh
├── server.py            # API server (FastAPI)
├── README.md            # File nay
├── outputs/             # Anh da tao (tu dong tao)
└── docs/
    ├── BA_Document.md
    └── Presentation_Guide.md
```

---

## Xu ly loi thuong gap

**Loi: CUDA not available**
```
python -c "import torch; print(torch.cuda.is_available())"
# Neu ra False:
# - Kiem tra nvidia-smi co chay khong
# - Cai lai PyTorch voi dung phien ban CUDA
```

**Loi: Model khong tai duoc (401/403)**
- Kiem tra HF_TOKEN trong .env
- Vao trang model tren HuggingFace, chap nhan license
- Thu model khong can token: sdxl, sd15, flux-schnell

**Loi: Out of memory (OOM)**
- Doi sang model nhe hon (sd15 cho 4GB, sdxl cho 7GB)
- Giam width/height xuong 512x512

**Loi: Anh den (black image)**
- Thuong xay ra voi SD 1.5 + float16
- He thong da tu dong xu ly (dung float32 cho GPU <10GB VRAM)

**Loi: Port 8000 da duoc su dung**
```
# Tim process dang dung port 8000
netstat -ano | findstr :8000
# Tat process do bang Task Manager, hoac doi port:
uvicorn server:app --host 0.0.0.0 --port 8001
```
