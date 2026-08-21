# -*- coding: utf-8 -*-
"""
dung-du-lieu.py — Bảng dữ liệu cho app robot lễ tân Bệnh viện Hùng Vương.

Nguồn (bệnh viện cung cấp 20/08/2026, lưu ở 10-project/Benh-vien-Hung-Vuong/tu-lieu/):
  · "Noi dung cai dat Robot 4 HIFU edit 200826.docx"  → PHẦN A chào hỏi · B1/B2/B3 hỏi đáp
                                                        · PHẦN C quy trình 8 bước
  · "Noi dung cai dat Robot_ địa điểm.docx"           → 9 điểm dẫn đường · 2 nút bấm thêm

Chạy:  python dung-du-lieu.py     → du-lieu/app-data.json
Rồi:   python dung-app.py         → demo/index.html + rải sang android assets

⚠ MỌI CÂU ROBOT ĐỌC ĐỀU LẤY NGUYÊN VĂN TỪ TÀI LIỆU BỆNH VIỆN, chỉ chuẩn hoá cách viết
  số sang chữ (robot đọc chữ số sẽ sai nhịp). Không thêm dữ kiện nào bệnh viện chưa cung cấp.
  Chỗ nào bệnh viện chưa cấp thì để "" và app sẽ nói "chưa có thông tin" — KHÔNG đoán.
"""
import io, json, os, sys, unicodedata

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
RA = os.path.join(HERE, "du-lieu", "app-data.json")

# ════════════════════════════════════════════════════════════════════
#  1. ĐIỂM TRÊN BẢN ĐỒ ROBOT
#     Tên viết KHÔNG DẤU, đúng hoa/thường, đúng một dấu cách — phải trùng TỪNG KÝ TỰ
#     với tên kỹ thuật đặt lúc quét bản đồ. Sai một ký tự là ERROR_DESTINATION_NOT_EXIST.
#     Xem huong-dan-dat-diem-ban-do.md
# ════════════════════════════════════════════════════════════════════
DIEM = {
    "hoi-truong":  "Hoi truong L11",
    "don-vi-hifu": "Don vi HIFU",
    "quay-cskh":   "Quay CSKH",
    "phong-mri":   "Phong MRI",
    "phong-12":    "Phong 12 khu B",
    "phong-8":     "Phong 8 khu B",
    "dieu-tri-ngay": "Dieu tri trong ngay",
    "ban-tiep-don": "Ban tiep don",
}
DIEM_VE_CHO = "Le tan"          # chỗ robot đứng đợi giữa hai lượt khách
DIEM_TRAM_SAC = "Tram sac"      # không dẫn tới, chỉ để màn tự kiểm đối chiếu

# ════════════════════════════════════════════════════════════════════
#  2. ĐÍCH DẪN ĐƯỜNG  (PHẦN C tài liệu địa điểm)
#
#  buoi: "sang" | "chieu" | "moi-luc"  — app lọc theo giờ máy, xem chonBuoi() trong HTML.
#  doc : lời robot đọc KHI TỚI NƠI, nguyên văn bệnh viện, số đã chuyển sang chữ.
# ════════════════════════════════════════════════════════════════════
DICH = [
    {
        "id": 1, "ma_bv": "C1", "buoi": "sang",
        "ten": "Hội trường lầu 11",
        "phu": "Lễ đón nhận danh hiệu Anh hùng Lao động",
        "icon": "🏛️", "diem": "hoi-truong",
        "tu_khoa": ["hội trường", "hoi truong", "lầu 11", "lau 11", "buổi lễ", "khai mạc",
                    "lễ đón nhận", "anh hùng lao động", "chỗ ngồi", "vào hội trường"],
        "doc": "Quý khách đã đến Hội trường lầu mười một Bệnh viện Hùng Vương. "
               "Chào mừng Quý vị đến dự Lễ đón nhận danh hiệu Anh hùng Lao động và Lễ khai trương "
               "Đơn vị điều trị không xâm lấn bằng sóng siêu âm hội tụ. "
               "Kính chúc Quý vị một ngày thật nhiều niềm vui!",
    },
    {
        "id": 2, "ma_bv": "C2.1", "buoi": "sang",
        "ten": "Đơn vị HIFU",
        "phu": "Buổi sáng — sau khi đón khách xong",
        "icon": "🔬", "diem": "don-vi-hifu",
        "tu_khoa": ["đơn vị hifu", "don vi hifu", "hifu", "khai trương đơn vị",
                    "điều trị không xâm lấn", "siêu âm hội tụ"],
        "doc": "Xin chào mừng Quý khách đã đến Đơn vị điều trị không xâm lấn bằng sóng siêu âm "
               "hội tụ, hay còn gọi là đơn vị HIFU. Xin chào đón Quý khách.",
    },
    {
        "id": 3, "ma_bv": "C2.2", "buoi": "chieu",
        "ten": "Hội trường lầu 11",
        "phu": "Hội thảo khoa học buổi chiều",
        "icon": "🏛️", "diem": "hoi-truong",
        "tu_khoa": ["hội trường", "hoi truong", "lầu 11", "lau 11", "hội thảo", "hoi thao",
                    "chỗ ngồi", "vào hội trường", "hội thảo khoa học"],
        "doc": "Quý khách đã đến Hội trường lầu mười một Bệnh viện Hùng Vương! "
               "Chào mừng Quý vị đến tham dự Hội thảo khoa học Điều trị không xâm lấn bằng sóng "
               "siêu âm hội tụ. Kính chúc Quý đại biểu có một ngày thật nhiều niềm vui và có những "
               "trải nghiệm, kiến thức bổ ích tại Hội thảo!",
    },
    {
        "id": 4, "ma_bv": "C3.1", "buoi": "moi-luc",
        "ten": "Đơn vị HIFU",
        "phu": "Tầng trệt toà nhà Cát Tường",
        "icon": "🔬", "diem": "don-vi-hifu",
        "tu_khoa": ["đơn vị hifu", "don vi hifu", "hifu", "điều trị hifu", "làm hifu",
                    "khoa phụ nội", "nội tiết"],
        "doc": "Đã đến Đơn vị điều trị không xâm lấn bằng sóng siêu âm hội tụ, "
               "hay còn gọi là đơn vị HIFU. Xin chào đón Quý đại biểu.",
    },
    {
        "id": 5, "ma_bv": "C3.2", "buoi": "moi-luc",
        "ten": "Quầy chăm sóc khách hàng",
        "phu": "Hướng dẫn và tư vấn dịch vụ",
        "icon": "💬", "diem": "quay-cskh",
        "tu_khoa": ["chăm sóc khách hàng", "cham soc khach hang", "cskh", "tư vấn", "tu van",
                    "hướng dẫn", "hỏi thông tin", "đăng ký", "quầy tư vấn"],
        "doc": "Đã đến quầy chăm sóc khách hàng. Bạn sẽ được hướng dẫn và tư vấn dịch vụ tại đây.",
    },
    {
        "id": 6, "ma_bv": "C3.3", "buoi": "moi-luc",
        "ten": "Phòng chụp cộng hưởng từ",
        "phu": "MRI — toà nhà Cát Tường",
        "icon": "🧲", "diem": "phong-mri",
        "tu_khoa": ["cộng hưởng từ", "cong huong tu", "mri", "chụp mri", "chụp phim",
                    "chụp cộng hưởng"],
        "doc": "Đã đến Phòng Chụp cộng hưởng từ, hay còn gọi là em e rờ i. "
               "Bạn sẽ thực hiện chụp cộng hưởng từ tại đây.",
    },
    {
        "id": 7, "ma_bv": "C3.4", "buoi": "moi-luc",
        "ten": "Phòng 12 – Khu B",
        "phu": "Xét nghiệm — toà nhà Cát Tường",
        "icon": "🧪", "diem": "phong-12",
        "tu_khoa": ["xét nghiệm", "xet nghiem", "phòng 12", "phong 12", "lấy máu", "thử máu",
                    "công thức máu", "khu b"],
        "doc": "Đã đến Phòng mười hai, Khu B, toà nhà Cát Tường. "
               "Bạn sẽ được thực hiện đầy đủ các xét nghiệm cần thiết tại đây.",
    },
    {
        "id": 8, "ma_bv": "C3.5", "buoi": "moi-luc",
        "ten": "Phòng 8 – Khu B",
        "phu": "Siêu âm — toà nhà Cát Tường",
        "icon": "📡", "diem": "phong-8",
        "tu_khoa": ["siêu âm", "sieu am", "phòng 8", "phong 8", "khu b"],
        "doc": "Đã đến Phòng tám, Khu B, toà nhà Cát Tường. "
               "Bạn sẽ được thực hiện đầy đủ các siêu âm cần thiết tại đây.",
    },
    {
        "id": 9, "ma_bv": "C3.6", "buoi": "moi-luc",
        "ten": "Khoa điều trị trong ngày",
        "phu": "Theo dõi sau cận lâm sàng",
        "icon": "🛏️", "diem": "dieu-tri-ngay",
        "tu_khoa": ["điều trị trong ngày", "dieu tri trong ngay", "theo dõi", "nằm theo dõi",
                    "khoa điều trị"],
        "doc": "Đây là khoa điều trị trong ngày. Bạn sẽ được theo dõi trong vòng hai giờ "
               "sau khi đã thực hiện các chỉ định cận lâm sàng.",
    },
]

# ════════════════════════════════════════════════════════════════════
#  3. LỜI CHÀO THEO LOẠI KHÁCH  (PHẦN A tài liệu chào hỏi)
#     Đại biểu → luân phiên STT 1 và 2.  Khách VIP → STT 5.
# ════════════════════════════════════════════════════════════════════
CHAO = {
    "dai-bieu": {
        "ten": "Đại biểu",
        "icon": "👥",
        "mo_ta": "Khách mời dự lễ và hội thảo",
        # Hai câu luân phiên — app đổi qua lại để hai người đứng cạnh nhau không nghe y hệt
        "cau": [
            "Bệnh viện Hùng Vương xin kính chào Quý đại biểu! Chào mừng Quý vị đến dự Lễ đón nhận "
            "danh hiệu Anh hùng Lao động và Lễ khai trương Đơn vị điều trị HIFU. "
            "Kính chúc Quý vị một ngày thật nhiều niềm vui!",

            "Xin nồng nhiệt chào đón Quý đại biểu đến với Bệnh viện Hùng Vương! "
            "Hôm nay là ngày hội lớn của bệnh viện chúng tôi. Rất hân hạnh được phục vụ Quý vị!",
        ],
        # Buổi chiều là Hội thảo khoa học — bệnh viện soạn riêng hai câu này ở bản s2
        # (20/08/2026). App tự chọn theo giờ máy, xem buoiHienTai() trong khung-app.html.
        "cau_chieu": [
            "Bệnh viện Hùng Vương trân trọng kính chào Quý đại biểu! Chào mừng Quý vị đến tham dự "
            "Hội thảo khoa học Điều trị không xâm lấn bằng sóng siêu âm hội tụ. Kính chúc Quý đại "
            "biểu có một ngày thật nhiều niềm vui và có những trải nghiệm, kiến thức bổ ích tại "
            "Hội thảo!",

            "Xin nồng nhiệt chào đón Quý đại biểu đến với Bệnh viện Hùng Vương. "
            "Rất hân hạnh được phục vụ Quý vị!",
        ],
    },
    "khach-vip": {
        "ten": "Khách VIP",
        "icon": "⭐",
        "mo_ta": "Lãnh đạo, khách mời danh dự",
        "cau": [
            "Bệnh viện Hùng Vương trân trọng kính chào Quý lãnh đạo! Kính mời Quý vị di chuyển "
            "đến Phòng khánh tiết tại lầu mười để dùng trà và điểm tâm nhẹ trong thời gian chờ "
            "buổi lễ bắt đầu.",
        ],
    },
}

# Câu robot đọc ở các tình huống khác — PHẦN A, giữ nguyên văn bệnh viện
CAU_CO_DINH = {
    "tu_gioi_thieu":
        "Xin chào! Tôi là robot lễ tân của Bệnh viện Hùng Vương. Tôi có thể giới thiệu chương trình "
        "buổi lễ, hướng dẫn đường đi và cung cấp thông tin về dịch vụ HIFU. "
        "Quý vị cần tôi hỗ trợ điều gì ạ?",

    "huong_dan_check_in":
        "Kính mời Quý đại biểu ghi danh tại bàn tiếp đón, nhận hoa cài áo và quà tặng của bệnh viện. "
        "Sau đó, kính mời Quý vị chụp hình lưu niệm tại khu vực backdrop và di chuyển lên "
        "Hội trường lầu mười một bằng thang máy ưu tiên.",

    # Nút "Mời khách" — yêu cầu D1 của bệnh viện. Buổi sáng là buổi lễ (gần chín giờ).
    "moi_vao_hoi_truong":
        "Buổi lễ sắp bắt đầu. Kính mời Quý đại biểu di chuyển vào Hội trường lầu mười một và ổn định "
        "chỗ ngồi theo hướng dẫn của Ban tổ chức. Xin trân trọng cảm ơn!",

    # Buổi chiều là Hội thảo (gần mười ba giờ ba mươi) — nguyên văn bản s2 STT 5.
    # Cùng một nút "Mời khách", app tự đổi câu theo giờ máy.
    "moi_vao_hoi_thao":
        "Chương trình sắp bắt đầu. Kính mời Quý đại biểu vui lòng di chuyển vào Hội trường lầu "
        "mười một và ổn định chỗ ngồi. Xin trân trọng cảm ơn!",

    # Robot tự giới thiệu ở buổi chiều — bản s2 STT 3, nói "chương trình hội thảo khoa học"
    # thay vì "chương trình buổi lễ".
    "tu_gioi_thieu_chieu":
        "Xin chào! Tôi là robot lễ tân của Bệnh viện Hùng Vương. Tôi có thể giới thiệu chương trình "
        "hội thảo khoa học, hướng dẫn đường đi và cung cấp thông tin về hội thảo. "
        "Quý vị cần tôi hỗ trợ điều gì ạ?",

    "cam_on":
        "Bệnh viện Hùng Vương xin trân trọng cảm ơn Quý đại biểu đã dành thời gian quý báu đến "
        "chung vui cùng bệnh viện trong ngày trọng đại hôm nay!",

    "moi_tiec_trua":
        "Kính mời Quý đại biểu di chuyển đến Hội trường lầu sáu để dùng tiệc trưa thân mật cùng "
        "bệnh viện, từ mười một giờ ba mươi đến mười ba giờ. Xin trân trọng kính mời!",

    "tam_biet":
        "Xin kính chào tạm biệt Quý đại biểu! Kính chúc Quý vị nhiều sức khỏe, hạnh phúc và thành công. "
        "Hẹn gặp lại Quý vị tại Bệnh viện Hùng Vương!",

    "khong_nghe_ro":
        "Xin lỗi Quý vị, tôi chưa nghe rõ câu hỏi. Quý vị vui lòng hỏi lại giúp tôi, hoặc liên hệ "
        "đội lễ tân tại bàn tiếp đón để được hỗ trợ trực tiếp ạ.",

    "ngoai_pham_vi":
        "Câu hỏi này nằm ngoài thông tin tôi được cung cấp. Quý vị vui lòng liên hệ Ban tổ chức "
        "hoặc gặp đội lễ tân để được giải đáp ạ.",

    "chuc_mung_su_kien":
        "Hôm nay Bệnh viện Hùng Vương vinh dự đón nhận danh hiệu Anh hùng Lao động do Đảng và "
        "Nhà nước trao tặng. Xin cảm ơn Quý vị đã đến chung vui cùng tập thể bệnh viện!",

    "thuyet_minh_quy_trinh":
        "Kính thưa Quý đại biểu, hành trình điều trị HIFU tại Bệnh viện Hùng Vương được chuẩn hóa "
        "qua tám bước khép kín: từ đăng ký khám, xét nghiệm và chụp cộng hưởng từ lập kế hoạch, "
        "hội chẩn xác định chỉ định, chuẩn bị chu đáo, đến điều trị không xâm lấn dưới hướng dẫn "
        "siêu âm thời gian thực và tái khám định kỳ. Người bệnh hoàn toàn không có vết mổ, bảo tồn "
        "nguyên vẹn tử cung, thường xuất viện ngay ngày hôm sau và có thể mang thai sau điều trị "
        "ba tháng.",
}

# ════════════════════════════════════════════════════════════════════
#  4. LUỒNG "TƯ VẤN THỰC HIỆN HIFU"  (yêu cầu D2 của bệnh viện)
#     Hai nhánh, mỗi nhánh: đọc câu tư vấn → hỏi có muốn dẫn đường không → dẫn.
# ════════════════════════════════════════════════════════════════════
TU_VAN_HIFU = {
    "tieu_de": "Tư vấn thực hiện HIFU",
    "hoi": "Bạn đến đây thực hiện dịch vụ HIFU theo trường hợp nào ạ?",
    "nhanh": [
        {
            "ma": "lan-dau",
            "ten": "Tôi đến thực hiện dịch vụ HIFU lần đầu",
            "icon": "1️⃣",
            "doc": "Mời bạn đến quầy chăm sóc khách hàng để được tư vấn về dịch vụ. "
                   "Bạn có muốn tôi dẫn đường không ạ?",
            "dich_id": 5,        # Quầy chăm sóc khách hàng
        },
        {
            "ma": "duoc-chi-dinh",
            "ten": "Tôi được đơn vị hoặc phòng khám khác chỉ định đến",
            "icon": "2️⃣",
            "doc": "Mời bạn đến trực tiếp Đơn vị điều trị không xâm lấn bằng sóng siêu âm hội tụ "
                   "để nhân viên tư vấn. Bạn có muốn tôi dẫn đường không ạ?",
            "dich_id": 4,        # Đơn vị HIFU
        },
    ],
}

# ════════════════════════════════════════════════════════════════════
#  5. KHO HỎI ĐÁP — nguồn duy nhất cho cả màn hình lẫn mô hình AI
#
#  Mỗi mục:  hoi   = câu hỏi chính (hiện trên màn hình dạng thẻ bấm)
#            cach  = các cách hỏi khác, để bộ tìm kiếm bắt được giọng nói
#            dap   = câu robot ĐỌC NGUYÊN VĂN. Số đã chuyển sang chữ.
#            nhom  = để gom thẻ trên màn hình
#
#  ⚠ Câu `dap` KHÔNG bao giờ đi qua mô hình AI. Mô hình chỉ được chọn id và soạn câu dẫn.
# ════════════════════════════════════════════════════════════════════
NHOM = [
    {"ma": "su-kien",  "ten": "Sự kiện hôm nay",    "icon": "🎉"},
    {"ma": "hoi-thao", "ten": "Hội thảo khoa học",   "icon": "🎤"},
    {"ma": "benh-vien", "ten": "Bệnh viện Hùng Vương", "icon": "🏥"},
    {"ma": "hifu",     "ten": "Kỹ thuật HIFU",      "icon": "🔬"},
    {"ma": "quy-trinh", "ten": "Quy trình điều trị", "icon": "📋"},
]

HOI_DAP = [
    # ─────────── Sự kiện hôm nay ───────────
    dict(id=1, nhom="su-kien", hoi="Hôm nay bệnh viện có sự kiện gì?",
         cach=["hôm nay có gì", "đang diễn ra sự kiện gì", "bệnh viện đang tổ chức gì",
               "sự kiện hôm nay", "hôm nay có chương trình gì"],
         dap="Hôm nay, thứ Bảy ngày hai mươi hai tháng tám năm hai nghìn không trăm hai mươi sáu, "
             "Bệnh viện Hùng Vương có hai sự kiện. Buổi sáng, bệnh viện long trọng tổ chức Lễ đón "
             "nhận danh hiệu Anh hùng Lao động do Đảng và Nhà nước trao tặng, kết hợp Lễ khai "
             "trương Đơn vị điều trị không xâm lấn bằng sóng siêu âm hội tụ HIFU. Buổi chiều, "
             "bệnh viện tổ chức Hội thảo khoa học Điều trị không xâm lấn bằng sóng siêu âm hội tụ."),

    dict(id=2, nhom="su-kien", hoi="Buổi lễ diễn ra ở đâu, lúc mấy giờ?",
         cach=["buổi lễ ở đâu", "mấy giờ bắt đầu", "khai mạc lúc nào", "địa điểm tổ chức",
               "hội trường ở đâu", "lễ bắt đầu khi nào"],
         dap="Buổi lễ bắt đầu lúc chín giờ sáng tại Hội trường lầu mười một, Toà nhà Bách Hợp, "
             "Bệnh viện Hùng Vương, số chín Lý Thường Kiệt, Phường Chợ Lớn, Thành phố Hồ Chí Minh. "
             "Bệnh viện hân hạnh đón tiếp Quý đại biểu từ tám giờ ba mươi."),

    dict(id=3, nhom="su-kien", hoi="Chương trình buổi lễ gồm những gì?",
         cach=["chương trình gồm gì", "lịch trình thế nào", "nội dung chương trình",
               "chương trình buổi lễ", "có những phần nào"],
         dap="Chương trình mở đầu bằng văn nghệ chào mừng lúc chín giờ, nghi thức chào cờ và giới "
             "thiệu đại biểu, phát biểu của lãnh đạo bệnh viện và trình chiếu phim phóng sự. "
             "Nghi thức đón nhận danh hiệu Anh hùng Lao động từ mười giờ. Nghi thức khai trương "
             "Đơn vị HIFU lúc mười một giờ mười lăm. Bế mạc lúc mười một giờ ba mươi và tiệc trưa "
             "thân mật tại lầu sáu. Quý vị có thể xem chương trình chi tiết trên màn hình của tôi."),

    dict(id=4, nhom="su-kien", hoi="Mấy giờ trao danh hiệu Anh hùng Lao động?",
         cach=["khi nào trao danh hiệu", "lúc nào nhận danh hiệu", "trao thưởng lúc mấy giờ",
               "nghi thức đón nhận lúc nào"],
         dap="Nghi thức đón nhận danh hiệu Anh hùng Lao động và các danh hiệu cao quý khác của "
             "Nhà nước diễn ra từ mười giờ đến mười giờ năm mươi tại Hội trường lầu mười một."),

    dict(id=5, nhom="su-kien", hoi="Mấy giờ khai trương Đơn vị HIFU?",
         cach=["khi nào khai trương", "lễ khai trương lúc mấy giờ", "cắt băng lúc nào",
               "khai trương đơn vị lúc nào"],
         dap="Nghi thức khai trương Đơn vị điều trị không xâm lấn bằng sóng siêu âm hội tụ HIFU "
             "diễn ra từ mười một giờ mười lăm đến mười một giờ hai mươi lăm, ngay trong chương "
             "trình buổi lễ."),

    dict(id=6, nhom="su-kien", hoi="Vì sao bệnh viện được phong tặng danh hiệu Anh hùng Lao động?",
         cach=["vì sao được anh hùng lao động", "lý do được phong tặng", "được thưởng vì cái gì",
               "thành tích gì mà được"],
         dap="Danh hiệu Anh hùng Lao động được Chủ tịch nước phong tặng theo Quyết định số tám "
             "trăm ba mươi ngày ba tháng sáu năm hai nghìn không trăm hai mươi sáu, ghi nhận những "
             "thành tích đặc biệt xuất sắc của tập thể Bệnh viện Hùng Vương qua nhiều thế hệ trong "
             "công tác khám chữa bệnh, đào tạo nguồn nhân lực, nghiên cứu khoa học, hợp tác quốc tế "
             "và chăm sóc sức khỏe bà mẹ, trẻ em."),

    dict(id=7, nhom="su-kien", hoi="Giám đốc bệnh viện là ai?",
         cach=["ai là giám đốc", "giám đốc tên gì", "lãnh đạo bệnh viện là ai"],
         dap="Giám đốc Bệnh viện Hùng Vương là Phó Giáo sư, Tiến sĩ, Bác sĩ Hoàng Thị Diễm Tuyết."),

    # ─────────── Bệnh viện ───────────
    dict(id=8, nhom="benh-vien", hoi="Giới thiệu về Bệnh viện Hùng Vương?",
         cach=["bệnh viện hùng vương là gì", "kể về bệnh viện", "bệnh viện thế nào",
               "giới thiệu bệnh viện"],
         dap="Bệnh viện Hùng Vương là bệnh viện chuyên khoa hạng một về sản phụ khoa, tuyến cuối "
             "của khu vực phía Nam, trực thuộc Sở Y tế Thành phố Hồ Chí Minh, với bề dày truyền "
             "thống trong khám chữa bệnh, đào tạo, nghiên cứu khoa học và hợp tác quốc tế, luôn "
             "tiên phong trong chăm sóc và bảo vệ sức khỏe bà mẹ và trẻ em."),

    dict(id=9, nhom="benh-vien", hoi="Đơn vị HIFU có ý nghĩa gì với bệnh viện?",
         cach=["ý nghĩa của đơn vị hifu", "vì sao lập đơn vị hifu", "đơn vị này quan trọng thế nào"],
         dap="Đơn vị HIFU ra đời là một bước ngoặt của bệnh viện trong điều trị khối u tử cung mà "
             "không phải can thiệp phẫu thuật, hoàn thiện phổ điều trị cá thể hóa gồm nội khoa, "
             "can thiệp không xâm lấn và phẫu thuật. Đây là kỹ thuật hiện đại phù hợp với xu hướng "
             "thế giới về can thiệp tối thiểu, góp phần nâng cao chất lượng khám chữa bệnh và đáp "
             "ứng nhu cầu chăm sóc sức khỏe ngày càng cao của người dân."),

    # ─────────── Kỹ thuật HIFU ───────────
    dict(id=10, nhom="hifu", hoi="HIFU là gì?",
         cach=["hifu là gì", "kỹ thuật này là gì", "sóng siêu âm hội tụ là gì",
               "điều trị không xâm lấn là gì", "giải thích hifu"],
         dap="HIFU là viết tắt của sóng siêu âm hội tụ cường độ cao. Chùm sóng siêu âm từ bên ngoài "
             "cơ thể được hội tụ chính xác vào khối u, tương tự thấu kính hội tụ ánh sáng. Tại tiêu "
             "điểm, mô u đạt sáu mươi đến một trăm độ C chỉ trong vài giây và bị hoại tử, trong khi "
             "da và mô lành trên đường truyền sóng hầu như không bị tổn thương. Kỹ thuật điều trị "
             "u xơ tử cung bằng sóng siêu âm hội tụ đã được cơ quan quản lý thực phẩm và dược phẩm "
             "Hoa Kỳ chấp thuận từ năm hai nghìn không trăm lẻ tư và được ứng dụng rộng rãi trên "
             "thế giới."),

    dict(id=11, nhom="hifu", hoi="Đơn vị HIFU điều trị những bệnh gì?",
         cach=["điều trị bệnh gì", "chữa được bệnh nào", "áp dụng cho bệnh nào",
               "hifu chữa gì", "làm được những gì"],
         dap="Theo Quy trình kỹ thuật đã được bệnh viện ban hành, Đơn vị điều trị các bệnh lý lành "
             "tính vùng chậu và tuyến vú, gồm năm nhóm: u xơ tử cung; lạc tuyến trong cơ tử cung; "
             "lạc nội mạc tử cung ở thành bụng; hỗ trợ tiền xử lý thai bám vết mổ cũ trước khi hút "
             "thai; và u xơ tuyến vú lành tính. Kỹ thuật chỉ áp dụng cho tổn thương lành tính đã "
             "được xác định, không dùng để điều trị ung thư."),

    dict(id=12, nhom="hifu", hoi="Ưu điểm của điều trị HIFU?",
         cach=["ưu điểm là gì", "lợi ích của hifu", "hay ở chỗ nào", "tốt hơn mổ chỗ nào"],
         dap="HIFU hoàn toàn không rạch da, không chảy máu, không để lại sẹo; bảo tồn nguyên vẹn "
             "tử cung, khả năng sinh sản và hình dạng tuyến vú của người phụ nữ. Người bệnh chỉ cần "
             "an thần nhẹ, hồi phục nhanh, thường xuất viện ngay ngày hôm sau và sớm trở lại sinh "
             "hoạt, lao động."),

    dict(id=13, nhom="hifu", hoi="Điều trị HIFU có đau không, có phải gây mê không?",
         cach=["có đau không", "có gây mê không", "đau lắm không", "có phải mê không",
               "làm có đau"],
         dap="Người bệnh không cần gây mê. Ê-kíp gây mê hồi sức sử dụng thuốc an thần và giảm đau "
             "đường tĩnh mạch; người bệnh vẫn tỉnh táo, giao tiếp được với bác sĩ trong suốt quá "
             "trình điều trị và được theo dõi sinh hiệu liên tục trên monitor. Đa số chỉ cảm thấy "
             "nóng ấm hoặc tức nhẹ vùng bụng dưới."),

    dict(id=14, nhom="hifu", hoi="Một ca điều trị mất bao lâu, nằm viện bao lâu?",
         cach=["mất bao lâu", "làm trong bao lâu", "nằm viện mấy ngày", "bao lâu thì xong",
               "thời gian điều trị"],
         dap="Thời gian điều trị khoảng một đến ba giờ đối với u tử cung và ba mươi đến sáu mươi "
             "phút đối với u vú. Người bệnh nhập viện trước một ngày để chuẩn bị và thường xuất "
             "viện ngay ngày hôm sau điều trị."),

    dict(id=15, nhom="hifu", hoi="Ai phù hợp để điều trị HIFU?",
         cach=["ai làm được", "trường hợp nào làm được", "phù hợp với ai", "đối tượng nào"],
         dap="Người bệnh có u xơ tử cung hoặc lạc tuyến trong cơ tử cung gây triệu chứng hoặc gây "
             "vô sinh, mong muốn bảo tồn tử cung hoặc không muốn phẫu thuật; người có khối lạc nội "
             "mạc tử cung ở thành bụng; hoặc u xơ tuyến vú lành tính có triệu chứng. Bác sĩ sẽ thăm "
             "khám, xét nghiệm, chụp cộng hưởng từ và thực hiện nghiệm pháp đánh giá trước khi "
             "quyết định chỉ định cho từng trường hợp cụ thể."),

    dict(id=16, nhom="hifu", hoi="Trường hợp nào không thực hiện được HIFU?",
         cach=["ai không làm được", "chống chỉ định", "trường hợp nào không được",
               "không nên làm khi nào"],
         dap="Một số trường hợp không thực hiện được, ví dụ: phụ nữ đang mang thai; có bệnh lý ác "
             "tính của cơ quan sinh dục hoặc hình ảnh nghi ngờ ác tính; đang đặt dụng cụ tử cung "
             "thì cần lấy ra trước; tiền sử xạ trị vùng chậu; không thể nằm sấp trong một đến ba "
             "giờ; hoặc một số bệnh lý nội khoa nặng. Bác sĩ sẽ sàng lọc kỹ lưỡng theo quy trình "
             "trước khi điều trị."),

    dict(id=17, nhom="hifu", hoi="Điều trị HIFU có an toàn không?",
         cach=["có an toàn không", "có rủi ro gì không", "biến chứng thế nào",
               "có nguy hiểm không"],
         dap="Đây là kỹ thuật có độ an toàn cao. Theo tổng kết y văn trên gần mười nghìn trường hợp, "
             "đa số chỉ gặp phản ứng nhẹ tự khỏi như đau bụng dưới hoặc sốt nhẹ, khoảng mười ba "
             "phẩy năm phần trăm; biến chứng nặng rất hiếm, chỉ khoảng không phẩy không năm phần "
             "trăm. Tại Bệnh viện Hùng Vương, quy trình được chuẩn hóa với bảng kiểm ba giai đoạn "
             "trước, trong và sau điều trị, và ê-kíp gây mê hồi sức theo dõi người bệnh liên tục "
             "trong suốt quá trình."),

    dict(id=18, nhom="hifu", hoi="Hiệu quả điều trị như thế nào?",
         cach=["hiệu quả ra sao", "kết quả thế nào", "u có nhỏ lại không", "khỏi được không"],
         dap="Mục tiêu là phá hủy ít nhất bảy mươi phần trăm thể tích khối u ngay trong lần điều "
             "trị, được kiểm chứng bằng chụp cộng hưởng từ. Theo y văn, thể tích u xơ tử cung giảm "
             "trung bình năm mươi đến tám mươi phần trăm sau mười hai tháng kèm cải thiện rõ triệu "
             "chứng và chất lượng sống. U xơ tuyến vú giảm khoảng bảy mươi phần trăm thể tích sau "
             "một năm và hiệu quả duy trì ổn định đến năm năm sau một lần điều trị."),

    dict(id=19, nhom="hifu", hoi="Sau điều trị HIFU có thể mang thai không?",
         cach=["có con được không", "mang thai được không", "còn sinh con được không",
               "ảnh hưởng sinh sản không", "bao lâu thì có thai được"],
         dap="Có. HIFU bảo tồn nguyên vẹn tử cung, và u xơ tử cung gây vô sinh cũng là một chỉ định "
             "điều trị. Theo quy trình của bệnh viện, người bệnh có thể mang thai sau điều trị ba "
             "tháng và sẽ được bác sĩ tư vấn kế hoạch sinh sản cụ thể khi tái khám."),

    dict(id=20, nhom="hifu", hoi="Người bệnh cần chuẩn bị gì trước điều trị?",
         cach=["cần chuẩn bị gì", "trước khi làm phải làm gì", "chuẩn bị thế nào",
               "có phải nhịn ăn không"],
         dap="Người bệnh được hướng dẫn chuẩn bị chu đáo trong ba ngày trước điều trị: tập làm quen "
             "với cảm giác căng bàng quang, ăn thức ăn nhẹ ít chất bã, sau đó nhập viện trước một "
             "ngày để làm sạch ruột và nhịn ăn uống trong ngày điều trị. Sự chuẩn bị này giúp tạo "
             "cửa sổ siêu âm tốt nhất để việc điều trị chính xác và an toàn."),

    dict(id=21, nhom="hifu", hoi="Ê-kíp thực hiện gồm những ai?",
         cach=["ai thực hiện", "bao nhiêu người làm", "ê kíp gồm ai", "đội ngũ thế nào"],
         dap="Mỗi ca điều trị do ê-kíp năm người thực hiện: bác sĩ sản phụ khoa, bác sĩ chẩn đoán "
             "hình ảnh, bác sĩ gây mê hồi sức, kỹ thuật viên gây mê và điều dưỡng hộ sinh; tất cả "
             "đều được đào tạo về kỹ thuật HIFU. Đơn vị có tổng cộng mười một nhân sự chuyên trách "
             "cùng phòng điều trị HIFU chuyên biệt."),

    dict(id=22, nhom="hifu", hoi="Khi nào Đơn vị bắt đầu tiếp nhận điều trị?",
         cach=["khi nào nhận bệnh", "bao giờ hoạt động", "bắt đầu điều trị từ khi nào",
               "khi nào làm được"],
         dap="Sau lễ khai trương hôm nay, Đơn vị HIFU sẽ tiếp nhận điều trị những trường hợp đầu "
             "tiên từ tháng chín năm hai nghìn không trăm hai mươi sáu, với sự đồng hành và giám "
             "sát của các chuyên gia giàu kinh nghiệm. Quý vị có thể đăng ký khám và tư vấn ngay "
             "từ bây giờ qua Bộ phận Chăm sóc khách hàng số không chín sáu một, hai năm một, "
             "bốn ba một, hoặc qua Zalo."),

    dict(id=23, nhom="hifu", hoi="Muốn khám và tư vấn HIFU thì đăng ký ở đâu?",
         cach=["đăng ký ở đâu", "khám ở đâu", "muốn tư vấn thì đi đâu", "liên hệ ở đâu",
               "đặt lịch ở đâu"],
         dap="Quý vị có thể đăng ký khám tại quầy tiếp đón ở toà nhà Cát Tường, khoa Phụ nội "
             "Nội tiết ở toà nhà Bách Hợp, hoặc liên hệ Bộ phận Chăm sóc khách hàng số không chín "
             "sáu một, hai năm một, bốn ba một, hoặc qua Zalo để đặt lịch hẹn tư vấn với bác sĩ "
             "chuyên khoa."),

    dict(id=24, nhom="hifu", hoi="Đơn vị HIFU nằm ở đâu trong bệnh viện?",
         cach=["đơn vị hifu ở đâu", "chỗ nào làm hifu", "đi đến hifu thế nào", "hifu ở tầng mấy"],
         dap="Đơn vị Điều trị không xâm lấn bằng sóng siêu âm hội tụ, hay còn gọi là đơn vị HIFU, "
             "trực thuộc khoa Phụ nội Nội tiết, được đặt tại tầng trệt toà nhà Cát Tường. "
             "Từ cổng số năm, địa chỉ số chín Lý Thường Kiệt nhìn vào, Quý vị sẽ thấy ngay đơn vị "
             "HIFU."),

    dict(id=25, nhom="hifu", hoi="Máy HIFU của bệnh viện là hệ thống nào?",
         cach=["máy gì", "thiết bị nào", "hệ thống máy ra sao", "máy móc thế nào"],
         dap="Bệnh viện trang bị hệ thống điều trị siêu âm hội tụ đồng bộ, gồm bàn điều trị tích "
             "hợp đầu phát sóng hội tụ, bể nước lạnh khử khí, hệ thống siêu âm định vị dẫn đường "
             "thời gian thực và máy trạm lập kế hoạch điều trị."),

    # ─────────── Hội thảo khoa học buổi chiều ───────────
    # Nguồn: "Noi dung cai dat Robot - HTKH HIFU_s2.docx" bệnh viện gửi 20/08/2026,
    # PHẦN B1 "Về chương trình Hội thảo". Đây là SỰ KIỆN THỨ HAI trong ngày 22/08 —
    # bản tài liệu 21/08 chỉ nói buổi lễ sáng nên trước đây robot không biết gì về
    # hội thảo chiều. Giữ nguyên văn bệnh viện, chỉ chuyển số sang chữ.
    dict(id=26, nhom="hoi-thao", hoi="Hội thảo diễn ra ở đâu, lúc mấy giờ?",
         cach=["hội thảo mấy giờ", "hội thảo ở đâu", "hội thảo khoa học lúc nào",
               "chiều nay mấy giờ", "hội thảo bắt đầu khi nào", "buổi chiều mấy giờ",
               "hội thảo khoa học ở đâu"],
         dap="Hội thảo bắt đầu lúc mười bốn giờ chiều tại Hội trường lầu mười một, Toà nhà Bách "
             "Hợp, Bệnh viện Hùng Vương, số chín đường Lý Thường Kiệt, Phường Chợ Lớn, Thành phố "
             "Hồ Chí Minh. Bệnh viện hân hạnh đón tiếp Quý đại biểu từ mười ba giờ ba mươi."),

    dict(id=27, nhom="hoi-thao", hoi="Chương trình Hội thảo gồm những gì?",
         cach=["chương trình hội thảo", "nội dung hội thảo", "lịch trình hội thảo",
               "hội thảo có những bài gì", "các bài báo cáo", "chương trình chiều nay"],
         dap="Chương trình gồm: mười bốn giờ năm phút, Giám đốc Bệnh viện Hùng Vương phát biểu "
             "khai mạc. Mười bốn giờ mười, Giáo sư He Min trình bày bài Tổng quan về ứng dụng lâm "
             "sàng của siêu âm hội tụ cường độ cao, thực trạng và định hướng phát triển trong "
             "tương lai. Mười bốn giờ ba mươi, Giáo sư Nguyễn Viết Tiến trình bày bài Kinh nghiệm "
             "điều trị u xơ tử cung và lạc tuyến trong cơ tử cung bằng điều trị không xâm lấn bằng "
             "sóng siêu âm hội tụ. Mười bốn giờ năm mươi, Quý đại biểu nghỉ giải lao. Mười lăm giờ "
             "mười, Phó Giáo sư, Tiến sĩ, Bác sĩ Hoàng Thị Diễm Tuyết trình bày bài Không phải mọi "
             "khối u tử cung đều cần phẫu thuật, kỷ nguyên điều trị bảo tồn trong phụ khoa. Mười "
             "lăm giờ ba mươi, Cử nhân hộ sinh Nguyễn Thị Hà Chi, Phòng Điều dưỡng Bệnh viện Hùng "
             "Vương, trình bày về Vai trò điều dưỡng chăm sóc người bệnh điều trị không xâm lấn "
             "bằng sóng siêu âm hội tụ. Từ mười lăm giờ năm mươi đến mười sáu giờ ba mươi, các đại "
             "biểu cùng thảo luận và đặt câu hỏi, sau đó tổng kết bế mạc Hội thảo. Quý vị có thể "
             "xem chương trình chi tiết trên màn hình của tôi."),

    dict(id=28, nhom="hoi-thao", hoi="Ai tham gia báo cáo trong Hội thảo hôm nay?",
         cach=["ai báo cáo", "diễn giả là ai", "báo cáo viên", "chuyên gia nào trình bày",
               "ai trình bày", "giáo sư nào"],
         dap="Giáo sư He Min, Tiến sĩ Y khoa, Bác sĩ điều trị không xâm lấn bằng sóng siêu âm hội "
             "tụ cao cấp, Trợ lý Giám đốc Bệnh viện Haifu Trùng Khánh, Giám đốc Trung tâm Đào tạo "
             "Lâm sàng. Giáo sư Nguyễn Viết Tiến, nguyên Thứ trưởng Bộ Y tế, Chủ tịch Hội Sản phụ "
             "khoa Việt Nam. Phó Giáo sư, Tiến sĩ, Bác sĩ Hoàng Thị Diễm Tuyết, Giám đốc Bệnh viện "
             "Hùng Vương. Và Cử nhân hộ sinh Nguyễn Thị Hà Chi, Phòng Điều dưỡng Bệnh viện Hùng Vương."),

    dict(id=29, nhom="hoi-thao", hoi="Vì sao bệnh viện tổ chức Hội thảo này?",
         cach=["lý do tổ chức hội thảo", "tại sao có hội thảo", "vì sao tổ chức",
               "mục tiêu tổ chức hội thảo"],
         dap="Hội thảo nằm trong khuôn khổ Tuần lễ cập nhật kiến thức y khoa liên tục năm hai "
             "nghìn không trăm hai mươi sáu, nhằm cập nhật những tiến bộ mới trong điều trị không "
             "xâm lấn bằng sóng siêu âm hội tụ, đồng thời tạo cơ hội để các chuyên gia cùng trao "
             "đổi, chia sẻ kinh nghiệm về một phương pháp điều trị hiện đại, hướng đến giảm can "
             "thiệp, nâng cao chất lượng điều trị và đặc biệt mở thêm lựa chọn cho phụ nữ có nhu "
             "cầu bảo tồn tử cung."),

    dict(id=30, nhom="hoi-thao", hoi="Mục đích của Hội thảo là gì?",
         cach=["mục đích hội thảo", "hội thảo để làm gì", "ý nghĩa của hội thảo",
               "hội thảo nhằm mục đích gì"],
         dap="Hội thảo khoa học là cơ hội để các nhân viên y tế trao đổi, cập nhật kiến thức mới "
             "cũng như chia sẻ kinh nghiệm trong việc chẩn đoán và kỹ thuật điều trị bệnh lý phụ "
             "khoa, nhũ hoa bằng công nghệ sóng siêu âm hội tụ cao tần."),

    dict(id=31, nhom="hoi-thao", hoi="Phí tham dự Hội thảo?",
         cach=["hội thảo có mất phí không", "tham dự tốn bao nhiêu", "có thu tiền không",
               "phí tham dự", "vào cửa có mất tiền không", "miễn phí không"],
         dap="Chương trình Hội thảo tổ chức không thu phí."),

    dict(id=32, nhom="hoi-thao", hoi="Phí cấp chứng chỉ CME là bao nhiêu?",
         cach=["cme bao nhiêu tiền", "phí cme", "chứng chỉ cme", "tín chỉ cme",
               "cấp cme", "muốn lấy chứng chỉ", "phí tham dự và cấp cme"],
         dap="Phí tham dự và cấp chứng chỉ CME là ba trăm nghìn đồng một CME, cấp một phẩy năm "
             "giờ tín chỉ."),

    dict(id=33, nhom="hoi-thao", hoi="Hội thảo tập trung vào những nội dung nổi bật nào?",
         cach=["nội dung nổi bật", "hội thảo nói về gì", "chủ đề hội thảo",
               "điểm nhấn hội thảo"],
         dap="Hội thảo tập trung vào thực trạng và định hướng phát triển trong tương lai của điều "
             "trị không xâm lấn bằng sóng siêu âm hội tụ, cùng kỷ nguyên mới trong điều trị bảo "
             "tồn trong phụ khoa."),

    dict(id=34, nhom="hoi-thao", hoi="Đại biểu nhận được gì khi tham dự Hội thảo?",
         cach=["tham dự được gì", "lợi ích khi tham dự", "đại biểu được gì",
               "dự hội thảo có lợi gì"],
         dap="Đại biểu có cơ hội cập nhật kiến thức mới, lắng nghe các chuyên gia chia sẻ kinh "
             "nghiệm thực tiễn và trao đổi về ứng dụng điều trị không xâm lấn bằng sóng siêu âm "
             "hội tụ trong điều trị bệnh lý phụ khoa."),

    dict(id=35, nhom="hoi-thao", hoi="Hội thảo có ý nghĩa gì đối với người bệnh?",
         cach=["ý nghĩa với người bệnh", "người bệnh được lợi gì", "bệnh nhân hưởng lợi gì",
               "hội thảo giúp gì cho bệnh nhân"],
         dap="Thông qua việc cập nhật và trao đổi chuyên môn, Hội thảo góp phần thúc đẩy những "
             "phương pháp điều trị hiện đại, an toàn, không xâm lấn và phù hợp hơn với nhu cầu "
             "chăm sóc sức khoẻ phụ nữ."),

    dict(id=36, nhom="hoi-thao", hoi="Hội thảo dành cho ai?",
         cach=["ai được tham dự", "đối tượng tham dự", "dành cho những ai",
               "ai được vào hội thảo", "thành phần tham dự"],
         dap="Hội thảo hướng đến các chuyên gia, bác sĩ, hộ sinh, điều dưỡng và nhân viên y tế "
             "hoạt động trong lĩnh vực sản phụ khoa."),

    dict(id=37, nhom="hoi-thao",
         hoi="Điều gì khiến điều trị bằng sóng siêu âm hội tụ đáng quan tâm hiện nay?",
         cach=["vì sao hifu được quan tâm", "tại sao hifu là xu hướng",
               "hifu có gì đáng chú ý", "xu hướng điều trị hiện nay"],
         dap="Trong xu hướng y học hiện đại, người bệnh ngày càng mong muốn những phương pháp ít "
             "xâm lấn, giảm đau, hồi phục nhanh và thân thiện hơn. Điều trị không xâm lấn bằng "
             "sóng siêu âm hội tụ là một trong những công nghệ đang được quan tâm trong xu hướng này."),

    # ─────────── Hai câu bệnh viện gửi thêm ở PHẦN B2 bản s2 ───────────
    dict(id=38, nhom="benh-vien",
         hoi="Bệnh viện Hùng Vương tiên phong triển khai HIFU như thế nào?",
         cach=["bệnh viện đầu tiên làm hifu", "tiên phong hifu", "đầu tiên tại thành phố",
               "thứ mấy cả nước", "bệnh viện nào làm trước"],
         dap="Bệnh viện Hùng Vương tiên phong triển khai công nghệ điều trị không xâm lấn bằng "
             "sóng siêu âm hội tụ, lần đầu tiên tại Thành phố Hồ Chí Minh và là nơi thứ hai trên "
             "cả nước."),

    dict(id=39, nhom="benh-vien",
         hoi="Bệnh viện đầu tư cho Đơn vị HIFU như thế nào?",
         cach=["đầu tư ra sao", "đào tạo ở đâu", "bác sĩ được đào tạo thế nào",
               "máy móc đầu tư", "chuẩn bị nhân sự thế nào"],
         dap="Đội ngũ bác sĩ và nữ hộ sinh được đào tạo chuyên sâu tại Trùng Khánh, Trung Quốc, "
             "nơi đã thực hiện rất nhiều ca điều trị bằng sóng siêu âm hội tụ. Bệnh viện trang bị "
             "máy điều trị thế hệ mới nhất, đồng thời hội chẩn và đào tạo định kỳ cùng các chuyên "
             "gia quốc tế."),
]

# ════════════════════════════════════════════════════════════════════
#  6. QUY TRÌNH 8 BƯỚC  (PHẦN C tài liệu — robot thuyết minh khi giới thiệu đơn vị)
#     `dich_id` nối bước với điểm dẫn đường, để bấm vào bước là dẫn được tới nơi.
# ════════════════════════════════════════════════════════════════════
QUY_TRINH = [
    dict(buoc=1, ten="Tiếp nhận – đăng ký khám", dich_id=5,
         doc="Bước một, tiếp nhận và đăng ký khám. Người bệnh đăng ký khám trực tiếp tại đơn vị "
             "HIFU nếu đến thông qua giấy giới thiệu từ bệnh viện hoặc từ phòng khám phụ khoa, "
             "hoặc đặt hẹn qua Bộ phận Chăm sóc khách hàng số không chín sáu một, hai năm một, "
             "bốn ba một, hoặc qua Zalo. Bác sĩ sản phụ khoa sẽ thăm khám và đánh giá nhu cầu "
             "sinh sản trong tương lai."),

    dict(buoc=2, ten="Xét nghiệm tiền phẫu", dich_id=7,
         doc="Bước hai, xét nghiệm tiền phẫu. Thực hiện đầy đủ các xét nghiệm: công thức máu, "
             "nhóm máu, chức năng đông máu, chức năng gan thận, bê ta hát xê gê, xê a một trăm hai "
             "mươi lăm, tế bào học cổ tử cung, điện tim và siêu âm tim. Tại phòng mười hai, Khu B, "
             "toà nhà Cát Tường."),

    dict(buoc=3, ten="Chẩn đoán hình ảnh chuyên sâu", dich_id=6,
         doc="Bước ba, chẩn đoán hình ảnh chuyên sâu. Chụp cộng hưởng từ vùng chậu có tiêm thuốc "
             "tương phản để lập kế hoạch điều trị; thực hiện nghiệm pháp oxytocin kết hợp siêu âm "
             "Doppler nhằm dự đoán mức độ đáp ứng với HIFU. Tại phòng chụp cộng hưởng từ, "
             "toà nhà Cát Tường."),

    dict(buoc=4, ten="Hội chẩn và tư vấn", dich_id=4,
         doc="Bước bốn, hội chẩn và tư vấn. Bác sĩ điều trị HIFU cùng bác sĩ gây mê hồi sức phối "
             "hợp đánh giá chỉ định và chống chỉ định; người bệnh được tư vấn đầy đủ về lợi ích, "
             "nguy cơ và ký đồng thuận trước điều trị. Tại đơn vị HIFU, toà nhà Cát Tường."),

    dict(buoc=5, ten="Chuẩn bị trước điều trị", dich_id=None,
         doc="Bước năm, chuẩn bị trước điều trị. Trong ba ngày trước điều trị: tập bàng quang và "
             "ăn chế độ ít chất bã theo hướng dẫn; nhập viện trước một ngày để làm sạch ruột; nhịn "
             "ăn uống hoàn toàn trong ngày điều trị. Tại khoa Phụ nội Nội tiết, toà nhà Bách Hợp."),

    dict(buoc=6, ten="Thực hiện điều trị HIFU", dich_id=4,
         doc="Bước sáu, thực hiện điều trị. Tại phòng điều trị HIFU chuyên biệt, người bệnh nằm sấp "
             "trên bàn điều trị có bể nước khử khí, được an thần và giảm đau nhưng vẫn tỉnh táo. "
             "Bác sĩ định vị khối u và phát sóng hội tụ tiêu hủy mô u dưới hướng dẫn siêu âm thời "
             "gian thực, với ê-kíp năm người theo dõi liên tục. Thời gian khoảng một đến ba giờ với "
             "u tử cung, ba mươi đến sáu mươi phút với u vú."),

    dict(buoc=7, ten="Theo dõi sau điều trị", dich_id=9,
         doc="Bước bảy, theo dõi sau điều trị. Người bệnh được làm mát bàng quang, theo dõi tại "
             "khoa nội trú và chụp cộng hưởng từ đánh giá hiệu quả với mục tiêu phá hủy ít nhất "
             "bảy mươi phần trăm thể tích khối u; thường xuất viện ngay ngày hôm sau."),

    dict(buoc=8, ten="Tái khám định kỳ", dich_id=None,
         doc="Bước tám, tái khám định kỳ. Tái khám tại phòng khám HIFU sau hai tuần, sau đó định kỳ "
             "ba, sáu và mười hai tháng với chụp cộng hưởng từ đánh giá mức giảm kích thước khối u. "
             "Người bệnh mong con được tư vấn có thai sau điều trị ba tháng."),
]

# ════════════════════════════════════════════════════════════════════
#  7. NHỮNG THỨ BỆNH VIỆN CHƯA CUNG CẤP
#     App KHÔNG đoán. Hỏi tới là trả lời "chưa có thông tin" + chỉ sang lễ tân.
#     Điền được cái nào thì bỏ khỏi danh sách này và thêm vào HOI_DAP.
# ════════════════════════════════════════════════════════════════════
CHUA_CO = [
    "số điện thoại Ban tổ chức sự kiện",
    "tên mạng wifi và mật khẩu",
    "vị trí nhà vệ sinh",
    "vị trí bãi giữ xe",
    "vị trí căn tin",
    "giá dịch vụ HIFU",
]


# ════════════════════════════════════════════════════════════════════
#  9. ĐI VÒNG QUANH SỰ KIỆN  (anh Trường chốt 21/08/2026)
#
#     Robot đi liên tục qua năm điểm, KHÔNG dừng lại ở điểm nào, vừa đi vừa chào khách.
#     Khách chạm màn hình → robot dừng, vào giao diện phục vụ.
#     Ba mươi giây không ai thao tác → robot đi tiếp.
#
#     ⚠ TÊN ĐIỂM phải trùng TỪNG KÝ TỰ với tên kỹ thuật đặt lúc quét bản đồ:
#       không dấu tiếng Việt, chữ D viết hoa, một dấu cách trước số.
#       Sai một ký tự là robot bỏ qua điểm đó mà không báo gì.
#
#     ⚠ NĂM CÂU CHÀO là GHÉP LẠI từ chính lời bệnh viện soạn ở PHẦN A (bảng CHAO và
#       CAU_CO_DINH bên trên) cho ngắn lại — robot đang đi, không đứng một chỗ nói dài.
#       Không thêm dữ kiện nào bệnh viện chưa cung cấp. Bệnh viện muốn đổi chữ thì sửa
#       ở đây rồi chạy lại hai script — KHÔNG phải build lại APK.
# ════════════════════════════════════════════════════════════════════
# ════════════════════════════════════════════════════════════════════
#  BIỂU CẢM ROBOT
#
#  Mười clip gốc của OrionStar, nguồn 02-media/bieu-cam-robot/orionstar-nova-goc.
#  Anh Trường chốt 21/08/2026: DÙNG HẾT, không chỉ một clip nháy mắt như trước.
#  Dùng chung cho cả ba chỗ có biểu cảm: màn chờ · lúc dẫn đường · màn Trò chuyện.
#
#  Thứ tự trong danh sách không quan trọng — app tự xáo, chỉ giữ cho hai clip liền
#  nhau không trùng.
#
#  ⚠ Bốn clip cuối mang sắc thái KHÔNG VUI (giận, chóng mặt, ngủ gật, sốt ruột).
#    Anh Trường chốt dùng hết nên để nguyên. Muốn bỏ clip nào trước buổi lễ thì xoá
#    dòng đó ở đây rồi chạy lại hai script — KHÔNG phải build lại APK.
# ════════════════════════════════════════════════════════════════════
BIEU_CAM = [
    "emoji_happy",
    "emoji_laugh",
    "emoji_blink",
    "emoji_wink_1",
    "emoji_wink_2",
    "emoji_wink_3",
    "emoji_angry",
    "emoji_dizzy",
    "emoji_fallasleep",
    "emoji_impatient",
]

DI_VONG = {
    # Tính năng có sẵn hay không. Robot KHÔNG tự đi — anh Trường chốt 21/08/2026:
    # phải bấm một trong ba nút "Du hành" ở màn chọn thì robot mới lăn bánh.
    "bat": True,

    # Thứ tự trong danh sách CHÍNH LÀ LỘ TRÌNH: 1→2→3→4→5 rồi quay về 1.
    # Đặt điểm thành vòng khép kín quanh sảnh, đừng đặt kiểu đi rồi quay đầu.
    # ⚠ CẢ BA chế độ du hành đi CHUNG lộ trình này — chúng chỉ khác nhau ở câu nói.
    "diem": ["Diem 1", "Diem 2", "Diem 3", "Diem 4", "Diem 5"],

    "cach_chao_giay": 10,     # nghỉ bao lâu rồi đọc lại, tính TỪ LÚC ĐỌC XONG
    "cho_khach_giay": 30,     # không ai thao tác bao lâu thì robot đi tiếp
    "dem_di_tiep_giay": 8,    # đếm ngược hiện trên màn hình sau khi khách bấm "Xong"

    # Tốc độ đi vòng. Mặc định của hãng là 0,7 m/s và 1,2 rad/s — nhanh so với một sảnh
    # đông đại biểu đang đứng nói chuyện. Hạ xuống cho robot đi điềm đạm.
    "toc_do_thang": 0.5,
    "toc_do_xoay": 0.8,

    # Sai số toạ độ khi phải dùng LỐI DỰ PHÒNG nối từng điểm. Để rộng một mét để robot
    # coi như đã tới từ xa rồi đi tiếp luôn, không xoay xở canh đúng tâm điểm.
    # Để 0,2 như dẫn đường khách là mỗi điểm robot khựng lại một nhịp thấy rõ.
    "sai_so_met": 1.0,

    # ── BA CHẾ ĐỘ DU HÀNH ────────────────────────────────────────────────────────
    # Anh Trường chốt 21/08/2026: ba nút riêng, MỖI CHẾ ĐỘ CHỈ ĐỌC ĐÚNG MỘT CÂU, lặp
    # đi lặp lại suốt chuyến. Không xoay vòng nhiều câu như bản trước — người vận hành
    # chọn thẳng thông điệp muốn phát theo từng lúc trong buổi.
    #
    # ⚠ Chữ số trong câu đã chuyển sang chữ: robot đọc "22/8/2026" thành ra sai nhịp.
    #   Cổng chất lượng ở cuối file chặn mọi câu còn chữ số, đừng gõ số vào đây.
    "che_do": [
        {
            "ma": "1",
            "ten": "Du hành 1",
            "mo_ta": "Chào mừng Hội thảo khoa học",
            "cau": "Bệnh viện Hùng Vương trân trọng kính chào quý đại biểu. Chào mừng quý vị "
                   "đến tham dự Hội thảo khoa học Điều trị không xâm lấn bằng sóng siêu âm hội tụ.",
        },
        {
            "ma": "2",
            "ten": "Du hành 2",
            "mo_ta": "Giới thiệu hai sự kiện trong ngày",
            "cau": "Hôm nay, Bệnh viện Hùng Vương long trọng tổ chức Lễ đón nhận danh hiệu Anh "
                   "hùng Lao động và Lễ khai trương Đơn vị điều trị không xâm lấn bằng sóng siêu "
                   "âm hội tụ HIFU. Buổi chiều có hội thảo khoa học. Hôm nay, thứ Bảy ngày hai "
                   "mươi hai tháng tám năm hai nghìn không trăm hai mươi sáu, Bệnh viện Hùng "
                   "Vương long trọng tổ chức Lễ đón nhận danh hiệu Anh hùng Lao động do Đảng và "
                   "Nhà nước trao tặng, kết hợp Lễ khai trương Đơn vị điều trị không xâm lấn "
                   "bằng sóng siêu âm hội tụ HIFU.",
        },
        {
            "ma": "3",
            "ten": "Du hành 3",
            "mo_ta": "Mời tham quan Đơn vị HIFU",
            "cau": "Bệnh viện Hùng Vương trân trọng kính mời quý đại biểu, quý khách cùng di "
                   "chuyển tham quan Đơn vị điều trị không xâm lấn bằng sóng siêu âm hội tụ HIFU.",
        },
    ],
}


# ════════════════════════════════════════════════════════════════════
#  DỰNG FILE
# ════════════════════════════════════════════════════════════════════
def khong_dau(s):
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return s.replace("đ", "d").replace("Đ", "D").lower()


def kiem_tra():
    """Cổng chất lượng — sai thì DỪNG, không sinh file lỗi ra cho robot đọc."""
    loi = []

    # điểm bản đồ phải không dấu và tồn tại
    for k, v in DIEM.items():
        if khong_dau(v) != v.lower():
            loi.append("Điểm '%s' = '%s' còn dấu tiếng Việt" % (k, v))
        if "  " in v or v != v.strip():
            loi.append("Điểm '%s' = '%s' có khoảng trắng thừa" % (k, v))

    # mọi đích phải trỏ tới một điểm có thật
    for d in DICH:
        if d["diem"] not in DIEM:
            loi.append("Đích '%s' trỏ tới điểm '%s' không có trong bảng DIEM" % (d["ten"], d["diem"]))
        if not d["doc"].strip():
            loi.append("Đích '%s' chưa có lời thoại" % d["ten"])

    # luồng tư vấn HIFU phải trỏ tới đích có thật
    ids = {d["id"] for d in DICH}
    for n in TU_VAN_HIFU["nhanh"]:
        if n["dich_id"] not in ids:
            loi.append("Nhánh tư vấn '%s' trỏ tới đích id=%s không có" % (n["ten"], n["dich_id"]))

    # quy trình
    for b in QUY_TRINH:
        if b["dich_id"] is not None and b["dich_id"] not in ids:
            loi.append("Bước %d trỏ tới đích id=%s không có" % (b["buoc"], b["dich_id"]))

    # hỏi đáp: id không trùng, nhóm có thật, có đủ cách hỏi
    manhom = {n["ma"] for n in NHOM}
    thay = set()
    for h in HOI_DAP:
        if h["id"] in thay:
            loi.append("Hỏi đáp id=%d bị trùng" % h["id"])
        thay.add(h["id"])
        if h["nhom"] not in manhom:
            loi.append("Hỏi đáp id=%d thuộc nhóm '%s' không có" % (h["id"], h["nhom"]))
        if len(h["cach"]) < 3:
            loi.append("Hỏi đáp id=%d chỉ có %d cách hỏi — cần ít nhất 3"
                       % (h["id"], len(h["cach"])))
        if not h["dap"].strip():
            loi.append("Hỏi đáp id=%d chưa có câu trả lời" % h["id"])

    # ⚠ Câu robot đọc KHÔNG được chứa chữ số — robot đọc chữ số sai nhịp.
    def soi_so(nhan, cau):
        if any(c.isdigit() for c in cau):
            loi.append("%s còn CHỮ SỐ, phải viết bằng chữ: %s" % (nhan, cau[:70]))

    for d in DICH:
        soi_so("Lời thoại đích '%s'" % d["ten"], d["doc"])
    for k, v in CAU_CO_DINH.items():
        soi_so("Câu cố định '%s'" % k, v)
    for loai, c in CHAO.items():
        for khoa in ("cau", "cau_chieu"):
            for i, cau in enumerate(c.get(khoa) or []):
                soi_so("Lời chào %s.%s [%d]" % (loai, khoa, i), cau)
    for h in HOI_DAP:
        soi_so("Đáp id=%d" % h["id"], h["dap"])
    for b in QUY_TRINH:
        soi_so("Bước %d" % b["buoc"], b["doc"])
    for n in TU_VAN_HIFU["nhanh"]:
        soi_so("Nhánh '%s'" % n["ma"], n["doc"])

    # ── Đi vòng ──
    # Cổng này tồn tại vì mọi lỗi ở đây đều IM LẶNG trên máy thật: tên điểm sai một ký tự
    # thì robot bỏ qua điểm đó, câu chào có chữ số thì robot đọc sai nhịp giữa sảnh đông
    # người — không cái nào bắn ra thông báo lỗi.
    dv = DI_VONG
    if dv.get("bat"):
        ds = dv.get("diem") or []
        if len(ds) < 2:
            loi.append("Đi vòng cần ít nhất hai điểm, đang có %d" % len(ds))
        if len(set(ds)) != len(ds):
            loi.append("Danh sách điểm đi vòng có tên trùng nhau")
        for v in ds:
            if khong_dau(v) != v.lower():
                loi.append("Điểm đi vòng '%s' còn dấu tiếng Việt" % v)
            if "  " in v or v != v.strip():
                loi.append("Điểm đi vòng '%s' có khoảng trắng thừa" % v)

        cds = dv.get("che_do") or []
        if len(cds) < 1:
            loi.append("DI_VONG['che_do'] rỗng — không có chế độ du hành nào")
        mas = set()
        for cd in cds:
            nhan = "Chế độ du hành '%s'" % cd.get("ten", "?")
            if cd.get("ma") in mas:
                loi.append("%s trùng mã '%s'" % (nhan, cd.get("ma")))
            mas.add(cd.get("ma"))
            cau = (cd.get("cau") or "").strip()
            if not cau:
                loi.append("%s chưa có câu để đọc" % nhan)
                continue
            soi_so(nhan, cau)
            # eleven_v3 và giọng robot đọc ~18 ký tự/giây.
            # Trần 500 ký tự ~ hai mươi tám giây đọc.
            if len(cau) > 500:
                loi.append("%s dài %d ký tự, quá hai mươi tám giây đọc: %s…"
                           % (nhan, len(cau), cau[:50]))
            elif len(cau) > 260:
                print("  ! %s dài %d ký tự (~%d giây đọc) — robot đang đi, câu dài thì "
                      "khách đi ngang chỉ nghe được nửa câu." % (nhan, len(cau), len(cau) // 18))

        if dv.get("cach_chao_giay", 0) < 5:
            loi.append("cach_chao_giay phải từ năm giây trở lên")
        if dv.get("cho_khach_giay", 0) < 10:
            loi.append("cho_khach_giay phải từ mười giây trở lên")
        if not (0.1 <= dv.get("toc_do_thang", 0) <= 0.8):
            loi.append("toc_do_thang phải trong khoảng 0,1 đến 0,8 m/s")
        if dv.get("sai_so_met", 0) < 0.3:
            loi.append("sai_so_met dưới 0,3 m là robot khựng lại ở từng điểm")

        # Điểm đi vòng KHÔNG được trùng tên điểm dẫn đường: robot đi vòng ngang qua đó
        # thì khách đang được dẫn tới đó sẽ thấy hai lệnh đánh nhau.
        trung = set(ds) & (set(DIEM.values()) | {DIEM_VE_CHO, DIEM_TRAM_SAC})
        if trung:
            loi.append("Điểm đi vòng trùng tên điểm dẫn đường: %s" % ", ".join(sorted(trung)))

    # ── Biểu cảm ──
    # Thiếu file là hỏng IM LẶNG: video không nạp được, máy biểu cảm nhảy sang clip kế,
    # màn hình đen một nhịp mà không báo gì. Soi ở đây rẻ hơn nhiều so với soi trên robot.
    if not BIEU_CAM:
        loi.append("BIEU_CAM rỗng — màn chờ sẽ là một khung đen")
    thu_bc = os.path.join(HERE, "bieu-cam")
    for ten in BIEU_CAM:
        f = os.path.join(thu_bc, ten + ".mp4")
        if not os.path.exists(f):
            loi.append("Biểu cảm '%s' không có file %s.mp4 trong bieu-cam/" % (ten, ten))
    if len(set(BIEU_CAM)) != len(BIEU_CAM):
        loi.append("Danh sách BIEU_CAM có tên trùng nhau")

    if loi:
        print("DỪNG — dữ liệu chưa đạt:")
        for x in loi:
            print("  ✘", x)
        raise SystemExit(1)


def main():
    kiem_tra()

    data = {
        "don_vi": "Bệnh viện Hùng Vương",
        "su_kien": "Lễ đón nhận danh hiệu Anh hùng Lao động · Lễ khai trương Đơn vị HIFU · "
                   "Hội thảo khoa học HIFU",
        "ngay": "22/08/2026",
        "nguon": "Tài liệu bệnh viện cung cấp 20/08/2026 — "
                 "10-project/Benh-vien-Hung-Vuong/tu-lieu/",
        "cap_nhat": "20/08/2026",

        "diem": DIEM,
        "diem_ve_cho": DIEM_VE_CHO,
        "diem_tram_sac": DIEM_TRAM_SAC,

        "dich": DICH,
        "chao": CHAO,
        "cau": CAU_CO_DINH,
        "tu_van_hifu": TU_VAN_HIFU,
        "nhom": NHOM,
        "hoi_dap": HOI_DAP,
        "quy_trinh": QUY_TRINH,
        "chua_co": CHUA_CO,
        "bieu_cam": BIEU_CAM,
        "di_vong": DI_VONG,

        # Nút "Mời khách vào hội trường" phát LẶP cho tới khi bấm lần nữa
        # (anh Trường chốt 21/08/2026 bản 2). Nghỉ bấy nhiêu giây giữa hai lượt đọc —
        # để 0 là robot đọc nối đuôi không ngắt, nghe như máy hỏng.
        "moi_lap_nghi_giay": 5,
    }

    os.makedirs(os.path.dirname(RA), exist_ok=True)
    with io.open(RA, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("Đã ghi:", RA)
    print("  %d đích dẫn đường · %d cặp hỏi đáp · %d bước quy trình · %d điểm bản đồ"
          % (len(DICH), len(HOI_DAP), len(QUY_TRINH), len(DIEM) + 2))
    print("  Điểm cần đặt trên bản đồ robot — DẪN ĐƯỜNG:")
    for v in sorted(set(list(DIEM.values()) + [DIEM_VE_CHO, DIEM_TRAM_SAC])):
        print("     •", v)
    if DI_VONG.get("bat"):
        print("  Điểm cần đặt trên bản đồ robot — ĐI VÒNG (đúng thứ tự lộ trình):")
        for v in DI_VONG["diem"]:
            print("     •", v)
        print("     %d chế độ du hành, mỗi chế độ đọc lặp ĐÚNG MỘT câu:"
              % len(DI_VONG["che_do"]))
        for cd in DI_VONG["che_do"]:
            print("       · %s — %s (%d ký tự, ~%d giây đọc)"
                  % (cd["ten"], cd["mo_ta"], len(cd["cau"]), len(cd["cau"]) // 18))
        print("     Đọc lại sau %d giây · vắng người %d giây thì đi tiếp"
              % (DI_VONG["cach_chao_giay"], DI_VONG["cho_khach_giay"]))
    print("  %d clip biểu cảm dùng chung cho màn chờ · dẫn đường · trò chuyện"
          % len(BIEU_CAM))


if __name__ == "__main__":
    main()
