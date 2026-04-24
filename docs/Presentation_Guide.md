# HƯỚNG DẪN THUYẾT TRÌNH BA CHO SẾP
# (Đọc trước khi vào họp - KHÔNG đưa file này cho sếp)

---

## NGUYÊN TẮC VÀNG

1. **Sếp không quan tâm kỹ thuật.** Sếp quan tâm: tốn bao nhiêu tiền, mất bao lâu,
   được cái gì, rủi ro gì.
2. **Nói ngắn trước, chi tiết sau.** Tóm tắt trong 2 phút → sếp hỏi gì trả lời đó.
3. **Đừng đọc tài liệu.** Nói bằng lời của mình, tài liệu chỉ để sếp đọc lại sau.

---

## KỊCH BẢN THUYẾT TRÌNH (~10 phút)

### MỞ ĐẦU (30 giây)

> "Em có một đề xuất về việc tự host dịch vụ tạo ảnh AI trên máy tính của mình,
> để các website của mình có thể gọi API tạo ảnh mà không cần trả tiền cho bên
> thứ ba như OpenAI hay Midjourney."

**Mục đích câu này:** Sếp hiểu ngay bạn muốn làm gì, trong 1 câu.

---

### PHẦN 1: VẤN ĐỀ (1 phút)

> "Hiện tại nếu website mình muốn có tính năng tạo ảnh bằng AI, mình phải dùng
> API của OpenAI hoặc Stability AI. Mỗi ảnh tốn khoảng 1,000 - 5,000 đồng.
> Nếu mình tạo 1,500 ảnh/tháng cho 3 website, thì mỗi tháng tốn khoảng
> 1.5 đến 7 triệu đồng. Một năm là 18 đến 85 triệu."
>
> "Ngoài ra, mình phụ thuộc hoàn toàn vào bên thứ ba - nếu họ tăng giá hoặc
> ngừng dịch vụ thì mình không có lựa chọn nào khác."

**Mẹo:** Nói CON SỐ TIỀN trước. Sếp sẽ chú ý ngay.

---

### PHẦN 2: GIẢI PHÁP (2 phút)

> "Giải pháp của em là dùng chính cái PC có card đồ hoạ RTX 5070 mà mình đã có
> sẵn, cài một model AI tạo ảnh mã nguồn mở tên là Stable Diffusion 3.5.
> Model này miễn phí, chất lượng tương đương 80-90% so với các dịch vụ trả tiền."
>
> "Em sẽ bọc nó thành một API server. Các website của mình chỉ cần gọi API là
> nhận được ảnh, giống y như gọi API của OpenAI, nhưng mình không tốn tiền
> per-ảnh nữa."

**Nếu sếp hỏi "Stable Diffusion là gì?":**
> "Nó giống như ChatGPT nhưng chuyên tạo ảnh. Mã nguồn mở nghĩa là mình tải
> về máy chạy miễn phí, không phải trả phí license."

**Nếu sếp hỏi "Chất lượng có bằng Midjourney/DALL-E không?":**
> "Khoảng 80-90%. Đối với đa số use case như ảnh sản phẩm, minh hoạ, avatar
> thì đủ dùng. Nếu cần ảnh cực kỳ cao cấp thì vẫn có thể dùng API cloud
> cho những trường hợp đặc biệt."

---

### PHẦN 3: CHI PHÍ (2 phút) ← PHẦN QUAN TRỌNG NHẤT

> "Chi phí triển khai: gần như KHÔNG TỐN gì, vì PC và GPU mình đã có sẵn.
> Phần mềm toàn bộ là mã nguồn mở, miễn phí."
>
> "Chi phí vận hành hàng tháng chỉ khoảng 200 đến 400 nghìn tiền điện.
> So với 1.5 đến 7 triệu/tháng nếu dùng API cloud, mình tiết kiệm được
> 80 đến 95%."

Đưa bảng so sánh cho sếp xem (trong tài liệu BA, mục 9.3):

> "Nếu nhìn vào bảng này: một năm host nội bộ tốn khoảng 3.6 triệu.
> Cùng lượng sử dụng đó mà dùng OpenAI thì tốn 18 đến 85 triệu.
> Mình tiết kiệm từ 14 đến 81 triệu mỗi năm."

**Mẹo:** DỪNG ở đây 3 giây. Để sếp tiêu hoá con số.

---

### PHẦN 4: CÁCH HOẠT ĐỘNG (1 phút - nói đơn giản)

> "Cách hoạt động rất đơn giản: website gửi một câu mô tả ảnh muốn tạo
> đến API server, server xử lý trên GPU khoảng 5-15 giây, rồi trả ảnh về.
>
> Em có thiết kế hệ thống bảo mật: mỗi website được cấp một API key riêng,
> có giới hạn số lượng request, có theo dõi ai dùng bao nhiêu.
> Không ai có thể truy cập nếu không có key."

**ĐỪNG NÓI:** Pipeline, inference, VRAM, CPU offload, FastAPI, Nginx, CORS,
rate limiter, webhook callback... Sếp không cần biết những thứ này.

**NẾU sếp hỏi chi tiết kỹ thuật:** Chỉ vào tài liệu BA và nói:
> "Chi tiết kỹ thuật em đã viết đầy đủ trong tài liệu này, anh/chị có thể
> đọc thêm ở mục 4, 5, 6."

---

### PHẦN 5: TIMELINE (1 phút)

> "Em chia thành 4 giai đoạn:
>
> - Tuần 1-2: Phát triển và test cơ bản - em đã làm được phần core rồi.
> - Tuần 3: Thêm bảo mật, API key, giới hạn tốc độ.
> - Sau đó 1-2 ngày deploy lên máy production.
> - Cuối cùng là tích hợp vào các website.
>
> Tổng cộng khoảng 3-4 tuần là có thể chạy được."

---

### PHẦN 6: RỦI RO (1 phút)

> "Rủi ro chính là nếu PC hoặc GPU gặp sự cố thì dịch vụ bị gián đoạn.
> Giải pháp là em sẽ cấu hình fallback sang API cloud tạm thời trong
> trường hợp đó, và cấu hình auto-restart khi PC bật lại.
>
> Còn về bảo mật, mọi request đều phải qua API key, có giới hạn tốc độ,
> và dữ liệu không đi ra ngoài server của mình."

**ĐỪNG liệt kê hết 8 rủi ro.** Chỉ nói 1-2 cái quan trọng nhất.
Nếu sếp hỏi thêm → mở tài liệu BA chỉ bảng rủi ro.

---

### KẾT THÚC (30 giây)

> "Tóm lại: mình tận dụng phần cứng đã có, dùng phần mềm miễn phí,
> tốn khoảng 300 nghìn/tháng tiền điện, tiết kiệm được hàng chục triệu
> mỗi năm so với dùng dịch vụ cloud. Em đã viết chi tiết trong tài liệu này,
> anh/chị xem thêm và cho em feedback ạ."

*Đưa tài liệu BA (bản in hoặc gửi file).*

---

## CÂU HỎI SẾP HAY HỎI & CÁCH TRẢ LỜI

### "Có ai làm kiểu này chưa?"
> "Dạ có. Rất nhiều công ty và cá nhân tự host Stable Diffusion. Cộng đồng
> rất lớn, có hàng triệu người dùng trên thế giới. Đây không phải giải pháp
> thử nghiệm mà đã rất phổ biến rồi."

### "Nếu cần scale lên thì sao?"
> "Nếu cần nhiều hơn, mình có thể thêm GPU thứ hai, hoặc chuyển lên server
> cloud khi volume đủ lớn. Kiến trúc API em thiết kế không thay đổi, chỉ
> thay backend."

### "Mất bao lâu để tạo 1 ảnh?"
> "Khoảng 5-15 giây tuỳ độ phức tạp và kích thước ảnh."

### "Nếu em nghỉ thì ai maintain?"
> "Code em viết đơn giản, có tài liệu đầy đủ. Bất kỳ developer nào biết
> Python đều có thể tiếp quản. Ngoài ra khi chạy ổn định rồi thì hầu như
> không cần maintain, chỉ cần PC bật là API hoạt động."

### "Có vi phạm bản quyền gì không?"
> "Không. Stable Diffusion 3.5 có license cho phép sử dụng thương mại.
> Mình tải model hợp pháp từ HuggingFace."

### "Tại sao không dùng luôn API của OpenAI cho nhanh?"
> "Nếu chỉ dùng ít thì API cloud nhanh hơn và tiện hơn. Nhưng khi volume
> tăng lên, chi phí cloud tăng tuyến tính còn chi phí host nội bộ gần như
> không đổi. Điểm hoà vốn chỉ khoảng 200-300 ảnh/tháng."

### "Em cần gì từ anh/chị?"
> "Em chỉ cần được phép dùng PC RTX 5070 để chạy, và khoảng 3-4 tuần để
> hoàn thiện. Không tốn thêm chi phí nào."

---

## NHỮNG LỖI NEWBIE BA HAY MẮC

| SAI | ĐÚNG |
|-----|------|
| Đọc tài liệu từ đầu đến cuối | Nói tóm tắt, chỉ mở tài liệu khi sếp hỏi chi tiết |
| Nói quá nhiều thuật ngữ kỹ thuật | Dùng từ đơn giản, ví dụ thực tế |
| Bắt đầu bằng giải pháp | Bắt đầu bằng VẤN ĐỀ và CHI PHÍ |
| Trình bày 30 phút liên tục | Nói 10 phút, dừng hỏi "anh/chị có câu hỏi gì không?" |
| Sợ nói "em không biết" | "Em sẽ tìm hiểu thêm và trả lời sau" là câu trả lời tốt |
| Hứa quá nhiều | Nói thực tế: "80-90% chất lượng" chứ không phải "bằng hoặc hơn" |
| Không chuẩn bị trước | Tập nói 1-2 lần trước gương hoặc với bạn |
| In tài liệu dài rồi đưa sếp | Gửi file trước 1 ngày để sếp đọc, hoặc đưa bản in khi họp |

---

## CHECKLIST TRƯỚC KHI VÀO HỌP

- [ ] Đã đọc lại tài liệu BA 1 lần
- [ ] Đã nhớ 3 con số: 300K/tháng (chi phí mình), 1.5-7 triệu/tháng (cloud), 80-95% (tiết kiệm)
- [ ] Đã tập nói phần tóm tắt 2 phút ít nhất 1 lần
- [ ] Đã chuẩn bị laptop/máy mở sẵn tài liệu BA (để chỉ khi sếp hỏi)
- [ ] Đã gửi tài liệu BA cho sếp trước (nếu có thể)
- [ ] Tâm thế: bình tĩnh, tự tin, không cần hoàn hảo
