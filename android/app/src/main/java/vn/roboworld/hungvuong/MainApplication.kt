package vn.roboworld.hungvuong

import android.app.Application
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.util.Log
import com.ainirobot.agent.AgentCore
import com.ainirobot.agent.AppAgent
import com.ainirobot.agent.LLMCallback
import com.ainirobot.agent.OnTranscribeListener
import com.ainirobot.agent.action.Action
import com.ainirobot.agent.action.Actions
import com.ainirobot.agent.assit.LLMResponse
import com.ainirobot.agent.base.Transcription
import com.ainirobot.agent.base.llm.LLMConfig
import com.ainirobot.agent.base.llm.LLMMessage
import com.ainirobot.agent.base.llm.Role

/**
 * Điểm khởi động của app lễ tân bệnh viện.
 *
 * Phân vai giữa hai tầng — chỗ dễ hiểu nhầm nhất:
 *
 *   • RobotApi / SkillApi  → dẫn đường và đọc thành tiếng. Đây là phần app sống bằng,
 *                            không phụ thuộc Agent SDK.
 *   • Agent SDK 0.4.7      → nghe (ASR) và gọi mô hình ngôn ngữ. App KHÔNG để AgentOS
 *                            tự hoạch định — xem `isDisablePlan` bên dưới và TraLoi.kt.
 *
 * Toàn bộ phần AI ở đây chép lối làm đã chạy được trên app tra cứu thủ tục Mông Dương
 * (11/08/2026). Bốn thứ dưới đây từng làm mất nhiều ngày ở app kia, đừng đổi nếu chưa
 * đọc kỹ chú thích tại chỗ:
 *   ① SDK phải lấy từ gói offline, không lấy JitPack   (xem app/build.gradle.kts)
 *   ② `businessInfo` phải là null, không được là ""     (xem hoiMoHinh)
 *   ③ bốn công tắc của hãng đều mặc định SAI với app này (xem onCreate)
 *   ④ việc an toàn chặn bằng MÃ, không chặn bằng prompt  (xem ba hàm chan…NeuCan)
 *
 * LƯU Ý: mỗi app CHỈ ĐƯỢC CÓ MỘT thực thể AppAgent.
 */
class MainApplication : Application() {

    companion object {
        private const val TAG = "BVApp"

        @Volatile private var agent: AppAgent? = null

        /** Bối cảnh ứng dụng — TraLoi cần để ghi nhật ký ra thẻ nhớ. */
        @Volatile var boiCanh: android.content.Context? = null; private set

        /**
         * AI đám mây đã trả lời thật hay chưa. Lớp web đọc cờ này để quyết định có hiện
         * nút micro không.
         *
         * ⚠ KHÔNG suy ra từ "agent != null". Dựng được AppAgent chỉ nghĩa là hàm khởi tạo
         *   không ném lỗi — nó vẫn dựng thành công khi dịch vụ của hãng không bind được.
         *   Cờ này chỉ bật khi mô hình trả lời thật, hoặc khi nghe được một câu ASR thật.
         *   Một nút micro bấm vào không phản ứng, trước mặt lãnh đạo bệnh viện, tệ hơn
         *   nhiều so với việc không có nút.
         */
        @Volatile private var agentSanSang = false

        /**
         * CỔNG AI — anh Trường chốt 21/08/2026: micro và bộ não hội thoại của hãng chỉ
         * được sống khi khách ĐANG Ở màn Giao tiếp AI. Ra khỏi màn đó là tắt ngay.
         *
         * ⚠ Vì sao phải là một cái cổng ở TẦNG KOTLIN chứ không chỉ tắt mic ở lớp web:
         *   `isMicrophoneMuted = true` là lời đề nghị với dịch vụ của hãng, không phải
         *   cái công tắc nguồn. Đã đo được ở app Mông Dương: có lúc AgentOS vẫn bắn
         *   `onASRResult` sau khi đã đặt cờ tắt tiếng — nghĩa là robot vẫn nghe lỏm và
         *   vẫn nghĩ ra câu trả lời, chỉ là không ai bảo nó im. Ở giữa một hội trường
         *   toàn bác sĩ, robot tự dưng lên tiếng là chuyện không sửa được bằng lời xin lỗi.
         *
         *   Nên ngoài việc tắt mic, mọi câu ASR/TTS nghe được khi cổng đóng đều bị VỨT
         *   NGAY tại callback, không đi tiếp vào TraLoi, không hiện lên màn hình.
         */
        @Volatile private var congAIMo = false

        /** Đã thăm dò mô hình lần nào chưa — chỉ làm ở lần đầu MỞ CỔNG, không làm lúc
         *  khởi động app. Thăm dò lúc khởi động là gọi lên đám mây của hãng trong khi
         *  khách còn chưa bấm nút nào. */
        @Volatile private var daThamDo = false

        /** Khách vào màn Giao tiếp AI. */
        fun moCongAI() {
            if (congAIMo) return
            congAIMo = true
            Log.d(TAG, "MỞ cổng AI — micro và bộ não hãng bắt đầu hoạt động")
            batMicro()
            if (!daThamDo) { daThamDo = true; thamDoAI() }
        }

        /** Khách rời màn Giao tiếp AI — tắt hẳn, kể cả câu đang nói dở. */
        fun dongCongAI() {
            if (!congAIMo) return
            congAIMo = false
            Log.d(TAG, "ĐÓNG cổng AI — tắt micro, vứt mọi câu nghe được từ đây")
            tatMicro()
            /* Cắt luôn câu mô hình đang đọc dở. Không cắt thì khách bấm "Quay lại" xong
               robot vẫn nói nốt câu trả lời cho một màn hình đã biến mất. */
            runCatching { AgentCore.stopTTS() }
        }

        fun congAIDangMo(): Boolean = congAIMo

        fun batMicro() = datMicro(false)
        fun tatMicro() = datMicro(true)

        /**
         * ⚠ Mic và "nghe không cần đánh thức" phải đi CÙNG NHAU, đặt ở đúng một chỗ này.
         *
         * `isEnableWakeFree` mặc định BẬT. Bật nghĩa là robot nghe và tự đáp mà không cần
         * từ đánh thức — ở app Mông Dương chính nó gây ra chuyện **lúc dẫn đường robot tự
         * nói bằng giọng AI**, chồng lên giọng đọc SkillApi của app: dọc đường có ai nói
         * câu gì là AgentOS bắt lời rồi trả lời luôn.
         *
         * Ở bệnh viện chuyện đó còn tệ hơn: sảnh đông, robot bắt lời người lạ giữa lúc
         * đang dẫn một người bệnh đi.
         *
         * Tắt hẳn thì màn Trò chuyện mất khả năng nghe liên tục. Nên buộc nó bám theo
         * trạng thái mic: mic mở mới cho nghe tự do, mic đóng là câm hẳn.
         */
        private fun datMicro(tat: Boolean) {
            runCatching {
                AgentCore.isMicrophoneMuted = tat
                AgentCore.isEnableWakeFree = !tat
                Log.d(TAG, "Micro: tắt tiếng=${AgentCore.isMicrophoneMuted} · " +
                           "nghe tự do=${AgentCore.isEnableWakeFree}")
            }.onFailure { Log.w(TAG, "Không đặt được trạng thái micro: ${it.message}") }
        }

        fun micDangMo(): Boolean = runCatching { !AgentCore.isMicrophoneMuted }.getOrDefault(false)

        /** Xoá ngữ cảnh hội thoại — gọi mỗi khi robot về màn chờ.
         *  Ở bệnh viện đây không chỉ là chuyện gọn gàng: chuyện bệnh tình của người trước
         *  không được dính sang lượt của người sau. */
        fun xoaNguCanh() = runCatching { AgentCore.clearContext() }.isSuccess

        /**
         * Kể cho mô hình biết trên màn hình đang có gì.
         *
         * ⚠ Kênh này CHỈ là mô tả màn hình đang hiện, KHÔNG phải kho tri thức. Hãng xác
         *   nhận (phản hồi 11/08/2026, câu A10) mô hình không dùng nó để trả lời câu hỏi
         *   kiến thức. Sự thật cố định (ba toà nhà, phạm vi robot đi được) phải đặt trong
         *   PERSONA; nội dung khoa phòng đi theo danh sách ứng viên trong prompt, xem TraLoi.
         */
        fun moTaManHinh(mo: String) {
            runCatching { AgentCore.uploadInterfaceInfo(mo) }
                .onSuccess { Log.d(TAG, "Đã gửi mô tả màn hình (${mo.length} ký tự)") }
                .onFailure { Log.w(TAG, "Không gửi được mô tả màn hình: ${it.message}") }
        }

        /**
         * Gọi thẳng mô hình ngôn ngữ, KHÔNG qua bộ hoạch định Action của AgentOS.
         * Đây là đường chính để robot trả lời, và là thứ chính hãng khuyên dùng.
         *
         * ⚠ Khác API 0.2.2 ở ba chỗ, sửa nhầm là không biên dịch được:
         *   · callback đổi từ `TaskCallback` sang `LLMCallback`
         *   · `llm()` thêm tham số `stream: Boolean` trước callback
         *   · callback nay trả về CẢ CÂU TRẢ LỜI (`LLMResponse`), không còn chỉ 0/1
         *
         * ⚠ `LLMConfig.fileSearch` (tham số thứ 4) đã bị BỎ — máy chủ ngừng đọc từ
         *   26/08/2025. Đặt true hay false đều vô nghĩa.
         *
         * ⚠⚠ `businessInfo` (tham số thứ 5) PHẢI là `null`, KHÔNG được là `""`.
         *   Đây là nguyên nhân của hai ngày đứng hình ở app Mông Dương: truyền chuỗi rỗng
         *   thì máy chủ hiểu là "có businessInfo" rồi đi tra một hồ sơ rỗng, tra không ra
         *   nên trả `status=2, result=null` sau ~355 ms — không lỗi, không lý do, không log.
         *   Quy ước mã trả về: **status=1 là thành công**, status=2 là máy chủ thất bại.
         *
         * @param khiXong gọi trên luồng phụ với (câu trả lời, lỗi). Một trong hai là null.
         */
        fun hoiMoHinh(danhSachTin: List<LLMMessage>, khiXong: (String?, String?) -> Unit) {
            val ok = runCatching {
                /* 400 token đủ cho hai câu dẫn cộng dòng KHOA_ID. 20 giây: quá mức đó thì
                   người bệnh đã bỏ đi rồi, chờ thêm vô nghĩa. */
                val cauHinh = LLMConfig(0.6f, 400, 20, false, null)
                AgentCore.llm(danhSachTin, cauHinh, 20_000L, false, object : LLMCallback {
                    override fun onTaskEnd(status: Int, result: LLMResponse?) {
                        val chu = result?.message?.content.orEmpty()
                        val tk = result?.tokenCost
                        Log.d(TAG, "hoiMoHinh: status=$status · ${result?.elapsedTime ?: -1f}s · " +
                                   "token prompt=${tk?.promptTokens ?: -1} " +
                                   "completion=${tk?.completionTokens ?: -1} " +
                                   "total=${tk?.totalTokens ?: -1}")
                        // In nguyên đối tượng trả về: lúc hãng từ chối, lý do nằm ở đây chứ
                        // không ở logcat của AgentService. Đây là thứ để gửi cho hãng.
                        Log.d(TAG, "hoiMoHinh: nguyên văn = $result")
                        if (status == 1 && chu.isNotBlank()) {
                            if (!agentSanSang) { agentSanSang = true; Cau.baoAISanSang(true) }
                            khiXong(chu, null)
                        } else khiXong(null,
                            listOfNotNull(
                                "status=$status",
                                result?.status?.takeIf { it.isNotBlank() }?.let { "trạng thái=$it" },
                                result?.error?.takeIf { it.isNotBlank() }?.let { "lỗi=$it" },
                                if (result == null) "không có dữ liệu trả về" else null
                            ).joinToString(" · "))
                    }
                })
            }.isSuccess
            if (!ok) khiXong(null, "không gọi được mô hình")
        }

        /**
         * CHẨN ĐOÁN — hỏi mô hình một câu vu vơ để biết đường lên đám mây có thông không.
         * Gõ trong DevTools:  CAU.thuLLM('Một cộng một bằng mấy?', false)
         * Xem kết quả:        adb logcat -s BVApp
         */
        fun thuLLM(cauHoi: String, @Suppress("UNUSED_PARAMETER") khongDungNua: Boolean) {
            Log.d(TAG, "thuLLM: hỏi '$cauHoi'")
            hoiMoHinh(
                listOf(
                    LLMMessage(Role.SYSTEM, "Bạn là robot lễ tân. Trả lời ngắn gọn bằng tiếng Việt."),
                    LLMMessage(Role.USER, cauHoi)
                )
            ) { chu, loi ->
                Log.d(TAG, "thuLLM: ${if (chu != null) "TRẢ LỜI ĐƯỢC: $chu" else "HỎNG: $loi"}")
                Cau.guiLoiNoi("robot",
                    if (chu != null) "[chẩn đoán] $chu" else "[chẩn đoán] Mô hình không trả lời: $loi",
                    true)
            }
        }

        /**
         * Thăm dò một lần lúc khởi động: mô hình đám mây có trả lời thật không.
         * Chỉ khi trả về status=1 thì lớp web mới hiện nút micro.
         *
         * Đây là phép thử ĐẦU-CUỐI, không phải kiểm tra "hàm có tồn tại không".
         * Bài học từ app Mông Dương: `webkitSpeechRecognition` CÓ tồn tại trong WebView
         * robot, `batMic()` gọi được, `AppAgent` dựng được — nhưng bấm nút mic thì chết
         * câm suốt hai tuần. **Mọi phép kiểm "có hàm không" đều đánh lừa.**
         */
        private fun thamDoAI() {
            Handler(Looper.getMainLooper()).postDelayed({
                hoiMoHinh(listOf(LLMMessage(Role.USER, "Xin chào"))) { chu, loi ->
                    Log.d(TAG, "Thăm dò AI: ${if (chu != null) "THÔNG — $chu" else "chưa thông — $loi"}")
                    Cau.baoAISanSang(chu != null)
                }
            }, 4_000L)   // chờ Agent SDK bind xong rồi mới thử
        }

        /** Thông tin để tự kiểm lúc lắp đặt, và để lớp web quyết định có hiện nút mic không. */
        fun thongTinAI(): String {
            val appId = runCatching { AgentCore.appId }.getOrNull()
            return """{"appId":${org.json.JSONObject.quote(appId ?: "")},""" +
                   """"coAgent":${agent != null},""" +
                   """"agentSanSang":$agentSanSang,""" +
                   """"micDangMo":${micDangMo()}}"""
        }

        /* ══════════════════════════════════════════════════════════════
           BA CHỐT AN TOÀN — chặn bằng MÃ, không chặn bằng lời dặn

           Vì sao không tin vào setObjective: ở app Mông Dương đã dặn rõ *"kho chưa có
           hộ tịch, gặp mấy việc đó phải nói rõ là chưa được nạp, tuyệt đối đừng đoán"*,
           nhưng đo ngày 11/08/2026: hỏi "tôi muốn làm giấy khai sinh cho con" thì robot
           KHÔNG gọi Action, tự trả lời luôn *"Anh cần chuẩn bị: tờ khai đăng ký khai
           sinh, giấy chứng…"* — bịa từ kiến thức nền của mô hình.

           Ở bệnh viện, cái giá của một câu bịa cao hơn nhiều so với ở uỷ ban.
           ══════════════════════════════════════════════════════════════ */

        /**
         * ① CẤP CỨU — chặn trước mọi thứ khác.
         *
         * ⚠ App này KHÁC app Uông Bí: ở đây robot đứng trong khu vực sự kiện, và bệnh viện
         *   KHÔNG cung cấp vị trí khoa cấp cứu. Nên robot chỉ HÔ TO gọi nhân viên y tế,
         *   tuyệt đối không chỉ đường và không dẫn. Chỉ sai chỗ trong tình huống cấp cứu
         *   còn tệ hơn nói thẳng là mình không biết.
         *
         * Chỉ gồm những từ KHÔNG THỂ hiểu nhầm. Cố ý KHÔNG đưa "khó thở" trơn vào đây.
         */
        private val TU_CAP_CUU = Regex(
            "cấp cứu|cap cuu|nguy kịch|nguy kich|ngất xỉu|ngat xiu|bất tỉnh|bat tinh|" +
            "co giật|co giat|đột quỵ|dot quy|tai biến|tai bien|" +
            "không thở được|khong tho duoc|khó thở quá|kho tho qua|ngạt thở|ngat tho|" +
            "chảy máu nhiều|chay mau nhieu|băng huyết|bang huyet|" +
            "ngộ độc|ngo doc|hóc|sặc|tai nạn|tai nan|đau ngực dữ dội|dau nguc du doi",
            RegexOption.IGNORE_CASE
        )

        /**
         * ② XIN Ý KIẾN Y TẾ CHO CHÍNH MÌNH — robot không phải bác sĩ.
         *
         * ⚠ CHỖ NÀY KHÁC HẲN APP UÔNG BÍ, đọc kỹ trước khi sửa.
         *
         * Bệnh viện ĐÃ DUYỆT sẵn câu trả lời cho hàng loạt câu hỏi chuyên môn về HIFU:
         * "có đau không", "có an toàn không", "ai không làm được", "sau điều trị có thai
         * được không". Đó là kiến thức chung, robot ĐƯỢC PHÉP đọc nguyên văn.
         *
         * Thứ phải chặn là câu hỏi về TRƯỜNG HỢP CỦA CHÍNH NGƯỜI ĐANG HỎI — "tôi bị u xơ
         * thì có làm được không", "trường hợp của em có nên mổ không". Đó là tư vấn y tế
         * cá nhân, phải để bác sĩ.
         *
         * Nên phép thử ở đây là HAI VẾ, phải khớp CẢ HAI:
         *   · có đại từ ngôi thứ nhất / người nhà  (tôi, em, cháu, mình, vợ, mẹ…)
         *   · có động từ xin ý kiến                (có nên, có được không, bị gì, chẩn đoán…)
         *
         * Dùng một regex gộp như app Uông Bí là chặn nhầm "HIFU có nguy hiểm không" —
         * câu mà bệnh viện đã soạn sẵn câu trả lời. Đã cân nhắc, không phải bỏ sót.
         */
        private val NGOI_THU_NHAT = Regex(
            "\\btôi\\b|\\btoi\\b|\\bem\\b|\\bcháu\\b|\\bchau\\b|\\bmình\\b|\\bminh\\b|" +
            "\\bcon (tôi|em|mình)\\b|\\bvợ (tôi|em)\\b|\\bmẹ (tôi|em)\\b|\\bchị (tôi|em)\\b|" +
            "trường hợp của|truong hop cua",
            RegexOption.IGNORE_CASE
        )
        private val XIN_Y_KIEN = Regex(
            "bị (bệnh )?gì|bi gi|có nên|co nen|nên mổ|nen mo|có phải mổ|co phai mo|" +
            "có cần mổ|co can mo|làm được không|lam duoc khong|" +
            "có sao không|co sao khong|có nặng không|co nang khong|" +
            "chẩn đoán|chan doan|khám giúp|kham giup|" +
            "uống thuốc gì|uong thuoc gi|nên uống|nen uong|dùng thuốc gì|dung thuoc gi|" +
            "xem (giúp|hộ|giùm).{0,12}kết quả|" +
            "kết quả (xét nghiệm|siêu âm|chụp).{0,20}(sao|thế nào|gì)",
            RegexOption.IGNORE_CASE
        )

        /**
         * ③ CHƯA CÓ DỮ LIỆU — bệnh viện chưa cung cấp.
         *
         * ⚠ CỐ Ý RẤT NGẮN. Danh sách này chỉ gồm thứ bệnh viện thật sự chưa đưa, và
         *   chưa đưa thì không đoán được: wifi, nhà vệ sinh, bãi xe, căn tin, giá điều trị.
         *
         * ⚠ TUYỆT ĐỐI KHÔNG bê nguyên danh sách của app Uông Bí sang. Bên đó chặn cả
         *   "mấy giờ" và "số điện thoại" — ở đây "mấy giờ khai mạc" và "liên hệ ở đâu"
         *   là hai câu bệnh viện ĐÃ soạn sẵn câu trả lời (mục hỏi đáp số 2, 4, 5, 23).
         *   Chặn chúng là robot từ chối đúng những câu khách hỏi nhiều nhất trong ngày.
         *
         * Câu nào không nằm trong danh sách này mà kho cũng không tra ra thì đã có lưới
         * cuối: bộ tìm kiếm trả "khong-thay" → robot đọc câu "ngoài phạm vi" của bệnh viện.
         */
        private val TU_CHUA_CO = Regex(
            "wifi|wi-fi|mật khẩu mạng|mat khau mang|mạng không dây|" +
            "nhà vệ sinh|nha ve sinh|toilet|\\bwc\\b|đi vệ sinh|" +
            "gửi xe|gui xe|bãi xe|bai xe|giữ xe|giu xe|đậu xe|dau xe|đỗ xe|" +
            "căn tin|can tin|căng tin|quán ăn|quan an|chỗ ăn|ăn trưa ở đâu|" +
            "giá (điều trị|dịch vụ)|gia (dieu tri|dich vu)|" +
            "chi phí (điều trị|làm)|chi phi (dieu tri|lam)|" +
            "(điều trị|làm) hifu.{0,15}bao nhiêu tiền|hết bao nhiêu tiền|" +
            "phí tham dự|phi tham du|lệ phí|le phi",
            RegexOption.IGNORE_CASE
        )

        /* ⚠ KHÔNG chỉ đường tới khoa cấp cứu — bệnh viện chưa cung cấp vị trí, mà đây
           cũng không phải khu khám bệnh. Robot hô to để người xung quanh nghe thấy.
           Robot đi 0,5–0,8 m/s, chậm hơn người chạy: dẫn là làm chậm người ta. */
        private const val LOI_CAP_CUU =
            "Có người cần cấp cứu! Xin nhân viên y tế tới hỗ trợ ngay! " +
            "Quý vị đừng chờ tôi, tôi đi chậm lắm. Xin gọi ngay nhân viên y tế " +
            "hoặc bảo vệ đang đứng gần đây nhất giúp tôi ạ."

        private const val LOI_HOI_Y_TE =
            "Tôi là robot lễ tân nên không thể tư vấn về sức khỏe của riêng Quý vị được ạ. " +
            "Trường hợp cụ thể cần bác sĩ thăm khám trực tiếp mới trả lời được. " +
            "Kính mời Quý vị tới quầy chăm sóc khách hàng để đăng ký khám ạ."

        private const val LOI_CHUA_CO =
            "Phần này tôi chưa được cung cấp thông tin nên không dám nói, sợ nói sai thì " +
            "Quý vị mất công. Kính mời Quý vị hỏi đội lễ tân tại bàn tiếp đón giúp tôi ạ."

        /**
         * Câu mà CHÍNH APP vừa cho robot đọc.
         *
         * Robot đọc câu nào thì onTTSResult cũng bắn từng mẩu chữ về ("Phần này tôi",
         * "Phần này tôi chưa được"…). Câu do app tự soạn thì app đã đưa lên màn hình rồi;
         * để mẩu chữ bắn về nữa là khung chat hiện lặp bốn năm lần cùng một câu.
         */
        @Volatile private var tuNoi: String = ""

        /**
         * ROBOT ĐỌC MỘT CÂU DO CHÍNH APP SOẠN.
         * Gom về một chỗ vì ba việc phải đi cùng nhau, thiếu một là lỗi:
         *   · nhớ câu vừa đọc (tuNoi) để onTTSResult khỏi đẩy lên màn hình lần nữa
         *   · đọc thành tiếng bằng SkillApi — đường này chạy tốt từ đầu, không đụng vào
         *   · hiện luôn lên khung chat cho người đứng xa đọc được
         */
        fun tuDoc(cau: String) {
            if (cau.isBlank()) return
            tuNoi = cau
            RobotHelper.doc(cau) {}
            Cau.guiLoiNoi("robot", cau, true)
        }

        /** Trả true nếu đã chặn xong — đừng hỏi mô hình nữa. */
        fun chanCapCuuNeuCan(cau: String): Boolean {
            if (!TU_CAP_CUU.containsMatchIn(cau)) return false
            Log.w(TAG, "CHẶN CẤP CỨU: '$cau'")
            runCatching { AgentCore.stopTTS() }
            Cau.moManCapCuu()
            tuDoc(LOI_CAP_CUU)
            return true
        }

        /** Hai vế phải khớp CẢ HAI — xem chú thích dài ở XIN_Y_KIEN. */
        fun chanHoiYTeNeuCan(cau: String): Boolean {
            if (!NGOI_THU_NHAT.containsMatchIn(cau)) return false
            if (!XIN_Y_KIEN.containsMatchIn(cau)) return false
            Log.w(TAG, "CHẶN XIN Ý KIẾN Y TẾ: '$cau'")
            runCatching { AgentCore.stopTTS() }
            tuDoc(LOI_HOI_Y_TE)
            return true
        }

        fun chanChuaCoDuLieuNeuCan(cau: String): Boolean {
            if (!TU_CHUA_CO.containsMatchIn(cau)) return false
            Log.w(TAG, "CHẶN CHƯA CÓ DỮ LIỆU: '$cau'")
            runCatching { AgentCore.stopTTS() }
            tuDoc(LOI_CHUA_CO)
            return true
        }

        /* ══════════════════════════════════════════════════════════════
           LỜI DẶN GỬI MÔ HÌNH — dùng chung cho setPersona và cho TraLoi
           ══════════════════════════════════════════════════════════════ */

        /**
         * ⚠ NHỮNG SỰ THẬT CỐ ĐỊNH PHẢI ĐẶT Ở ĐÂY, KHÔNG ĐẶT Ở uploadInterfaceInfo.
         * Hãng xác nhận kênh uploadInterfaceInfo chỉ là MÔ TẢ MÀN HÌNH ĐANG HIỆN, mô hình
         * không dùng nó để trả lời câu hỏi kiến thức.
         *
         * Quy tắc: sự thật KHÔNG ĐỔI (ba toà nhà, phạm vi robot đi được) → đây.
         *          Thứ THAY ĐỔI theo màn hình → uploadInterfaceInfo.
         *          Vị trí khoa phòng → danh sách ứng viên trong prompt, xem TraLoi.kt.
         */
        val PERSONA =
            "Bạn là robot lễ tân của Bệnh viện Hùng Vương, Thành phố Hồ Chí Minh, " +
            "đang phục vụ sự kiện ngày hai mươi hai tháng tám năm hai nghìn không trăm hai mươi sáu.\n" +

            "Hôm nay bệnh viện tổ chức Lễ đón nhận danh hiệu Anh hùng Lao động và Lễ khai trương " +
            "Đơn vị điều trị không xâm lấn bằng sóng siêu âm hội tụ, gọi tắt là Đơn vị HIFU. " +
            "Buổi chiều có Hội thảo khoa học về cùng chủ đề.\n" +

            "Người tới đây phần lớn là ĐẠI BIỂU: bác sĩ, hộ sinh, điều dưỡng, chuyên gia y tế và " +
            "khách mời của bệnh viện. Cũng có người bệnh tới tìm hiểu dịch vụ.\n" +

            "BẠN XƯNG 'tôi', GỌI NGƯỜI ĐỐI DIỆN LÀ 'Quý vị'. Lễ độ, trang trọng, nói ngắn gọn. " +
            "Hôm nay là ngày trọng đại của bệnh viện nên giọng điệu cần trang trọng, " +
            "không suồng sã, không đùa cợt.\n" +

            "BẠN KHÔNG PHẢI BÁC SĨ. Bạn được phép đọc lại những thông tin chuyên môn mà bệnh viện " +
            "đã soạn sẵn cho bạn, nhưng TUYỆT ĐỐI KHÔNG tư vấn cho trường hợp riêng của người hỏi, " +
            "không chẩn đoán, không khuyên nên hay không nên điều trị, không nhận xét kết quả " +
            "xét nghiệm. Gặp câu như vậy thì mời Quý vị tới quầy chăm sóc khách hàng đăng ký khám.\n" +

            "PHẠM VI ĐI LẠI của bạn: chỉ trong khu vực đã quét bản đồ. Bạn KHÔNG tự đi thang máy " +
            "và KHÔNG lên xuống tầng. Tuyệt đối đừng hứa dẫn Quý vị lên lầu.\n" +

            "Bạn KHÔNG biết vị trí nhà vệ sinh, bãi giữ xe, căn tin, và KHÔNG biết mật khẩu wifi — " +
            "bệnh viện chưa cung cấp. Gặp câu đó thì nói thẳng là chưa có thông tin và mời Quý vị " +
            "hỏi đội lễ tân tại bàn tiếp đón. Đừng đoán."

        /**
         * Luật gửi kèm mỗi lần gọi mô hình.
         *
         * ⚠ Luật số 3 — dòng DAP_ID — là thứ để app KIỂM BẰNG MÃ, không phải cho đẹp.
         *   Mô hình trả id không nằm trong danh sách ứng viên, hoặc quên hẳn dòng này, thì
         *   app vứt cả câu trả lời và đọc câu từ chối của mình. Xem TraLoi.docCauTraLoi().
         *   Sai thì sai theo hướng im lặng.
         *
         * ⚠ Luật số 2 — cấm tự nói nội dung. Đây là phần KHÔNG được sai: nội dung y khoa
         *   về HIFU do bệnh viện soạn và duyệt từng chữ. App đọc nguyên văn phần đó, mô
         *   hình chỉ được soạn MỘT câu dẫn ngắn phía trước.
         */
        val LUAT_TRA_LOI =
            "LUẬT BẮT BUỘC:\n" +
            "1. Chỉ được chọn trong DANH SÁCH ỨNG VIÊN gửi kèm bên dưới. Tuyệt đối không trả lời " +
            "bằng kiến thức của riêng bạn, không nhớ từ chỗ khác, không suy ra.\n" +
            "2. KHÔNG tự nói nội dung câu trả lời. Ngay sau câu của bạn, máy sẽ tự đọc nguyên văn " +
            "nội dung mà Bệnh viện Hùng Vương đã duyệt. Bạn nói nữa là Quý vị nghe hai lần, mà " +
            "lệch một con số là sai hẳn thông tin y khoa.\n" +
            "3. DÒNG CUỐI CÙNG của câu trả lời BẮT BUỘC viết đúng dạng:\n" +
            "   DAP_ID: X\n" +
            "   X là id của mục bạn chọn trong danh sách ứng viên;\n" +
            "   hoặc KHONG_CO nếu Quý vị hỏi về sự kiện hay bệnh viện mà không ứng viên nào khớp;\n" +
            "   hoặc TAM_SU nếu Quý vị chỉ chào hỏi, cảm ơn hay nói chuyện ngoài lề.\n" +
            "4. Câu của bạn chỉ là CÂU DẪN ngắn, tối đa hai câu. " +
            "Ví dụ: \"Dạ, tôi xin thưa với Quý vị.\" hoặc \"Dạ vâng ạ.\"\n" +
            "Không hứa hẹn thay bác sĩ, không bàn chuyện bệnh tình của người hỏi, " +
            "không bàn chuyện chính trị."
    }

    override fun onCreate() {
        super.onCreate()
        boiCanh = applicationContext

        // Tầng thấp: dẫn đường + đọc thành tiếng. Đây mới là phần app sống bằng.
        RobotHelper.ketNoi(this)

        // Tầng cao: nghe và gọi mô hình
        agent = object : AppAgent(this) {

            override fun onCreate() {

                /*
                 * ═══ BỐN CÔNG TẮC CỦA HÃNG, CẢ BỐN ĐỀU MẶC ĐỊNH SAI VỚI APP NÀY ═══
                 *
                 * Đặt ở đây là an toàn: `create$sdk_release` gán `api` rồi mới gọi `onCreate`,
                 * nên giá trị đặt tại đây nằm luôn trong gói `AppInfo` gửi sang AgentService.
                 *
                 * 1. isEnableVoiceBar — MẶC ĐỊNH BẬT. Đây là hộp trắng góc phải dưới màn hình
                 *    robot: phụ đề câu đang đọc kèm nút "Chạm để Ngắt". Nó ĐÈ LÊN giao diện
                 *    app. App đã có khung chat và video biểu cảm riêng nên thanh này chỉ vướng.
                 *
                 * 2. isDisablePlan — bật để TẮT bộ hoạch định của AgentOS. Bắt buộc phải tắt
                 *    khi app tự gọi `AgentCore.llm()`, không thì hai bên cùng trả lời một câu
                 *    hỏi và robot nói chồng lên chính nó.
                 *    ⚠ Đổi lại: từ đây AgentOS KHÔNG còn gọi Action nào nữa. Đường chính là
                 *      onASRResult → TraLoi.hoi(). App này vì thế KHÔNG đăng ký Action riêng.
                 *    ⚠ Chốt kiểm sau khi cài: nói vào robot vẫn phải thấy `Người bệnh nói: …`
                 *      trong logcat. Mất dòng đó nghĩa là tắt hoạch định giết luôn ASR —
                 *      đã đo ở app Mông Dương là KHÔNG giết, nhưng vẫn phải kiểm lại trên máy này.
                 *
                 * 3. isMicrophoneMuted — mặc định KHÔNG tắt tiếng, tức robot nghe cả ngày ngay
                 *    từ lúc mở app. Ở sảnh bệnh viện đó là nghe lỏm chuyện bệnh tình của người
                 *    ngồi chờ. Đóng lại từ đầu; chỉ mở ở màn Trò chuyện.
                 *
                 * 4. isEnableWakeFree — mặc định BẬT, robot tự bắt lời người đi ngang. Xem
                 *    chú thích dài ở datMicro().
                 */
                isEnableVoiceBar = false
                isDisablePlan = true
                isMicrophoneMuted = true
                isEnableWakeFree = false
                Log.d(TAG, "Công tắc hãng: voiceBar=$isEnableVoiceBar · disablePlan=$isDisablePlan · " +
                           "micTat=$isMicrophoneMuted · wakeFree=$isEnableWakeFree")

                /* Persona vẫn đặt dù đã tắt hoạch định: nó là đường lui nếu phải bật
                   disablePlan=false lại, và không tốn gì. */
                setPersona(PERSONA)
                setObjective(
                    "Việc của bạn là đón tiếp đại biểu, trả lời câu hỏi về sự kiện hôm nay, về " +
                    "Bệnh viện Hùng Vương và về kỹ thuật điều trị HIFU, rồi dẫn Quý vị tới đúng " +
                    "nơi trong khu vực sự kiện.\n" + LUAT_TRA_LOI
                )

                // Hai Action nói chuyện có sẵn của hệ thống. App KHÔNG đăng ký Action riêng:
                // đã tắt hoạch định thì AgentOS không gọi Action nào nữa, đăng ký cũng vô ích.
                registerAction(Actions.SAY)
                registerAction(Actions.KNOWLEDGE_QA)

                /*
                 * ĐÂY LÀ CÁI MIC.
                 *
                 * Đừng quay lại webkitSpeechRecognition của trình duyệt: trên WebView robot
                 * hàm đó TỒN TẠI nhưng gọi start() là ném ngay error=not-allowed (Android
                 * WebView không có dịch vụ nhận dạng giọng nói, chỉ Chrome thật mới có).
                 *
                 * ⚠ Bản 0.2.2 chỉ có MỘT hàm `onTranscribe`, phân biệt hai chiều bằng cờ
                 *   `isUserSpeaking`. Bản 0.4.7 tách hẳn làm hai hàm — trình biên dịch bắt
                 *   được ngay nếu viết nhầm.
                 *
                 * Trả false để hệ thống XỬ LÝ TIẾP như bình thường — trả true là nuốt mất
                 * câu nói.
                 *
                 * ⚠ Callback này chạy trên LUỒNG PHỤ. Đụng tới WebView phải post về luồng
                 *   chính — Cau.guiLoiNoi đã lo việc đó.
                 */
                setOnTranscribeListener(object : OnTranscribeListener {

                    override fun onASRResult(t: Transcription): Boolean {
                        val chu = t.text
                        if (chu.isNullOrBlank()) return false

                        /* CỔNG ĐÓNG = VỨT. Không đẩy vào TraLoi, không hiện lên màn hình,
                           không đánh dấu AI sẵn sàng. Đây là chốt chặn cuối cùng cho yêu
                           cầu "AI chỉ dùng trong chức năng Giao tiếp AI" — xem chú thích
                           dài ở congAIMo. */
                        if (!congAIMo) {
                            if (t.final) Log.d(TAG, "Cổng AI đóng — bỏ qua câu nghe được")
                            return false
                        }

                        // Nghe được chữ nghĩa là đường dây thật sự thông.
                        if (!agentSanSang) { agentSanSang = true; Cau.baoAISanSang(true) }

                        Cau.guiLoiNoi("nguoi", chu, t.final)

                        if (t.final) {
                            Log.d(TAG, "Người bệnh nói: $chu")
                            tuNoi = ""          // lượt mới, quên câu app tự đọc lần trước
                            /* ĐƯỜNG CHÍNH của cả cuộc hội thoại nằm ở đây. TraLoi tự lo:
                               cấp cứu → hỏi bệnh → chưa có dữ liệu → tra kho → chấm tin cậy
                               → hỏi mô hình → kiểm câu trả lời → mới cho robot đọc.
                               Nó tự đẩy sang luồng phụ nên callback này không bị chặn. */
                            TraLoi.hoi(chu)
                        }
                        return false
                    }

                    override fun onTTSResult(t: Transcription): Boolean {
                        val chu = t.text
                        if (chu.isNullOrBlank()) return false
                        if (!congAIMo) return false      // cổng đóng thì không hiện gì lên màn hình
                        /* Câu do chính app soạn thì đã hiện trên màn hình rồi — xem tuNoi.
                           ⚠ ĐỪNG xoá tuNoi ở đây khi t.final: robot đọc xong TỪNG CÂU là bắn
                           một gói final, nên xoá ngay câu đầu thì mấy câu sau lọt lưới và màn
                           hình lại hiện lặp. tuNoi chỉ xoá khi người bệnh mở miệng lần sau. */
                        if (tuNoi.isNotEmpty() && tuNoi.contains(chu.trim())) return false
                        Cau.guiLoiNoi("robot", chu, t.final)
                        return false
                    }
                })
            }

            /** App này không mở Action nào cho app khác gọi vào. */
            override fun onExecuteAction(action: Action, params: Bundle?): Boolean = false
        }

        /* ⚠ KHÔNG thăm dò mô hình ở đây nữa.
           Trước đây app gọi thamDoAI() ngay lúc khởi động để biết có nên hiện nút micro
           không. Nhưng đó là gọi lên đám mây của hãng trong khi khách còn chưa bấm nút
           nào — trái với yêu cầu "AI chỉ chạy khi vào chức năng Giao tiếp AI".
           Giờ việc thăm dò dời sang lần đầu MỞ CỔNG (xem moCongAI). Hệ quả: nút micro
           chỉ hiện sau khi khách vào màn Trò chuyện chừng một giây — mà cũng chỉ ở đó
           mới cần tới nó. */
        tatMicro()
    }
}
