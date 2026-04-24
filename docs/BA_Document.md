# TÀI LIỆU PHÂN TÍCH NGHIỆP VỤ (BA Document)
# Dịch Vụ API Tạo Ảnh AI - Host Nội Bộ

| Thông tin | Chi tiết |
|-----------|----------|
| **Dự án** | AI Image Generation API Service |
| **Ngày tạo** | 23/04/2026 |
| **Phiên bản** | 3.0 |
| **Trạng thái** | Draft |
| **Deadline** | 07/05/2026 |

---

## 1. TÓM TẮT DỰ ÁN (Executive Summary)

Xây dựng **dịch vụ API tạo và xử lý ảnh bằng AI**, host trên máy chủ nội bộ
(PC với GPU NVIDIA RTX 5070, 12GB VRAM). Dịch vụ cung cấp REST API để
**các website/ứng dụng bên ngoài** gọi API tạo ảnh hoặc biến đổi ảnh theo yêu cầu.

**Hai chức năng chính:**
1. **Tạo ảnh từ text** (text-to-image): Nhận prompt mô tả → trả ảnh mới
2. **Biến đổi ảnh** (image-to-image): Nhận ảnh gốc + prompt hướng dẫn → trả ảnh
   đã biến đổi theo prompt (giữ cấu trúc ảnh gốc, thay đổi style/bề mặt)

Hệ thống sử dụng model mã nguồn mở Stable Diffusion 3.5 Medium,
có xác thực bằng API key, giới hạn tốc độ (rate limit), và theo dõi lượng sử dụng
(usage tracking) cho từng client.

---

## 2. BỐI CẢNH VÀ VẤN ĐỀ (Problem Statement)

### 2.1 Hiện trạng
- Các website muốn tích hợp tính năng tạo ảnh AI phải dùng API cloud trả phí
  (OpenAI, Stability AI, Midjourney).
- Chi phí cao: **$0.02 - $0.19/ảnh**, tích luỹ nhanh khi nhiều website cùng sử dụng.
- Phụ thuộc hoàn toàn vào bên thứ ba về uptime, pricing, và policy.

### 2.2 Vấn đề cần giải quyết
- Cung cấp API tạo ảnh AI **giá rẻ hoặc miễn phí** cho các website nội bộ/đối tác.
- Kiểm soát hoàn toàn hạ tầng, không phụ thuộc bên ngoài.
- Quản lý được ai đang dùng, dùng bao nhiêu, và giới hạn khi cần.

---

## 3. GIẢI PHÁP ĐỀ XUẤT (Proposed Solution)

### 3.1 Tổng quan giải pháp
Triển khai model **Stable Diffusion 3.5 Medium** trên PC nội bộ, bọc bởi một API server
có đầy đủ: xác thực, rate limit, hàng đợi, tracking. Các website bên ngoài gọi API
qua HTTPS với API key được cấp riêng.

### 3.2 Tại sao chọn Stable Diffusion 3.5?

| Tiêu chí | SD 3.5 | GPT-Image (OpenAI) | Midjourney |
|-----------|--------|---------------------|------------|
| Chi phí | Miễn phí (mã nguồn mở) | ~$0.04-0.19/ảnh | ~$10-60/tháng |
| Host nội bộ | Được | Không | Không |
| Bảo mật dữ liệu | Hoàn toàn nội bộ | Gửi lên cloud | Gửi lên cloud |
| Chất lượng ảnh | Cao | Rất cao | Rất cao |
| Tuỳ chỉnh model | Có (fine-tune) | Không | Không |
| Cung cấp lại cho bên thứ ba | Được | Tuỳ ToS | Không |

### 3.3 Kiến trúc hệ thống

```
                     Website A / B / C
                     (co API key rieng)
                            |
                         HTTPS
                            |
  +---------------------------------------------------------+
  |                  PC HOST (RTX 5070)                     |
  |                                                         |
  |   [Nginx HTTPS] --> [FastAPI :8000] --> [Auth+RateLimit] |
  |                          |                              |
  |              +-----------+-----------+                  |
  |              |                       |                  |
  |        [txt2img]              [img2img]                 |
  |       prompt -> anh        anh + prompt -> anh          |
  |              |                       |                  |
  |              +-----------+-----------+                  |
  |                          |                              |
  |                    [Output PNG]     [Usage Tracker DB]  |
  |                                                         |
  +---------------------------------------------------------+
```

### 3.4 Luong hoat dong (Workflow)

```
Website gui request + API key
        |
Nginx nhan request (HTTPS -> HTTP noi bo)
        |
FastAPI kiem tra API key ---- Sai -> 401 Unauthorized
        | Dung
Kiem tra rate limit ---- Qua gioi han -> 429 Too Many Requests
        | OK
Xu ly tren GPU (~5-15 giay)
  - /api/v1/generate: tao anh tu prompt text
  - /api/v1/design: bien doi anh theo prompt (img2img)
        |
Ghi log usage -> Tra anh PNG ve cho website
```

## 4. YÊU CẦU KỸ THUẬT (Technical Requirements)

### 4.1 Phần cứng (đã có)

| Thành phần | Cấu hình tối thiểu | Cấu hình hiện tại | Đánh giá |
|------------|--------------------|--------------------|----------|
| GPU | NVIDIA 8GB VRAM | **RTX 5070 12GB** | Đạt |
| RAM | 16GB | Cần xác nhận | - |
| Ổ cứng | SSD 50GB trống | Cần xác nhận | - |
| CPU | 4 cores | Cần xác nhận | - |
| Mạng | Upload ổn định 10Mbps+ | Cần xác nhận | - |

### 4.2 Phần mềm

| Thành phần | Phiên bản | Mục đích |
|------------|-----------|----------|
| Python | 3.10.x | Runtime |
| PyTorch | 2.x + CUDA | Deep learning framework |
| Diffusers | Latest | Load và chạy SD model |
| FastAPI | Latest | API server |
| Nginx | Latest | Reverse proxy + HTTPS |
| SQLite | Built-in | Lưu usage log + API key |
| Certbot/SSL | Latest | Chứng chỉ HTTPS miễn phí |
| NVIDIA Driver | 550+ | GPU driver |

### 4.3 Yêu cầu mạng (để web bên ngoài gọi được)

| Hạng mục | Mô tả | Phương án |
|----------|-------|-----------|
| **IP tĩnh hoặc DDNS** | Web bên ngoài cần biết địa chỉ để gọi API | Dùng DDNS miễn phí (No-IP, DuckDNS) hoặc IP tĩnh từ ISP |
| **Port forwarding** | Mở port từ router vào PC | Forward port 443 (HTTPS) → PC |
| **Domain (tuỳ chọn)** | Địa chỉ dễ nhớ thay vì IP | Mua domain hoặc dùng subdomain DDNS |
| **SSL/HTTPS** | Bắt buộc cho API public | Let's Encrypt (miễn phí) qua Certbot |

**Phương án thay thế (nếu mạng không cho phép port forward):**

| Phương án | Chi phí | Mô tả |
|-----------|---------|-------|
| Cloudflare Tunnel | Miễn phí | Tạo tunnel từ PC ra internet, không cần mở port |
| Ngrok | Miễn phí / $8/tháng | Tunnel nhanh, domain cố định cần trả phí |
| Tailscale | Miễn phí | VPN mesh, phù hợp nếu các web cùng hệ thống |

### 4.4 Model AI

| Model | Kích thước | VRAM cần | Thời gian/ảnh (RTX 5070) |
|-------|-----------|----------|--------------------------|
| SD 3.5 Medium | ~5.5 GB | ~8 GB | ~5-10 giây |
| SD 3.5 Large | ~12 GB | ~12 GB | ~10-20 giây |

**Khuyến nghị:** Bắt đầu với **SD 3.5 Medium** vì fit tốt trong 12GB VRAM, dư headroom
cho queue xử lý.

---

## 5. XÁC THỰC & BẢO MẬT (Authentication & Security)

### 5.1 API Key Authentication

Mỗi website/client được cấp một **API key** riêng biệt.

```
Header: Authorization: Bearer sk-abc123xyz...
```

| Thuộc tính API Key | Mô tả |
|--------------------|-------|
| Tên client | Tên website/ứng dụng sử dụng |
| API key | Chuỗi ngẫu nhiên duy nhất (64 ký tự) |
| Rate limit | Số request tối đa/phút cho client này |
| Quota/tháng | Số ảnh tối đa được tạo/tháng (0 = không giới hạn) |
| Trạng thái | Active / Suspended / Revoked |
| Ngày tạo | Timestamp |

### 5.2 Rate Limiting

| Level | Giới hạn mặc định | Mục đích |
|-------|--------------------|----------|
| Per API key | 10 request/phút | Ngăn 1 client spam |
| Global | 20 request/phút | Bảo vệ GPU không quá tải |

Khi vượt limit → trả về **HTTP 429** kèm header `Retry-After`.

### 5.3 Bảo mật khác

| Biện pháp | Mô tả |
|-----------|-------|
| HTTPS bắt buộc | Mọi request phải qua HTTPS |
| CORS whitelist | Chỉ cho phép domain đã đăng ký gọi API từ browser |
| Input validation | Kiểm tra prompt length, kích thước ảnh hợp lệ |
| Không lưu prompt | Prompt không được lưu lâu dài (chỉ log tạm nếu cần debug) |

---

## 6. API SPECIFICATION

### 6.1 Base URL
```
https://your-domain.com/api/v1
```

### 6.2 Xác thực
Tất cả request cần header:
```
Authorization: Bearer <API_KEY>
```

### 6.3 Endpoints

#### POST /api/v1/design (ENDPOINT CHÍNH - Biến đổi ảnh theo style)
Nhận ảnh gốc + prompt mô tả style mong muốn → trả ảnh đã biến đổi.
**Giữ nguyên cấu trúc/bố cục ảnh gốc, chỉ thay đổi style/bề mặt.**

**Request:** `multipart/form-data`

| Field | Type | Bắt buộc | Mô tả |
|-------|------|----------|-------|
| image | File (PNG/JPG/WEBP) | Có | Ảnh gốc cần biến đổi |
| prompt | string | Có | Prompt mô tả style mong muốn |
| negative_prompt | string | Không | Những thứ không muốn xuất hiện |
| strength | float (0.1-0.95) | Không | Mức thay đổi so với ảnh gốc (mặc định 0.6) |
| steps | int (1-50) | Không | Số bước xử lý (mặc định 28) |
| guidance_scale | float (1-20) | Không | Mức bám sát prompt (mặc định 7.0) |
| seed | int | Không | Seed để tạo lại kết quả giống nhau |

**Về tham số `strength` (quan trọng):**
```
strength = 0.3-0.4  →  Giữ rất nhiều cấu trúc gốc, thay đổi nhẹ
strength = 0.5-0.6  →  Cân bằng (KHUYẾN NGHỊ bắt đầu ở đây)
strength = 0.7-0.8  →  Style mạnh hơn, nhưng có thể mất chi tiết cấu trúc
strength = 0.9      →  Gần như tạo ảnh mới, chỉ giữ bố cục chung
```

**Response:** `200 OK` - File ảnh PNG (binary)

**Ví dụ prompt từ Gemini:**
```
"Mediterranean exterior style: warm cream stucco walls, terracotta clay
roof tiles, arched wooden front door with iron hardware, wrought iron
window grilles, stone accent trim around windows, small juliet balcony
with iron railing, terracotta flower pots, warm ambient lighting"
```

---

#### POST /api/v1/generate (Phụ - Tạo ảnh từ text)
Tạo ảnh hoàn toàn mới từ prompt, không cần ảnh input.
Dùng khi không có ảnh input.

**Request:** `application/json`
```json
{
    "prompt": "a modern minimalist house, white walls, glass windows",
    "negative_prompt": "blurry, low quality",
    "width": 512,
    "height": 512,
    "steps": 28,
    "guidance_scale": 7.0,
    "seed": 12345
}
```

**Response:** `200 OK` - File ảnh PNG (binary)

**Headers trả về:**
- `X-Generation-Time`: Thời gian tạo ảnh (vd: `8.2s`)
- `X-Request-Id`: ID của request (dùng để trace/debug)
- `X-RateLimit-Remaining`: Số request còn lại trong window

**Lỗi có thể trả về:**

| HTTP Code | Ý nghĩa | Khi nào |
|-----------|---------|---------|
| 401 | Unauthorized | API key sai hoặc thiếu |
| 403 | Forbidden | API key bị suspended/revoked |
| 422 | Validation Error | Prompt quá dài, kích thước không hợp lệ |
| 429 | Too Many Requests | Vượt rate limit |
| 503 | Service Busy | Queue đầy, GPU đang bận |

---

#### POST /api/v1/generate/async (Asynchronous - Khuyến nghị)
Gửi request tạo ảnh, nhận task_id, sau đó poll hoặc nhận webhook khi xong.
Phù hợp khi client không muốn chờ lâu (UX tốt hơn).

**Request:** (giống /generate, thêm webhook tuỳ chọn)
```json
{
    "prompt": "a sunset over mountains, oil painting style",
    "width": 768,
    "height": 768,
    "webhook_url": "https://your-website.com/api/image-callback"
}
```

**Response:** `202 Accepted`
```json
{
    "task_id": "task_a1b2c3d4",
    "status": "queued",
    "position": 3,
    "estimated_time": "30s"
}
```

---

#### GET /api/v1/tasks/{task_id}
Kiểm tra trạng thái của task async.

**Response (đang xử lý):**
```json
{
    "task_id": "task_a1b2c3d4",
    "status": "processing",
    "progress": 60
}
```

**Response (hoàn thành):**
```json
{
    "task_id": "task_a1b2c3d4",
    "status": "completed",
    "image_url": "/api/v1/images/task_a1b2c3d4.png",
    "generation_time": "8.2s"
}
```

---

#### GET /api/v1/images/{filename}
Tải ảnh đã tạo. Ảnh được giữ trên server **24 giờ** rồi tự xoá.

**Response:** File ảnh PNG (binary)

---

#### GET /api/v1/usage
Xem thống kê sử dụng của API key hiện tại.

**Response:**
```json
{
    "client": "Website A",
    "period": "2026-04",
    "images_generated": 342,
    "quota_limit": 1000,
    "quota_remaining": 658,
    "total_generation_time": "2847.3s"
}
```

---

#### GET /api/v1/health
Kiểm tra trạng thái server (không cần API key).

**Response:**
```json
{
    "status": "ok",
    "gpu": "NVIDIA RTX 5070",
    "vram_used": "7.8 GB / 12 GB",
    "queue_size": 2,
    "uptime": "3d 14h 22m"
}
```

### 6.4 Webhook Callback

Khi task async hoàn thành, server gọi POST đến `webhook_url` mà client đã cung cấp:

```json
{
    "event": "image.completed",
    "task_id": "task_a1b2c3d4",
    "image_url": "https://your-domain.com/api/v1/images/task_a1b2c3d4.png",
    "generation_time": "8.2s"
}
```

### 6.5 Giới hạn tham số

| Tham số | Min | Max | Mặc định |
|---------|-----|-----|----------|
| prompt length | 1 ký tự | 2000 ký tự | - |
| width | 256 | 1024 | 512 |
| height | 256 | 1024 | 512 |
| steps | 1 | 50 | 28 |
| guidance_scale | 1.0 | 20.0 | 7.0 |

### 6.6 SDK / Cách tích hợp cho website client

**JavaScript (Frontend - gửi ảnh nhà thô + prompt):**
```javascript
async function designExterior(houseImageFile, stylePrompt) {
    const formData = new FormData();
    formData.append('image', houseImageFile);  // File từ <input type="file">
    formData.append('prompt', stylePrompt);     // Prompt từ Gemini
    formData.append('strength', '0.6');

    const response = await fetch('https://your-domain.com/api/v1/design', {
        method: 'POST',
        headers: { 'Authorization': 'Bearer sk-your-api-key' },
        body: formData
    });

    const blob = await response.blob();
    return URL.createObjectURL(blob);  // URL ảnh hiển thị
}
```

**Python (Backend):**
```python
import requests

with open('nha_tho.jpg', 'rb') as f:
    response = requests.post(
        'https://your-domain.com/api/v1/design',
        headers={'Authorization': 'Bearer sk-your-api-key'},
        files={'image': ('house.jpg', f, 'image/jpeg')},
        data={
            'prompt': 'Mediterranean style, cream walls, terracotta roof...',
            'strength': '0.6',
        }
    )
with open('nha_da_thiet_ke.png', 'wb') as f:
    f.write(response.content)
```

**cURL:**
```bash
curl -X POST https://your-domain.com/api/v1/design \
  -H "Authorization: Bearer sk-your-api-key" \
  -F "image=@nha_tho.jpg" \
  -F "prompt=Mediterranean style, cream walls, terracotta roof tiles" \
  -F "strength=0.6" \
  --output nha_da_thiet_ke.png
```

---

## 7. TASK QUEUE & XỬ LÝ ĐỒNG THỜI (Concurrency)

### 7.1 Vấn đề
GPU chỉ xử lý được **1 ảnh tại 1 thời điểm**. Nếu 5 website gửi request cùng lúc,
4 request phải chờ.

### 7.2 Giải pháp: Task Queue

```
Request A ──┐
Request B ──┤     ┌──────────┐     ┌──────┐     ┌────────┐
Request C ──┼────▶│  Queue   │────▶│ GPU  │────▶│ Output │
Request D ──┤     │ (max 20) │     │      │     │        │
Request E ──┘     └──────────┘     └──────┘     └────────┘
                  Xếp hàng,        Xử lý         Trả kết
                  FIFO             từng cái       quả
```

| Cấu hình | Giá trị | Mô tả |
|-----------|---------|-------|
| Queue size | 20 | Tối đa 20 request chờ |
| Timeout | 120 giây | Request chờ quá lâu → huỷ |
| Khi queue đầy | Trả 503 | Client biết để retry sau |

---

## 8. THEO DÕI SỬ DỤNG (Usage Tracking)

### 8.1 Dữ liệu được ghi lại

Mỗi request tạo ảnh sẽ được log:

| Trường | Mô tả | Ví dụ |
|--------|-------|-------|
| request_id | ID duy nhất | `req_a1b2c3` |
| client_name | Tên website | `Website A` |
| api_key_id | ID của API key | `key_001` |
| timestamp | Thời điểm request | `2026-04-23 14:30:00` |
| prompt_hash | Hash của prompt (không lưu prompt gốc) | `sha256:abc...` |
| width x height | Kích thước ảnh | `512x512` |
| steps | Số bước inference | `28` |
| generation_time | Thời gian tạo | `8.2s` |
| status | Trạng thái | `success / failed` |

### 8.2 Dashboard (Phase 3)

Có thể xây thêm trang web dashboard để xem:
- Tổng số ảnh đã tạo theo ngày/tuần/tháng
- Usage per client
- Thời gian xử lý trung bình
- GPU utilization

---

## 9. PHÂN TÍCH CHI PHÍ (Cost Analysis)

### 9.1 Chi phí triển khai (một lần)

| Hạng mục | Chi phí | Ghi chú |
|----------|---------|---------|
| Phần cứng (PC + RTX 5070) | Đã có | Không phát sinh |
| Phần mềm | $0 | Toàn bộ mã nguồn mở |
| Model AI | $0 | Miễn phí |
| Domain (tuỳ chọn) | ~200,000 VNĐ/năm | Hoặc dùng DDNS miễn phí |
| SSL Certificate | $0 | Let's Encrypt miễn phí |
| **Tổng** | **~0 - 200,000 VNĐ** | |

### 9.2 Chi phí vận hành (hàng tháng)

| Hạng mục | Chi phí ước tính |
|----------|------------------|
| Điện (PC chạy 8h/ngày) | ~200,000 - 400,000 VNĐ/tháng |
| Internet (đã có) | $0 |
| Bảo trì | Tự vận hành |
| **Tổng** | **~200,000 - 400,000 VNĐ/tháng** |

### 9.3 So sánh với dịch vụ cloud

Giả sử phục vụ **3 website**, mỗi website tạo **500 ảnh/tháng** = **1,500 ảnh/tháng**:

| | Host nội bộ | OpenAI API | Stability AI API |
|---|---|---|---|
| Chi phí/tháng | ~300,000 VNĐ (điện) | ~$60-285 (1.5-7 triệu VNĐ) | ~$30-90 (750K-2.3 triệu VNĐ) |
| Chi phí/năm | ~3.6 triệu VNĐ | ~18-85 triệu VNĐ | ~9-27 triệu VNĐ |
| Giới hạn | Không | Theo budget | Theo budget |

**Kết luận:** Với volume 1,500+ ảnh/tháng, host nội bộ tiết kiệm **80-95%** chi phí.

---

## 10. RỦI RO VÀ GIẢM THIỂU (Risks & Mitigation)

| # | Rủi ro | Mức độ | Giảm thiểu |
|---|--------|--------|------------|
| 1 | GPU hỏng → ngừng dịch vụ | Trung bình | Fallback sang cloud API (OpenAI) tạm thời |
| 2 | PC mất điện / restart | Trung bình | Cấu hình auto-start service + UPS |
| 3 | Quá tải khi nhiều client cùng gọi | Trung bình | Queue system + rate limit per client |
| 4 | API bị lạm dụng (spam, nội dung xấu) | Trung bình | Rate limit + API key revoke + content filter |
| 5 | Mất kết nối internet | Thấp | Monitoring + alert + ISP backup |
| 6 | DDoS attack | Thấp | Cloudflare proxy (miễn phí) + rate limit |
| 7 | Chất lượng ảnh không đạt kỳ vọng | Thấp | Fine-tune model hoặc đổi sang Flux |
| 8 | IP động thay đổi | Thấp | DDNS tự động cập nhật |

---

## 11. KẾ HOẠCH TRIỂN KHAI (Implementation Plan)

**Tổng thời gian:** ~2 tuần (23/04/2026 → 07/05/2026)

### Tuần 1 (23/04 - 30/04): Phát triển core + test
- [x] Setup môi trường Python + dependencies
- [x] Viết code generate ảnh (txt2img + img2img, auto-detect GPU)
- [x] Viết API server cơ bản (FastAPI)
- [ ] Test trên máy dev (GTX 1650)
- [ ] Thêm API key authentication
- [ ] Thêm rate limiting + CORS
- [ ] Thêm error handling & logging

### Tuần 2 (01/05 - 07/05): Deploy + tích hợp
- [ ] Cài đặt môi trường trên PC RTX 5070
- [ ] Tải model SD 3.5 Medium
- [ ] Test hiệu năng (thời gian tạo ảnh, VRAM usage)
- [ ] Cấu hình port forwarding hoặc Cloudflare Tunnel
- [ ] Cấu hình auto-start khi PC bật
- [ ] Cấp API key cho website client, hỗ trợ tích hợp

### Sau deadline (nếu có thời gian):
- [ ] Cài Nginx reverse proxy + SSL
- [ ] Thêm task queue (async generation)
- [ ] Thêm usage tracking (SQLite)
- [ ] Xây dashboard usage
- [ ] Mở rộng model (Flux, SDXL)

---

## 12. TIÊU CHÍ NGHIỆM THU (Acceptance Criteria)

### Phase 1 - Core
1. API server khởi động thành công trên PC RTX 5070
2. Endpoint `POST /api/v1/generate` trả về ảnh PNG hợp lệ
3. Thời gian tạo ảnh 512x512 dưới 15 giây

### Phase 2 - Security
4. Request không có API key → trả 401
5. Request vượt rate limit → trả 429
6. Queue hoạt động đúng khi nhiều request đồng thời
7. Usage log ghi đầy đủ thông tin mỗi request

### Phase 3 - Production
8. Website bên ngoài gọi API qua HTTPS thành công
9. Server chạy ổn định liên tục ít nhất 24 giờ không crash
10. `GET /health` trả về trạng thái chính xác

---

## 13. PHỤ LỤC

### A. Cấu trúc dự án

```
Host_AI_TaoAnh/
├── .env                 # Config & secrets (không commit)
├── .env.example         # Template
├── .gitignore
├── requirements.txt     # Dependencies
│
├── generate.py          # Core: load model + tạo ảnh (txt2img + img2img)
├── server.py            # API server (FastAPI) - endpoint /design + /generate
├── auth.py              # API key authentication
├── queue_manager.py     # Task queue management
├── usage_tracker.py     # Usage logging (SQLite)
│
├── outputs/             # Ảnh đã tạo (tự xoá sau 24h)
├── data/                # SQLite DB (API keys, usage logs)
├── docs/                # Tài liệu
│   ├── BA_Document.md   # Tài liệu BA (file này)
│   └── Presentation_Guide.md  # Hướng dẫn thuyết trình
│
└── nginx/               # Config Nginx (cho production)
    └── api.conf
```

### B. Cách chạy (Development)

```bash
# Cài đặt
pip install -r requirements.txt

# Test tạo ảnh (chạy trực tiếp - tạo ảnh text + img2img demo)
python generate.py

# Chạy API server
uvicorn server:app --host 0.0.0.0 --port 8000

# Gọi API biến đổi ảnh (endpoint chính)
curl -X POST http://localhost:8000/api/v1/design \
  -H "Authorization: Bearer sk-your-api-key" \
  -F "image=@nha_tho.jpg" \
  -F "prompt=modern minimalist, white walls, glass windows" \
  -F "strength=0.6" \
  --output result.png
```

### C. Cách gọi API (cho website client)

```bash
# Biến đổi ảnh (endpoint chính)
curl -X POST https://your-domain.com/api/v1/design \
  -H "Authorization: Bearer sk-your-api-key" \
  -F "image=@nha_tho.jpg" \
  -F "prompt=Mediterranean style, cream walls, terracotta roof" \
  -F "strength=0.6" \
  --output nha_da_thiet_ke.png

# Tạo ảnh từ text (endpoint phụ)
curl -X POST https://your-domain.com/api/v1/generate \
  -H "Authorization: Bearer sk-your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "a modern house exterior"}' \
  --output image.png

# Kiểm tra trạng thái
curl https://your-domain.com/api/v1/health
```

### D. Glossary

| Thuật ngữ | Giải thích |
|-----------|------------|
| Stable Diffusion | Model AI tạo ảnh mã nguồn mở từ Stability AI |
| VRAM | Bộ nhớ trên card đồ hoạ, dùng để chạy model AI |
| Prompt | Câu mô tả nội dung ảnh muốn tạo |
| API | Giao diện lập trình, cho phép các ứng dụng khác gọi tạo ảnh |
| API Key | Mã bí mật dùng để xác thực quyền truy cập API |
| Rate Limit | Giới hạn số request trong 1 khoảng thời gian |
| Task Queue | Hàng đợi xếp thứ tự xử lý khi có nhiều request |
| Webhook | Server tự động gọi lại URL của client khi có kết quả |
| CORS | Cơ chế cho phép/chặn website gọi API từ domain khác |
| Reverse Proxy | Nginx đứng trước API server, xử lý HTTPS và chuyển tiếp request |
| DDNS | Dịch vụ tự động cập nhật domain khi IP thay đổi |
| SSL/HTTPS | Mã hoá kết nối giữa client và server |
| FastAPI | Framework Python để xây dựng API server nhanh |
| Fine-tune | Huấn luyện thêm model với dữ liệu riêng để cải thiện chất lượng |
| Inference | Quá trình model xử lý input và tạo ra output (ảnh) |
| CPU Offload | Kỹ thuật chuyển một phần xử lý từ GPU sang CPU để tiết kiệm VRAM |
