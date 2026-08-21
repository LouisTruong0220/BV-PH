# Robot lễ tân — Bệnh viện Hùng Vương

App chạy trên **GreetingBot Nova**, phục vụ sự kiện ngày **22/08/2026** tại Bệnh viện
Hùng Vương, TP. Hồ Chí Minh:

- **Sáng** — Lễ đón nhận danh hiệu Anh hùng Lao động + Lễ khai trương Đơn vị HIFU
- **Chiều** — Hội thảo khoa học về điều trị không xâm lấn bằng sóng siêu âm hội tụ

---

## 🚀 Kỹ thuật viên bắt đầu từ đây

**Chỉ cần cài lên robot, không cần build:**

1. Tải `apk/le-tan-benh-vien-hung-vuong-v1.0.apk`
2. Nối cáp USB vào **đầu robot**, dùng **adb 1.0.41** của Android SDK
   (⚠ **không** dùng `C:\Windows\adb.exe` bản 1.0.39 của PUDU — hai bản giết tiến trình của nhau)
   ```powershell
   adb install -r le-tan-benh-vien-hung-vuong-v1.0.apk
   ```
3. **Mở app từ RobotOS Home**, tuyệt đối không dùng `am start` — dùng `am start` thì
   `RobotApi` trả `handleApiDisabled`, mất cả dẫn đường lẫn giọng nói mà app không báo lỗi gì.
4. Quét bản đồ và đặt **10 điểm** theo [`huong-dan-dat-diem-ban-do.md`](huong-dan-dat-diem-ban-do.md)
   — ⚠ đọc mục *"Quyết định phải chốt trước khi ra hiện trường"*, có một việc phải hỏi
   bệnh viện trước.
5. Tự kiểm: ở màn hai lựa chọn, **bấm giữ biểu tượng 🏥 góc trên trái 1,2 giây** → màn
   tự kiểm bản đồ, hỏi thẳng robot xem điểm nào đã đặt.

**Muốn xem app trông thế nào mà chưa có robot:** mở `demo/thu-nghiem.html` bằng Chrome —
có giả lập robot, bấm được nút dẫn đường.

| | |
|---|---|
| Trạng thái | **Bản demo + APK xong, 43/43 phép kiểm tự động đạt. CHƯA chạy trên robot thật, CHƯA khảo sát mặt bằng.** |
| APK | `apk/le-tan-benh-vien-hung-vuong-v1.0.apk` (6,8 MB) |
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
màn chờ  (chiếu emoji_wink_2.mp4, lặp)
   │  chạm bất kỳ đâu
   ▼
HAI LỰA CHỌN ─────────────────────────────────────────────┐
   │                                                       │
   ├── 🧭 DẪN ĐƯỜNG                                        │
   │      → danh sách vị trí (tự lọc theo buổi sáng/chiều) │
   │      → chi tiết điểm (hiện sẵn lời robot sẽ nói)      │
   │      → đang dẫn — ROBOT IM LẶNG, chỉ chiếu biểu cảm   │
   │      → TỚI NƠI: đọc lời giới thiệu bệnh viện soạn     │
   │      → tự về chỗ đứng đợi                             │
   │                                                       │
   └── 💬 GIAO TIẾP AI                                      │
          → chọn "Đại biểu" hay "Khách VIP"                │
          → phát ĐÚNG lời chào của loại khách đó           │
          → trò chuyện: thẻ câu hỏi sẵn · gõ chữ · nói mic │
                                                           │
   Hai nút bệnh viện yêu cầu thêm, ở hàng dưới ────────────┘
     📣 Mời khách vào hội trường  → đọc lời mời ổn định chỗ ngồi
     🔬 Tư vấn thực hiện HIFU     → 2 nhánh → hỏi có dẫn đường không → dẫn
```

**Lời chào đại biểu luân phiên hai câu.** Bệnh viện cung cấp hai biến thể; app đổi qua lại
để hai người đứng cạnh nhau không nghe y hệt một câu — robot phát băng nghe rất giả.

**Màn chờ dùng `emoji_wink_2.mp4`** theo anh Trường chốt. Muốn xoay vòng nhiều clip thì
thêm tên vào mảng `BIEU_CAM_CHO` trong `khung-app.html`.

---

## Nguồn dữ liệu

Toàn bộ nội dung robot nói **lấy nguyên văn từ tài liệu Bệnh viện Hùng Vương cung cấp
ngày 20/08/2026**, chỉ chuẩn hoá cách viết số sang chữ (robot đọc chữ số sai nhịp):

| Tài liệu bệnh viện | Vào đâu trong app |
|---|---|
| `Noi dung cai dat Robot 4 HIFU edit 200826.docx` — PHẦN A | 10 kịch bản chào hỏi, lời chào đại biểu/VIP |
| cùng file — PHẦN B1/B2/B3 | 25 cặp hỏi đáp (sự kiện · bệnh viện · kỹ thuật HIFU) |
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

43 phép kiểm, chạy trọn tám bước của app trên bản giả lập, kiểm bằng **trạng thái thật**
(màn nào đang hiện, robot đọc câu gì, lệnh nào gửi xuống Kotlin) chứ không chỉ chụp ảnh.
Ảnh soi từng bước ra `demo/anh-soi/`.

Nó bắt đúng loại lỗi hay dính trên Nova: nút bị co về kích thước 0, chồng hai màn cùng lúc,
lời thoại còn sót chữ số, tên điểm bản đồ lỡ có dấu tiếng Việt.

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

1. **Chưa chạy trên robot thật, chưa khảo sát mặt bằng.** Toàn bộ 43 phép kiểm chạy trên
   giả lập — nó dựng lại đúng chữ ký hàm và trình tự báo trạng thái của `Cau.kt`, nhưng
   **không thay được một lần chạy thật**.
2. **Chưa chốt robot đặt ở tầng nào** — xem
   [`huong-dan-dat-diem-ban-do.md`](huong-dan-dat-diem-ban-do.md). Quyết định này chi phối
   toàn bộ danh sách điểm bản đồ.
3. **Chưa có gì cho phần trình chiếu.** Câu trả lời về chương trình có nhắc *"Quý vị có thể
   xem chương trình chi tiết trên màn hình của tôi"* — nhưng chưa có slide nào. Cần ảnh
   **1920×1080 nằm ngang**, nếu không robot nói một đằng màn hình một nẻo.
4. **Chưa có nhóm hậu cần** — nhà vệ sinh, thang máy, bãi xe, wifi, căn tin. App đang trả
   lời "chưa có thông tin"; bệnh viện cung cấp thì thêm vào `HOI_DAP` trong `dung-du-lieu.py`.
5. **Chưa nạp persona lên cổng OrionStar.** App tự tra cứu và tự đọc câu trả lời nên vẫn
   chạy đủ chức năng khi chưa nạp; persona chỉ là đường lui. Nạp thì lưu ý appId đang dùng
   chung với app Uông Bí (xem cảnh báo ở đầu trang).
