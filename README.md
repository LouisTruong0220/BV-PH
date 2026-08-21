# Robot lễ tân — Bệnh viện Hùng Vương

App chạy trên **GreetingBot Nova**, phục vụ sự kiện ngày **22/08/2026** tại Bệnh viện
Hùng Vương, TP. Hồ Chí Minh:

- **Sáng** — Lễ đón nhận danh hiệu Anh hùng Lao động + Lễ khai trương Đơn vị HIFU
- **Chiều** — Hội thảo khoa học về điều trị không xâm lấn bằng sóng siêu âm hội tụ

---

## 🚀 Kỹ thuật viên bắt đầu từ đây

> ### 📘 Chưa từng làm việc với robot?
> Đọc **[`huong-dan-cai-dat.html`](huong-dan-cai-dat.html)** — hướng dẫn 8 bước, từ cài adb
> tới đặt tên điểm bản đồ, viết cho người không phải lập trình viên.
>
> ⚠ GitHub **không hiển thị** file HTML, nó chỉ hiện mã nguồn. Bấm nút **Download raw file**
> (mũi tên tải xuống ở góc phải) rồi mở bằng Chrome. Hoặc tải cả kho bằng
> **Code → Download ZIP**, giải nén, nháy đúp file đó.

**Chỉ cần cài lên robot, không cần build:**

1. Tải `apk/le-tan-benh-vien-hung-vuong-v1.1.apk`
2. Nối cáp USB vào **đầu robot**, dùng **adb 1.0.41** của Android SDK
   (⚠ **không** dùng `C:\Windows\adb.exe` bản 1.0.39 của PUDU — hai bản giết tiến trình của nhau)
   ```powershell
   adb install -r le-tan-benh-vien-hung-vuong-v1.1.apk
   ```
   Hoặc để script làm hết (tự tìm adb, tự tìm APK, tự kiểm tra lại):
   ```powershell
   .\tools\cai-len-robot.ps1
   ```
3. **Mở app từ RobotOS Home**, tuyệt đối không dùng `am start` — dùng `am start` thì
   `RobotApi` trả `handleApiDisabled`, mất cả dẫn đường lẫn giọng nói mà app không báo lỗi gì.
4. Quét bản đồ và đặt **15 điểm** (10 điểm dẫn đường + 5 điểm đi vòng) theo [`huong-dan-dat-diem-ban-do.md`](huong-dan-dat-diem-ban-do.md)
   — ⚠ đọc mục *"Quyết định phải chốt trước khi ra hiện trường"*, có một việc phải hỏi
   bệnh viện trước.
5. Tự kiểm: ở màn hai lựa chọn, **bấm giữ biểu tượng 🏥 góc trên trái 1,2 giây** → màn
   tự kiểm bản đồ, hỏi thẳng robot xem điểm nào đã đặt.

**Muốn xem app trông thế nào mà chưa có robot:** mở `demo/thu-nghiem.html` bằng Chrome —
có giả lập robot, bấm được nút dẫn đường.

| | |
|---|---|
| Trạng thái | **Bản demo + APK xong, 64/64 phép kiểm tự động đạt. CHƯA chạy trên robot thật, CHƯA khảo sát mặt bằng.** |
| APK | `apk/le-tan-benh-vien-hung-vuong-v1.1.apk` (6,8 MB) — bản 1.1, thêm tính năng đi vòng |
| Package | `vn.roboworld.hungvuong` — khác app Uông Bí (`vn.roboworld.benhvien`), hai app cài chung một máy được |
| appId OrionStar | `app_70eef22c4a6d4777af413ac942ea0153` |
| Ngày | 21/08/2026 |

> ⚠ **appId đang DÙNG CHUNG với app Bệnh viện Uông Bí.** Anh Trường chốt dùng lại số này.
> Hệ quả: nạp persona lên cổng OrionStar cho app này sẽ **đè lên** persona của app Uông Bí,
> và ngược lại. Hai app không chạy song song trên cổng được. Cần tách thì phải xin
> OrionStar cấp thêm một appId.

---

## Luồng màn hình

```
ĐI VÒNG  ⟳  robot đi liên tục qua Diem 1 → 2 → 3 → 4 → 5 → 1 …
   │        KHÔNG dừng ở điểm nào · vừa đi vừa chào (5 câu ngẫu nhiên, cách nhau 10 giây)
   │        màn hình chiếu biểu cảm emoji_wink_2.mp4
   │  khách chạm bất kỳ đâu  → robot DỪNG ngay
   ▼
HAI LỰA CHỌN ─────────────────────────────────────────────┐
   │                                                       │
   ├── 🧭 DẪN ĐƯỜNG                                        │
   │      → danh sách vị trí (tự lọc theo buổi sáng/chiều) │
   │      → chi tiết điểm (hiện sẵn lời robot sẽ nói)      │
   │      → đang dẫn — ROBOT IM LẶNG, chỉ chiếu biểu cảm   │
   │      → TỚI NƠI: đọc lời giới thiệu bệnh viện soạn     │
   │      → đếm ngược rồi ĐI TIẾP vòng của nó              │
   │                                                       │
   └── 💬 GIAO TIẾP AI                                      │
          → chọn "Đại biểu" hay "Khách VIP"                │
          → phát ĐÚNG lời chào của loại khách đó           │
          → trò chuyện: thẻ câu hỏi sẵn · gõ chữ · nói mic │
                                                           │
   Hai nút bệnh viện yêu cầu thêm, ở hàng dưới ────────────┘
     📣 Mời khách vào hội trường  → đọc lời mời ổn định chỗ ngồi
     🔬 Tư vấn thực hiện HIFU     → 2 nhánh → hỏi có dẫn đường không → dẫn

   ⟵ 30 GIÂY không ai thao tác → về màn chờ và ĐI TIẾP
```

**Lời chào đại biểu luân phiên hai câu.** Bệnh viện cung cấp hai biến thể; app đổi qua lại
để hai người đứng cạnh nhau không nghe y hệt một câu — robot phát băng nghe rất giả.

**Màn chờ dùng `emoji_wink_2.mp4`** theo anh Trường chốt. Muốn xoay vòng nhiều clip thì
thêm tên vào mảng `BIEU_CAM_CHO` trong `khung-app.html`.

**Sáng khác chiều.** Ngày 22/08 có HAI sự kiện, và bệnh viện soạn lời riêng cho từng cái.
App tự chọn theo **giờ máy** (mốc 12 giờ), lễ tân không phải bấm gì:

| | Trước 12 giờ | Sau 12 giờ |
|---|---|---|
| Lời chào đại biểu | Lễ đón nhận danh hiệu Anh hùng Lao động | Hội thảo khoa học HIFU |
| Câu chào lúc đi vòng | `di_vong.chao` | `di_vong.chao_chieu` |
| Nút 📣 Mời khách | `moi_vao_hoi_truong` | `moi_vao_hoi_thao` |
| Danh sách điểm dẫn đường | các đích `buoi: "sang"` | các đích `buoi: "chieu"` |

⚠ Muốn thử lời buổi chiều mà đang là buổi sáng thì **đổi giờ máy tính**, đừng sửa mã.

---

## ⟳ Đi vòng quanh sự kiện

Anh Trường chốt 21/08/2026. Robot không đứng một chỗ chờ khách tới nữa — nó đi liên tục
quanh sảnh và chào khách dọc đường.

**Cách chỉnh:** mọi con số nằm trong `DI_VONG` ở `dung-du-lieu.py`, sửa xong chạy
`dung-du-lieu.py` rồi `dung-app.py`. **Không phải build lại APK** nếu chỉ đổi tên điểm,
đổi câu chào hay đổi thời gian.

| Khai báo | Đang đặt | Nghĩa |
|---|---|---|
| `diem` | `Diem 1`…`Diem 5` | Thứ tự trong danh sách **chính là lộ trình**. Đặt thành vòng khép kín, đừng đặt kiểu đi rồi quay đầu |
| `cach_chao_giay` | 10 | Nghỉ bao lâu giữa hai câu chào — tính **từ lúc đọc xong**, không phải từ lúc bắt đầu đọc |
| `cho_khach_giay` | 30 | Vắng người bao lâu thì bỏ màn hình mà đi tiếp |
| `toc_do_thang` | 0,5 m/s | Mặc định hãng là 0,7 — nhanh so với sảnh đông người đứng nói chuyện |
| `toc_do_xoay` | 0,8 rad/s | Mặc định hãng là 1,2 |
| `sai_so_met` | 1,0 | Chỉ dùng cho lối dự phòng. Để 0,2 như dẫn khách là mỗi điểm robot khựng một nhịp thấy rõ |
| `chao` / `chao_chieu` | 5 câu mỗi bộ | Bốc **ngẫu nhiên**, hết một lượt mới xáo lại, không để hai câu giống nhau liền nhau |

### Hai lối đi, robot tự chọn

**Lối 1 — `startCruise` của hãng.** Đọc bytecode `robotservice.jar` thấy nó gói tham số vào
`CruiseParams`: `route` · `startPoint` · `dockingPoints` · `linearSpeed` · `angularSpeed` ·
`multipleWaitTime`.

> ⚠ **`dockingPoints` là danh sách chỉ số những điểm robot PHẢI DỪNG LẠI.** App để **rỗng**
> — đó chính là cách làm được yêu cầu "không dừng ở mỗi điểm". Đừng nhét chỉ số vào đó
> "cho đủ", nhét vào là robot đứng lại ở từng điểm.

**Lối 2 — nối từng lệnh `startNavigation`.** Tới điểm là bắn ngay lệnh đi điểm kế, không
nghỉ một nhịp nào. Robot vẫn khựng lại rất ngắn ở mỗi điểm vì SDK không có khái niệm
"điểm đi ngang qua", nhưng để sai số một mét thì gần như không thấy.

**Vì sao phải có lối 2:** `startCruise` **chưa từng chạy trên máy thật**. Cả OrionStar lẫn
PUDU đều đã có tiền lệ nhận lệnh, trả mã dương, rồi không làm gì và cũng không báo lỗi.
Nên `DiVong.kt` **không tin lời API nói mà đo**: cứ hai giây hỏi `getCurrentPose()`, hai
mươi giây robot chưa nhích nổi 30 cm thì coi như lối 1 chết, tự chuyển sang lối 2. Người
vận hành không phải biết gì về chuyện này — xem log `BVDiVong` nếu muốn biết đang đi lối nào.

### Chia việc giữa hai tầng

| | Lo chuyện gì |
|---|---|
| `DiVong.kt` (Kotlin) | Giữ cho robot còn đang đi. Chọn lối 1 / lối 2. Gặp lỗi thì bỏ qua điểm đó, thử điểm kế sau 12 giây; hỏng 5 lần liền thì nghỉ 1 phút |
| `khung-app.html` (web) | Quyết định **khi nào** được đi (chỉ khi đang ở màn chờ) và **nói gì** dọc đường |

Ở lớp web có một **đồng hồ canh gác** chạy 2 giây một nhịp (`dvNhipCanhGac`). Nó là thứ
**duy nhất** ra lệnh cho robot đi, nên mọi cách robot có thể chết đứng đều tự hồi phục qua
đó: RobotOS chưa kết nối xong lúc mới mở app · robot bị hệ thống treo rồi thả · Kotlin gặp
lỗi tự tắt vòng đi. Không có nó thì mỗi chỗ phải tự đoán thời điểm — mà đoán là sai.

### Đèn báo cho kỹ thuật viên

Góc dưới trái màn chờ có một chấm nhỏ: **xanh nhấp nháy** = đang đi, **cam đứng yên** =
chưa đi được. Bên cạnh là dòng chữ mờ cho biết đang tới điểm nào. Cố ý làm nhỏ và mờ —
khách nhìn vào chỉ thấy một chấm sáng.

---

## Nguồn dữ liệu

Toàn bộ nội dung robot nói **lấy nguyên văn từ tài liệu Bệnh viện Hùng Vương cung cấp
ngày 20–21/08/2026**, chỉ chuẩn hoá cách viết số sang chữ (robot đọc chữ số sai nhịp).
**39 cặp hỏi đáp**, phủ cả hai sự kiện của ngày 22/08:

| Tài liệu bệnh viện | Vào đâu trong app |
|---|---|
| `Noi dung cai dat Robot 4 HIFU edit 200826.docx` — PHẦN A | 10 kịch bản chào hỏi, lời chào đại biểu/VIP |
| cùng file — PHẦN B1/B2/B3 | 25 cặp hỏi đáp (sự kiện · bệnh viện · kỹ thuật HIFU) |
| **`Noi dung cai dat Robot - HTKH HIFU_s2.docx`** — PHẦN A | lời chào + lời mời riêng cho **hội thảo chiều** |
| cùng file — PHẦN B1 | **12 cặp hỏi đáp về Hội thảo khoa học** (nhóm `hoi-thao`) |
| cùng file — PHẦN B2 | 2 cặp: tiên phong HIFU · bệnh viện đầu tư thế nào |
| cùng file — PHẦN C | 8 bước quy trình điều trị |
| `Noi dung cai dat Robot_ địa điểm.docx` — PHẦN C | 9 đích dẫn đường + lời giới thiệu khi tới nơi |
| cùng file — PHẦN D | Hai nút thêm: mời khách · tư vấn HIFU hai nhánh |

**Không thêm dữ kiện nào bệnh viện chưa cung cấp.** Những thứ còn thiếu (wifi, nhà vệ sinh,
bãi xe, căn tin, giá điều trị) app **nói thẳng là chưa có thông tin** thay vì đoán —
xem `CHUA_CO` trong `dung-du-lieu.py`.

---

## Dây chuyền dựng

```powershell
cd D:\RBW_Claude\11-app-nova\le-tan-benh-vien-hung-vuong
python dung-du-lieu.py      # bảng dữ liệu  → du-lieu/app-data.json   (chỉ khi nội dung đổi)
python dung-app.py          # HTML + JSON   → demo/*.html + rải sang android assets
node tools\thu-app.mjs      # 43 phép kiểm tự động + ảnh soi từng bước
.\tools\build-apk.ps1       # → android\app\build\outputs\apk\debug\app-debug.apk
```

`dung-du-lieu.py` có **cổng chất lượng**: câu robot đọc mà còn chữ số, đích trỏ tới điểm
không có thật, hỏi đáp thiếu cách hỏi — script **DỪNG**, không sinh file.

`dung-app.py` sinh **hai** bản HTML: `demo/index.html` (bản sạch, đúng cái vào APK) và
`demo/thu-nghiem.html` (bản sạch + giả lập robot). Giả lập **không** rải sang android assets.

Xong thì copy tay APK sang `apk/…-vX.Y.apk` (script không tự đổi tên).

---

## Sửa nội dung ở đâu

| Muốn đổi | Sửa file | Rồi chạy |
|---|---|---|
| Lời chào, câu hỏi đáp, lời dẫn đường | `dung-du-lieu.py` | `dung-du-lieu.py` + `dung-app.py` |
| Tên điểm bản đồ, chỗ robot về đứng | `dung-du-lieu.py` → `DIEM`, `DIEM_VE_CHO` | như trên |
| Clip biểu cảm màn chờ | `khung-app.html` → `BIEU_CAM_CHO` | `dung-app.py` |
| Giao diện, bố cục, luồng màn hình | `khung-app.html` | `dung-app.py` |
| Lớp chặn an toàn, persona gửi mô hình | `MainApplication.kt` **và** `gia-lap-robot.js` | build lại APK |

**Chỉ khi đụng vào `.kt` mới phải build lại APK.** Đổi nội dung và giao diện thì chạy
`dung-app.py` rồi đẩy lại `index.html` là đủ:

```powershell
adb push demo\index.html /sdcard/  # rồi cài lại APK, hoặc build lại — assets nằm trong APK
```

---

## Tầng AI — chép lối đã chạy được ở hai app trước

Bốn thứ then chốt, **đừng đổi nếu chưa đọc chú thích tại chỗ**:

1. **Agent SDK lấy từ GÓI OFFLINE của hãng**, không lấy JitPack. `app/libs/sdk-0.4.7.aar` +
   `agent-base-0.2.10.aar`. Mọi bản trên JitPack ghi cứng sai tên gói dịch vụ nên
   `AgentCore.*` lặng lẽ không làm gì — không lỗi, không callback, không log.
2. **`businessInfo` phải là `null`, không được là `""`.** Chuỗi rỗng thì máy chủ trả
   `status=2, result=null` sau ~355 ms, không lỗi không lý do.
3. **Bốn công tắc của hãng đều mặc định SAI với app này** — đặt trong `AppAgent.onCreate`:
   `isEnableVoiceBar=false` · `isDisablePlan=true` · `isMicrophoneMuted=true` ·
   `isEnableWakeFree=false`.
4. **Việc an toàn chặn bằng MÃ, không chặn bằng lời dặn trong prompt.**

### Đường đi của một câu hỏi — `TraLoi.kt`

```
nghe được câu (onASRResult) hoặc gõ chữ (CAU.hoiRobot) — CÙNG MỘT ĐƯỜNG
  → ① CẤP CỨU?          → hô ngay gọi nhân viên y tế, KHÔNG hỏi mô hình
  → ② xin ý kiến y tế?   → từ chối, KHÔNG hỏi mô hình
  → ③ chưa có dữ liệu?   → nói thẳng chưa có, KHÔNG hỏi mô hình
  → ④ tra kho hỏi đáp tại chỗ, lấy MỨC TIN CẬY
  → ⑤ CHẮC CHẮN → đọc thẳng câu bệnh viện duyệt, KHÔNG hỏi mô hình   ← lối tắt
  → ⑥ chưa chắc → hỏi mô hình kèm ĐÚNG danh sách ứng viên
  → ⑦ KIỂM dòng DAP_ID → mới cho robot mở miệng
```

**Lối tắt ở bước ⑤ là khác biệt lớn nhất so với hai app trước.** Ở đây mỗi câu hỏi đã có
sẵn một câu trả lời bệnh viện duyệt từng chữ. Nội dung y khoa không phải thứ để mô hình
diễn đạt lại — lệch một con số (*"bảy mươi phần trăm"* thành *"chín mươi phần trăm"*) là
sai hẳn thông tin y tế, trước mặt một hội trường toàn bác sĩ. Lối tắt xử lý phần lớn câu
hỏi trong ngày, vừa an toàn hơn vừa nhanh hơn vì không phải chờ mạng.

Khi có gọi mô hình, nó cũng **chỉ được chọn id**; câu trả lời do app đọc nguyên văn từ
`window.docDapAn(id)`. Mô hình trả id không nằm trong danh sách ứng viên, hoặc quên dòng
`DAP_ID`, thì app **vứt cả câu trả lời** và đọc câu từ chối của mình.

### ⚠ Lớp chặn ở đây KHÁC app Uông Bí — đọc trước khi copy sang

Ba khác biệt cố ý, không phải bỏ sót:

**1. Không chặn "mấy giờ" và "số điện thoại".** App Uông Bí chặn hai cụm này vì bệnh viện
đó không cung cấp giờ làm việc. Ở đây *"mấy giờ khai mạc"*, *"mấy giờ trao danh hiệu"*,
*"liên hệ ở đâu"* là những câu bệnh viện **đã soạn sẵn câu trả lời** — chặn là robot từ
chối đúng những câu khách hỏi nhiều nhất trong ngày.

**2. Chặn xin ý kiến y tế phải khớp HAI VẾ** (đại từ ngôi thứ nhất **và** động từ xin ý
kiến), không dùng một regex gộp. Lý do: *"HIFU có nguy hiểm không"* là câu bệnh viện đã
duyệt câu trả lời, còn *"trường hợp của tôi có làm được không"* mới là tư vấn cá nhân.
Regex gộp kiểu Uông Bí chặn nhầm cả hai.

**3. Cấp cứu: hô to, KHÔNG chỉ đường.** Bệnh viện chưa cung cấp vị trí khoa cấp cứu, mà
đây cũng không phải khu khám bệnh. Chỉ sai chỗ trong tình huống cấp cứu còn tệ hơn nói
thẳng là mình không biết.

**⚠ Ba biểu thức chặn nằm ở HAI nơi** — `MainApplication.kt` và `gia-lap-robot.js`.
Sửa một bên phải sửa cả hai, không thì bản thử trên máy tính nói khác robot thật.

---

## Bộ thử tự động

```powershell
node tools\thu-app.mjs
```

64 phép kiểm, chạy trọn mười bước của app trên bản giả lập, kiểm bằng **trạng thái thật**
(màn nào đang hiện, robot đọc câu gì, lệnh nào gửi xuống Kotlin) chứ không chỉ chụp ảnh.
Ảnh soi từng bước ra `demo/anh-soi/`.

Nó bắt đúng loại lỗi hay dính trên Nova: nút bị co về kích thước 0, chồng hai màn cùng lúc,
lời thoại còn sót chữ số, tên điểm bản đồ lỡ có dấu tiếng Việt.

Phần 9 thử **cả vòng đi**: robot tự lăn bánh ở màn chờ · tới điểm là đi tiếp chứ không dừng ·
khách chạm màn hình thì dừng ngay · đủ ba mươi giây vắng người thì đi tiếp. Bộ giả lập
dựng lại đúng chữ ký và đúng trình tự báo trạng thái của `DiVong.kt`.

Trong đó có **bộ thử hồi quy cho bộ tìm kiếm** — cặp câu *"mấy giờ khai mạc"* (buổi lễ) và
*"mấy giờ khai trương"* (Đơn vị HIFU) chỉ khác nhau một tiếng, đã từng làm robot hỏi lại
một câu mà nó thừa sức trả lời. Đổi ngưỡng hay đổi cách chấm điểm thì **chạy lại bộ thử**.

---

## Ba cái bẫy của Nova — dính là mất buổi

1. **Màn Nova ngang 1920×1080 @560dpi → WebView chỉ cho khung 548×308 CSS px.** Cỡ chữ gốc
   tính ra 4,56 px, Chrome nâng lên sàn 8 px, mọi thứ to lên 1,75 lần và tràn ra ngoài thẻ.
   Chữa bằng `<meta viewport width=1920>` + bốn setting trong `MainActivity`. **Đừng đụng
   vào bốn dòng đó.**
2. **`robotservice.jar` cần Gson nhưng không đóng gói kèm.** Thiếu dòng gson trong
   `dependencies` thì `RobotApi.connectServer` ném `ClassNotFoundException`.
3. **Khai quyền micro trong Manifest CHƯA ĐỦ** — phải gọi `requestPermissions()` lúc chạy.

**Soi giao diện trên robot:**
```powershell
adb shell cat /proc/net/unix | Select-String webview_devtools_remote
adb forward tcp:9222 localabstract:webview_devtools_remote_<pid>
# rồi mở chrome://inspect trên máy tính
```
Chụp màn hình: `adb shell screencap -p /sdcard/_s.png` rồi `adb pull` — **không** dùng
`adb exec-out screencap -p > file.png`, PowerShell chèn BOM làm hỏng PNG.

---

## Tự kiểm nhanh

Trong DevTools của WebView (hoặc Console của Chrome khi mở `demo/index.html`):

```js
CAU.kiemTraBanDo()              // mười điểm bản đồ đã đặt đúng tên chưa
CAU.thongTinAI()                // appId, Agent SDK bind chưa, mic đang mở/tắt
CAU.thuLLM('Xin chào', true)    // mô hình đám mây có trả lời không

traCuu('hifu là gì').muc                  // → 'chac'
traCuu('mấy giờ khai mạc').ung_vien[0].id // → 2   (buổi lễ, KHÔNG phải khai trương)
traCuu('mấy giờ khai trương').ung_vien[0].id // → 5   (Đơn vị HIFU)
traCuu('thời tiết hôm nay thế nào').muc   // → 'khong-thay'  (phải nói không biết)
docDapAn(10)                              // → định nghĩa HIFU nguyên văn bệnh viện
```

---

## ⚠ Việc còn treo

1. **Chưa chạy trên robot thật, chưa khảo sát mặt bằng.** Toàn bộ 64 phép kiểm chạy trên
   giả lập — nó dựng lại đúng chữ ký hàm và trình tự báo trạng thái của `Cau.kt`, nhưng
   **không thay được một lần chạy thật**.
2. **Chưa biết `startCruise` có chạy trên máy Nova không.** Đây là việc đầu tiên phải làm
   khi có robot trong tay: mở app, để yên ở màn chờ, xem log `adb logcat -s BVDiVong`.
   Thấy dòng *"Đo được robot đã đi … m"* là lối 1 chạy thật; thấy *"Hai mươi giây robot
   không nhúc nhích"* là đã tự chuyển sang lối nối điểm — vẫn đi được, chỉ hơi khựng ở
   mỗi điểm. Cả hai đều chấp nhận được, nhưng phải **biết** mình đang ở lối nào.
3. **Năm điểm đi vòng đặt ở đâu là việc của khảo sát mặt bằng.** Chốt lộ trình vòng khép
   kín quanh khu vực đón khách, tránh lối thoát hiểm và tránh cắt ngang chỗ chụp hình
   backdrop. Sảnh chưa đủ rộng cho năm điểm thì bớt xuống ba — sửa `DI_VONG['diem']`.
4. **Chưa chốt robot đặt ở tầng nào** — xem
   [`huong-dan-dat-diem-ban-do.md`](huong-dan-dat-diem-ban-do.md). Quyết định này chi phối
   toàn bộ danh sách điểm bản đồ.
5. **Chưa có gì cho phần trình chiếu.** Câu trả lời về chương trình có nhắc *"Quý vị có thể
   xem chương trình chi tiết trên màn hình của tôi"* — nhưng chưa có slide nào. Cần ảnh
   **1920×1080 nằm ngang**, nếu không robot nói một đằng màn hình một nẻo.
6. **Chưa có nhóm hậu cần** — nhà vệ sinh, thang máy, bãi xe, wifi, căn tin. App đang trả
   lời "chưa có thông tin"; bệnh viện cung cấp thì thêm vào `HOI_DAP` trong `dung-du-lieu.py`.
7. **Chưa nạp persona lên cổng OrionStar.** App tự tra cứu và tự đọc câu trả lời nên vẫn
   chạy đủ chức năng khi chưa nạp; persona chỉ là đường lui. Nạp thì lưu ý appId đang dùng
   chung với app Uông Bí (xem cảnh báo ở đầu trang).

8. **Đã gỡ được một mâu thuẫn trong tài liệu gốc.** Bản 21/08 chỉ ghi *"không thu phí"*,
   bản s2 lại ghi *"300.000 đồng cấp CME"* — nay thấy rõ là **hai câu hỏi khác nhau**:
   dự hội thảo miễn phí, còn muốn lấy chứng chỉ CME (1,5 giờ tín chỉ) thì đóng ba trăm
   nghìn. App tách thành hai mục hỏi đáp riêng và có phép kiểm bảo đảm chúng không lẫn
   vào nhau. **Vẫn nên để bệnh viện xác nhận lại cách hiểu này trước sáng 22/08.**
9. **Phần song ngữ tiếng Anh vẫn chưa bật.** Cả hai bản tài liệu đều có câu chào tiếng Anh
   nhưng ghi rõ *"tuỳ chọn — nếu Ban Giám đốc kích hoạt"*. Chưa ai chốt nên chưa đưa vào app.
