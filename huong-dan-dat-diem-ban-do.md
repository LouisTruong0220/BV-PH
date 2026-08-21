# Hướng dẫn đặt điểm bản đồ — Robot lễ tân Bệnh viện Hùng Vương

**In trang này ra mang theo khi đi khảo sát.**

Robot chỉ đi được tới những điểm đã đặt tên sẵn trên bản đồ. Tên điểm phải trùng
**TỪNG KÝ TỰ** với bảng dưới đây — sai một ký tự là robot báo lỗi
`ERROR_DESTINATION_NOT_EXIST` và đứng im, không giải thích gì cả.

---

## Mười điểm DẪN ĐƯỜNG

| # | Tên điểm — **gõ đúng thế này** | Đặt ở đâu | Bắt buộc |
|---|---|---|---|
| 1 | `Le tan` | Chỗ robot đứng đợi khách giữa hai lượt | ✔ |
| 2 | `Tram sac` | Vị trí trạm sạc | ✔ |
| 3 | `Hoi truong L11` | Trước cửa Hội trường lầu 11, Toà nhà Bách Hợp | ✔ |
| 4 | `Don vi HIFU` | Đơn vị HIFU — tầng trệt toà nhà Cát Tường | ✔ |
| 5 | `Quay CSKH` | Quầy chăm sóc khách hàng | ✔ |
| 6 | `Phong MRI` | Phòng chụp cộng hưởng từ — toà nhà Cát Tường | ✔ |
| 7 | `Phong 12 khu B` | Phòng 12, Khu B, toà nhà Cát Tường (xét nghiệm) | ✔ |
| 8 | `Phong 8 khu B` | Phòng 8, Khu B, toà nhà Cát Tường (siêu âm) | ✔ |
| 9 | `Dieu tri trong ngay` | Khoa điều trị trong ngày | ✔ |
| 10 | `Ban tiep don` | Bàn tiếp đón / ghi danh của sự kiện | ✔ |

**Quy tắc gõ tên:**

- **Không dấu tiếng Việt.** `Hoi truong L11`, không phải `Hội trường L11`.
- **Đúng hoa thường.** `Quay CSKH` — chữ Q hoa, `uay` thường, `CSKH` hoa.
- **Đúng một dấu cách** giữa các chữ, không có dấu cách thừa ở đầu hay cuối.
- Không đổi tên cho "đẹp hơn". Muốn đổi thì sửa bảng `DIEM` trong `dung-du-lieu.py`
  rồi chạy lại `dung-du-lieu.py` + `dung-app.py` — **không phải build lại APK**.

---

## Năm điểm ĐI VÒNG — đặt thêm, khác với mười điểm trên

Robot không đứng một chỗ chờ khách nữa. Nó **đi liên tục** theo vòng
`Diem 1 → 2 → 3 → 4 → 5 → 1 → …`, vừa đi vừa chào khách, khách chạm màn hình thì dừng lại
phục vụ, ba mươi giây không ai thao tác thì đi tiếp.

| # | Tên điểm — **gõ đúng thế này** | Đặt ở đâu |
|---|---|---|
| 11 | `Diem 1` | Chọn năm chỗ **rải đều quanh khu vực đón khách**, nối lại thành **vòng khép kín** |
| 12 | `Diem 2` | |
| 13 | `Diem 3` | |
| 14 | `Diem 4` | |
| 15 | `Diem 5` | |

**Chữ D viết hoa, chữ `iem` thường, một dấu cách trước số.** `Diem 1` — không phải
`diem 1`, không phải `Điểm 1`, không phải `Diem1`.

### Chọn chỗ đặt năm điểm thế nào

- **Vòng khép kín, không phải đường đi rồi quay đầu.** Điểm 5 phải nằm gần Điểm 1. Đặt
  thành một đường thẳng là robot đi tới cuối rồi quay ngoắt lại — nhìn rất kỳ, và mỗi lần
  quay đầu robot đứng lại mấy giây.
- **Tránh lối thoát hiểm và cửa ra vào.** Robot dừng giữa lối thoát hiểm là chuyện an toàn,
  không phải chuyện thẩm mỹ.
- **Tránh cắt ngang khu chụp hình backdrop.** Đại biểu đang chụp hình mà robot đi ngang
  qua là hỏng ảnh của người ta.
- **Cách tường và bàn ghi danh ít nhất một mét.** Robot vòng qua điểm chứ không đỗ vào đó.
- **Sảnh nhỏ thì bớt xuống ba điểm.** Không có luật nào bắt phải đủ năm. Sửa danh sách
  `DI_VONG['diem']` trong `dung-du-lieu.py` rồi chạy lại hai script — **không build lại APK**.

### Kiểm lại sau khi đặt

Màn tự kiểm (bấm giữ 🏥 góc trên trái 1,2 giây) **soi cả năm điểm này**. Đây là chỗ bắt
buộc phải xem, vì thiếu điểm đi vòng là kiểu hỏng **im lặng nhất**: robot vẫn đi bình
thường, chỉ lặng lẽ bỏ qua đúng cái điểm gõ sai tên, không báo lỗi, không ai biết cho tới
lúc ngồi xem lại đường robot đã đi.

Kiểm thêm bằng mắt: mở app, để yên ở màn chờ chừng một phút. Robot phải **tự lăn bánh**
mà không cần ai bấm gì, và ở góc dưới trái màn hình có **chấm xanh nhấp nháy** kèm dòng
chữ mờ cho biết đang đi tới điểm nào. Chấm **cam đứng yên** nghĩa là robot chưa đi được —
thường vì chưa định vị.

### Muốn robot đứng yên như cũ

Sửa `DI_VONG['bat']` thành `False` trong `dung-du-lieu.py`, chạy lại hai script, đẩy lại
`index.html`. App quay về nếp cũ: đứng đợi ở `Le tan`, dẫn xong thì tự về chỗ.

---

## ⚠ Quyết định phải chốt trước khi ra hiện trường

**Hội trường ở lầu 11. Robot Nova KHÔNG tự đi thang máy.**

Nghĩa là robot chỉ hoạt động được **trong một tầng**. Phải chọn một trong hai:

| Phương án | Robot đặt ở đâu | Đặt được điểm nào |
|---|---|---|
| **A — Đón khách ở tầng trệt** | Sảnh tầng trệt, gần thang máy | `Le tan`, `Ban tiep don`, `Don vi HIFU`, `Quay CSKH`, `Phong MRI`, `Phong 12 khu B`, `Phong 8 khu B`, `Dieu tri trong ngay` — **không có** `Hoi truong L11` |
| **B — Đón khách ngay tại lầu 11** | Sảnh lầu 11, trước cửa hội trường | `Le tan`, `Hoi truong L11`, `Ban tiep don` (nếu bàn ghi danh đặt trên lầu) — **không có** các phòng ở Cát Tường |

Không có phương án nào phủ được cả hai tầng bằng một con robot.

**Đề xuất của Roboworld:** phương án **B cho buổi lễ sáng và hội thảo chiều** (khách chủ yếu
cần vào hội trường), rồi hạ robot xuống tầng trệt nếu bệnh viện muốn phục vụ người bệnh
tìm đơn vị HIFU. Mỗi lần đổi tầng phải **quét lại bản đồ**.

Bệnh viện chốt phương án nào thì báo lại — kỹ thuật chỉ đặt những điểm dùng được ở tầng đó,
những điểm còn lại app tự ẩn nút (không đặt thì bấm vào robot sẽ báo lỗi trước mặt khách).

---

## Thứ tự làm tại hiện trường

1. **Dựng xong mặt bằng trước** — bàn ghi danh, standee, backdrop, bàn ghế đã kê đúng chỗ.
   Quét bản đồ trước rồi mới kê đồ là robot đâm vào những thứ nó chưa biết, hoặc dừng
   giữa đường.
2. Quét bản đồ toàn khu vực robot sẽ đi.
3. Đặt **mười lăm điểm** theo hai bảng trên — mười điểm dẫn đường + năm điểm đi vòng.
4. **Định vị robot** — chưa định vị thì mọi lệnh dẫn đường đều lỗi `ERROR_NOT_ESTIMATE`.
5. **Tự kiểm bằng chính app**, đừng nhìn bằng mắt:
   - Mở app → ở màn hai lựa chọn, **bấm giữ biểu tượng 🏥 góc trên trái 1,2 giây**
   - Màn tự kiểm hiện ra, hỏi thẳng robot xem đã định vị chưa và những điểm nào đã đặt
   - Điểm nào ✘ là **chưa có trên bản đồ**, phải đặt lại
6. Chạy thử ít nhất một lượt dẫn đường thật, đi hết quãng đường, nghe robot đọc lời
   giới thiệu khi tới nơi.

---

## Điều kiện mặt bằng

| Yếu tố | Yêu cầu |
|---|---|
| Lối đi hẹp nhất | **70 cm** — giữ thông thoáng, không dây điện, không bậc thềm, không thảm dày |
| Mặt sàn | Cứng, phẳng, không dốc. Sàn mới lau bóng làm robot trượt bánh |
| Trạm sạc | Sát tường, chừa trống **1,6 m phía trước** và **1,6–5 m hai bên**, có ổ điện |
| Wi-Fi | Phủ toàn khu vực robot chạy (cần cho phần trò chuyện AI) |
| Vách kính, vật thấp | Báo trước để đánh dấu vạch cấm trên bản đồ |
| Ánh sáng | Tránh nắng chiếu thẳng vào cảm biến |

---

## Nếu robot không đi

| Hiện tượng | Nguyên nhân thường gặp |
|---|---|
| Bấm nút dẫn, robot đứng im, màn báo "Chưa có điểm này trên bản đồ" | Tên điểm gõ sai — đối chiếu lại bảng trên, để ý dấu cách và hoa thường |
| Báo "Robot chưa định vị được" | Chưa định vị sau khi khởi động. Định vị lại trên màn hình hãng |
| Nút dẫn đường bị mờ, không bấm được | App chưa kết nối RobotOS. **Mở app từ RobotOS Home**, đừng dùng `am start` |
| Robot đi được nửa đường rồi dừng | Vật cản trên tuyến, hoặc bản đồ quét trước khi kê bàn ghế |
