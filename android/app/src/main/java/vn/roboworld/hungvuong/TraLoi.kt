package vn.roboworld.hungvuong

import android.util.Log
import com.ainirobot.agent.base.llm.LLMMessage
import com.ainirobot.agent.base.llm.Role
import org.json.JSONArray
import org.json.JSONObject
import java.io.File
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.concurrent.Executors

/**
 * BỘ ĐIỀU PHỐI HỘI THOẠI — app tự cầm trịch, mô hình chỉ là một lời gọi CÓ KIỂM.
 *
 * Chép lối làm đã chạy được ở app Mông Dương (11/08) và app Uông Bí (17/08), đổi phần
 * dữ liệu sang KHO HỎI ĐÁP của sự kiện Bệnh viện Hùng Vương.
 *
 * Khác biệt lớn nhất so với hai app kia: ở đây mỗi câu hỏi có sẵn MỘT CÂU TRẢ LỜI
 * BỆNH VIỆN ĐÃ DUYỆT TỪNG CHỮ. Nội dung y khoa về HIFU không phải thứ để mô hình
 * diễn đạt lại — lệch một con số ("bảy mươi phần trăm" thành "chín mươi phần trăm")
 * là sai hẳn thông tin y tế, trước mặt một hội trường toàn bác sĩ.
 *
 * Nên đường đi ở đây có một lối tắt mà hai app kia không có:
 *
 *   nghe được câu (onASRResult) hoặc gõ chữ (Cau.hoiRobot) — CÙNG MỘT ĐƯỜNG
 *     → ① CẤP CỨU?            → hô ngay, KHÔNG hỏi mô hình
 *     → ② xin ý kiến y tế?     → từ chối, KHÔNG hỏi mô hình
 *     → ③ chưa có dữ liệu?     → nói thẳng chưa có, KHÔNG hỏi mô hình
 *     → ④ tra kho hỏi đáp tại chỗ, lấy MỨC TIN CẬY
 *     → ⑤ CHẮC CHẮN → đọc thẳng câu bệnh viện duyệt, KHÔNG hỏi mô hình  ← lối tắt
 *     → ⑥ chưa chắc → hỏi mô hình kèm ĐÚNG danh sách ứng viên
 *     → ⑦ KIỂM dòng DAP_ID → mới cho robot mở miệng
 *
 * Lối tắt ở bước ⑤ vừa an toàn hơn (không có chỗ cho mô hình chen vào) vừa nhanh hơn
 * (không phải chờ mạng), và nó xử lý phần lớn câu hỏi trong ngày.
 *
 * Nguyên tắc xuyên suốt: **việc an toàn chặn bằng MÃ, không chặn bằng lời dặn trong
 * prompt.** Prompt vẫn viết đầy đủ, nhưng không được tính là một lớp bảo vệ.
 */
object TraLoi {

    private const val TAG = "HVTraLoi"

    /** Mô hình chạy trên mạng, tra cứu chạy trên WebView — không được chặn luồng gọi. */
    private val tho = Executors.newSingleThreadExecutor()

    /* ── Những câu app TỰ soạn. Không câu nào đi qua mô hình. ── */

    private const val KHONG_CO_TRONG_KHO =
        "Câu hỏi này nằm ngoài thông tin tôi được cung cấp. Kính mời Quý vị liên hệ Ban tổ chức " +
        "hoặc gặp đội lễ tân tại bàn tiếp đón để được giải đáp ạ."

    private const val MO_HINH_HONG =
        "Xin lỗi Quý vị, lúc này tôi chưa nghĩ ra câu trả lời. Kính mời Quý vị chạm vào màn hình " +
        "để chọn câu hỏi có sẵn, hoặc hỏi đội lễ tân giúp tôi ạ."

    /**
     * Điểm vào duy nhất. Gọi được từ luồng bất kỳ — bên trong tự đẩy sang luồng phụ.
     * Cả lời nói (onASRResult) lẫn chữ gõ (Cau.hoiRobot) đều vào đây.
     */
    fun hoi(cauHoi: String) {
        val cau = cauHoi.trim()
        if (cau.length < 2) return
        tho.execute { xuLy(cau) }
    }

    private fun xuLy(cau: String) {
        // ── Lớp 1: CẤP CỨU. Chặn trước mọi thứ, kể cả trước khi tra cứu.
        if (MainApplication.chanCapCuuNeuCan(cau)) { ghiNhatKy(cau, "cap-cuu", "", "", null); return }

        // ── Lớp 2: xin ý kiến y tế cho chính mình. Robot không phải bác sĩ.
        if (MainApplication.chanHoiYTeNeuCan(cau)) { ghiNhatKy(cau, "hoi-y-te", "", "", null); return }

        // ── Lớp 3: những thứ bệnh viện chưa cung cấp (wifi, nhà vệ sinh, bãi xe…).
        if (MainApplication.chanChuaCoDuLieuNeuCan(cau)) { ghiNhatKy(cau, "chua-co", "", "", null); return }

        // ── Lớp 4: tra trong kho hỏi đáp, lấy cả độ tin cậy.
        val kho = runCatching { JSONObject(Cau.traKhoaChoAI(cau)) }.getOrNull()
        if (kho == null) {
            Log.w(TAG, "Không đọc được kết quả tra cứu — trả lời dự phòng")
            MainApplication.tuDoc(MO_HINH_HONG)
            ghiNhatKy(cau, "loi-tra-cuu", "", "", null)
            return
        }

        val muc = kho.optString("muc")
        val ungVien = kho.optJSONArray("ung_vien") ?: JSONArray()

        // ── Lớp 5: LỐI TẮT. Chắc chắn thì đọc thẳng câu bệnh viện duyệt.
        //
        // ⚠ Đây là đường đi của phần lớn câu hỏi trong ngày. Không gọi mô hình nghĩa là
        //   không có chỗ nào cho nó thêm bớt một chữ vào nội dung y khoa. Đừng "cải tiến"
        //   bằng cách cho mô hình soạn câu dẫn ở đây — được thêm một câu khách sáo,
        //   đổi lại mất tính bảo đảm và thêm một giây chờ mạng.
        if (muc == "chac" && ungVien.length() > 0) {
            val id = ungVien.getJSONObject(0).optInt("id")
            val dap = Cau.layDapAn(id)
            if (dap.isNotBlank()) {
                Log.d(TAG, "Lối tắt: đọc thẳng đáp án id=$id, không gọi mô hình")
                MainApplication.tuDoc(dap)
                ghiNhatKy(cau, "chac-loi-tat", id.toString(), "", null)
                return
            }
            Log.w(TAG, "Tra được id=$id nhưng lớp web trả đáp án rỗng — chuyển sang hỏi mô hình")
        }

        // ── Lớp 6: chưa chắc, hoặc không tra ra gì. Hỏi mô hình kèm ĐÚNG ứng viên.
        MainApplication.hoiMoHinh(dungTinNhan(cau, muc, ungVien)) { chu, loi ->
            if (chu == null) {
                Log.w(TAG, "Mô hình không trả lời: $loi")
                // Còn ứng viên thì tự trả lời bằng dữ liệu trong máy, đừng bỏ mặc khách đứng đó.
                val duPhong = if (ungVien.length() > 0)
                    Cau.layDapAn(ungVien.getJSONObject(0).optInt("id")) else ""
                MainApplication.tuDoc(duPhong.ifBlank { KHONG_CO_TRONG_KHO })
                ghiNhatKy(cau, muc, "", "loi:$loi", null)
            } else {
                docCauTraLoi(cau, muc, ungVien, chu)
            }
        }
    }

    /**
     * Dựng danh sách tin nhắn gửi mô hình.
     *
     * ⚠ CHỈ gửi id và CÂU HỎI. KHÔNG gửi câu trả lời — dù lớp web có sẵn.
     *   Gửi câu trả lời cho mô hình là mời nó diễn đạt lại nội dung y khoa mà bệnh viện
     *   đã duyệt từng chữ. App tự đọc phần đó sau câu dẫn của mô hình. Xem docCauTraLoi().
     *
     *   Đây cũng là lý do mô hình được giao việc rất hẹp: nó chỉ phải CHỌN xem trong mấy
     *   câu hỏi ứng viên thì câu nào đúng ý người vừa nói. Việc đó nó làm tốt; việc nhớ
     *   số liệu y khoa thì không.
     */
    private fun dungTinNhan(cau: String, muc: String, ungVien: JSONArray): List<LLMMessage> {
        val danhSach = if (ungVien.length() == 0) "(máy không tìm được mục nào khớp)"
        else (0 until ungVien.length()).joinToString("\n") { i ->
            val t = ungVien.getJSONObject(i)
            "[id=${t.optInt("id")}] ${t.optString("hoi")}"
        }

        val nhac = when (muc) {
            "chac"      -> "Máy khá chắc ứng viên đầu tiên là đúng."
            "chua-chac" -> "Máy CHƯA CHẮC. Nếu bạn cũng chưa chắc thì hãy hỏi lại cho rõ " +
                           "thay vì đoán bừa."
            else        -> "Máy không tìm được mục nào khớp."
        }

        return listOf(
            LLMMessage(Role.SYSTEM, MainApplication.PERSONA + "\n\n" + MainApplication.LUAT_TRA_LOI),
            LLMMessage(Role.USER,
                "DANH SÁCH ỨNG VIÊN (máy vừa tra trong kho hỏi đáp bệnh viện cài sẵn trong robot):\n" +
                danhSach + "\n\n" + nhac + "\n\n" +
                "Quý vị vừa nói: \"" + cau + "\"")
        )
    }

    /* ══════════════════════════════════════════════════════════════════
       CHỐT AN TOÀN — kiểm câu trả lời của mô hình TRƯỚC KHI robot mở miệng
       ══════════════════════════════════════════════════════════════════ */

    /** Dòng cuối bắt buộc, ví dụ `DAP_ID: 3` hoặc `DAP_ID: KHONG_CO`. */
    private val DONG_ID = Regex("""DAP_ID\s*:\s*([A-Za-z0-9_]+)""", RegexOption.IGNORE_CASE)

    private fun docCauTraLoi(cau: String, muc: String, ungVien: JSONArray, chuGoc: String) {
        val khop = DONG_ID.find(chuGoc)
        val ma = khop?.groupValues?.get(1)?.uppercase().orEmpty()
        val chu = DONG_ID.replace(chuGoc, "").trim()

        // Thiếu hẳn dòng mã → coi như không hợp lệ. Sai theo hướng an toàn.
        if (ma.isEmpty()) {
            Log.w(TAG, "Mô hình bỏ dòng DAP_ID — bỏ câu trả lời. Nguyên văn: $chuGoc")
            MainApplication.tuDoc(KHONG_CO_TRONG_KHO)
            ghiNhatKy(cau, muc, "", "thieu-ma", chuGoc)
            return
        }

        if (ma == "TAM_SU") {
            /* Chào hỏi, cảm ơn, nói chuyện ngoài lề: để mô hình nói tự nhiên.
               Chặn kèm CHỮ SỐ — số ở đây chỉ có thể là giờ giấc hoặc số liệu y khoa,
               hai thứ mô hình không được phép tự nói. */
            val an = chu.any { it.isDigit() }
            if (an) Log.w(TAG, "TAM_SU nhưng câu có chữ số — bỏ: $chu")
            MainApplication.tuDoc(if (an) "Dạ vâng ạ." else chu.ifBlank { "Dạ vâng ạ." })
            ghiNhatKy(cau, muc, "TAM_SU", "", chuGoc)
            return
        }

        if (ma == "KHONG_CO") {
            /* Hai tình huống rất khác nhau:
             *  a) Máy không tra ra gì → mô hình hay "giúp thêm" bằng kiến thức nền của nó,
             *     đúng cái đã làm nó bịa danh sách giấy tờ ở app Mông Dương. Dùng CÂU CỨNG.
             *  b) Máy có ứng viên nhưng chưa chắc → mô hình hỏi lại rất đúng việc
             *     ("Quý vị muốn hỏi về chương trình buổi lễ hay về kỹ thuật ạ?"), mà bảng
             *     câu hỏi đang hiện sẵn trên màn hình để khách chọn. Cho nói.
             * Chặn kèm: câu hỏi lại mà có CHỮ SỐ thì vứt. */
            val hoiLai = ungVien.length() > 0 && chu.isNotBlank() && !chu.any { it.isDigit() }
            if (hoiLai) {
                MainApplication.tuDoc(chu)
            } else {
                if (chu.any { it.isDigit() }) Log.w(TAG, "KHONG_CO nhưng câu có chữ số — bỏ: $chu")
                MainApplication.tuDoc(KHONG_CO_TRONG_KHO)
            }
            ghiNhatKy(cau, muc, if (hoiLai) "KHONG_CO-hoi-lai" else "KHONG_CO", "", chuGoc)
            return
        }

        // Mã phải là id của MỘT trong những ứng viên vừa gửi đi.
        val id = ma.toIntOrNull()
        val hopLe = (0 until ungVien.length())
            .map { ungVien.getJSONObject(it) }
            .any { it.optInt("id") == id }

        if (!hopLe || id == null) {
            Log.w(TAG, "Mô hình trả id LẠC '$ma' — không nằm trong danh sách ứng viên. Bỏ câu trả lời.")
            MainApplication.tuDoc(KHONG_CO_TRONG_KHO)
            ghiNhatKy(cau, muc, "lac:$ma", "", chuGoc)
            return
        }

        /* Hợp lệ: robot đọc câu dẫn của mô hình, RỒI app tự đọc nội dung lấy nguyên văn
           từ kho hỏi đáp bệnh viện duyệt. Nội dung y khoa không đi qua mô hình lần nào. */
        val dap = Cau.layDapAn(id)
        if (dap.isBlank()) {
            Log.w(TAG, "id=$id hợp lệ nhưng lớp web trả đáp án rỗng")
            MainApplication.tuDoc(KHONG_CO_TRONG_KHO)
            ghiNhatKy(cau, muc, "rong:$ma", "", chuGoc)
            return
        }
        val noi = buildString {
            if (chu.isNotBlank()) { append(chu); if (!chu.endsWith(".")) append("."); append(" ") }
            append(dap)
        }
        MainApplication.tuDoc(noi)
        ghiNhatKy(cau, muc, ma, "", chuGoc)
    }

    /* ══════════════════════════════════════════════════════════════════
       NHẬT KÝ — để hiệu chỉnh ngưỡng và để biết chi phí
       ══════════════════════════════════════════════════════════════════ */

    /**
     * Ghi mỗi lượt hỏi ra thẻ nhớ. Lấy về bằng:
     *
     *   adb pull /sdcard/Android/data/vn.roboworld.hungvuong/files/nhat-ky
     *
     * Dùng getExternalFilesDir nên KHÔNG cần xin quyền lưu trữ, và gỡ app là dọn sạch theo.
     *
     * ⚠ File này có thể chứa lời khách kể về bệnh tình của mình. Đó là dữ liệu riêng tư.
     *   Lấy về để hiệu chỉnh xong thì XOÁ, đừng để tồn trên máy, và đừng gửi ra ngoài
     *   Roboworld khi chưa hỏi bệnh viện.
     */
    private fun ghiNhatKy(cau: String, muc: String, ma: String, loi: String, traLoi: String?) {
        runCatching {
            val ctx = MainApplication.boiCanh ?: return
            val thuMuc = File(ctx.getExternalFilesDir(null), "nhat-ky").apply { mkdirs() }
            val ngay = SimpleDateFormat("yyyy-MM-dd", Locale.US).format(Date())
            val gio = SimpleDateFormat("HH:mm:ss", Locale.US).format(Date())
            val dong = listOf(gio, muc, ma, loi, cau.replace('\n', ' '),
                              (traLoi ?: "").replace('\n', ' ').take(400))
                .joinToString("\t") + "\n"
            File(thuMuc, "hoi-$ngay.tsv").appendText(dong)
        }.onFailure { Log.w(TAG, "Không ghi được nhật ký: ${it.message}") }
    }
}
