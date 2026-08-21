package vn.roboworld.hungvuong

import android.os.Handler
import android.os.HandlerThread
import android.os.Looper
import android.util.Log
import com.ainirobot.coreservice.client.RobotApi
import com.ainirobot.coreservice.client.actionbean.Pose
import com.ainirobot.coreservice.client.listener.ActionListener

/**
 * ĐI VÒNG QUANH SỰ KIỆN — robot đi liên tục qua các điểm, KHÔNG dừng ở điểm nào.
 *
 * Lớp này chỉ lo MỘT việc: giữ cho robot còn đang đi. Nó không biết gì về câu chào,
 * về màn hình, về khách — những thứ đó nằm ở lớp web (xem phần "ĐI VÒNG" trong
 * khung-app.html). Chia như vậy vì hai bên đổi vì lý do khác hẳn nhau: nội dung chào
 * đổi theo yêu cầu bệnh viện, còn cách lái robot đổi theo cách hãng cho phép.
 *
 * ── HAI LỐI ĐI, TỰ CHUYỂN ─────────────────────────────────────────────────────
 *
 * LỐI 1 — `startCruise` của hãng (ưu tiên).
 *   Đây là API đi tuần có sẵn trong robotservice.jar. Đọc bytecode thấy nó gói tham số
 *   vào `CruiseParams` với các trường: route (danh sách điểm) · startPoint · dockingPoints
 *   · linearSpeed · angularSpeed · multipleWaitTime.
 *
 *   ⚠ `dockingPoints` LÀ DANH SÁCH CHỈ SỐ NHỮNG ĐIỂM ROBOT PHẢI DỪNG LẠI. Để RỖNG
 *     nghĩa là không dừng ở đâu cả — đúng thứ anh Trường yêu cầu. Đừng nhét chỉ số vào
 *     đó "cho đủ", nhét vào là robot đứng lại ở từng điểm.
 *
 *   ⚠ Mặc định của hãng là 0,7 m/s và 1,2 rad/s. Trong một sảnh đông đại biểu đang đứng
 *     nói chuyện thì đó là nhanh. Tốc độ lấy từ app-data.json, đang đặt 0,5 và 0,8.
 *
 * LỐI 2 — nối từng lệnh `startNavigation` (dự phòng).
 *   Tới điểm này thì bắn ngay lệnh đi điểm kế, không nói năng gì. Robot vẫn khựng lại
 *   một nhịp ngắn ở mỗi điểm vì SDK không có khái niệm "điểm đi ngang qua" — nhưng để
 *   sai số toạ độ rộng một mét thì nó coi như đã tới từ xa, nhịp khựng gần như không thấy.
 *
 * ── VÌ SAO PHẢI CÓ LỐI 2 ──────────────────────────────────────────────────────
 * `startCruise` CHƯA TỪNG được chạy thử trên máy thật. Kinh nghiệm với cả OrionStar lẫn
 * PUDU đã đủ nhiều lần: lệnh nhận, trả về mã dương, rồi KHÔNG LÀM GÌ và cũng không báo
 * lỗi (xem ghi chú "hãng khoá bộ dò chân" và "AgentCore im lặng" trong CLAUDE.md).
 * Nên ở đây không tin lời API nói, mà ĐO: cứ hai giây hỏi `getCurrentPose()` một lần,
 * hai mươi giây mà robot xê dịch chưa nổi ba mươi phân thì coi như lối 1 chết, tự chuyển
 * sang lối 2. Người vận hành không phải biết gì về chuyện này.
 */
object DiVong {

    private const val TAG = "BVDiVong"

    /** Robot phải nhích được bao nhiêu mét thì mới tính là "có đi". */
    private const val NGUONG_DI_MET = 0.3

    /** Chờ lâu nhất bao nhiêu mili giây rồi mới kết luận lối 1 chết. */
    private const val HAN_DO_MS = 20_000L

    /** Nhịp hỏi vị trí robot. */
    private const val NHIP_SOI_MS = 2_000L

    /** Gặp lỗi thì nghỉ bao lâu rồi thử điểm kế. */
    private const val NGHI_SAU_LOI_MS = 12_000L

    /** Lỗi liên tiếp bao nhiêu lần thì nghỉ dài, khỏi quần API. */
    private const val LOI_LIEN_TIEP_TOI_DA = 5
    private const val NGHI_DAI_MS = 60_000L

    private val main = Handler(Looper.getMainLooper())

    /** Luồng riêng để hỏi vị trí robot — `getCurrentPose` là lệnh liên tiến trình, gọi
     *  trên luồng giao diện là có ngày giao diện khựng. */
    private val luongSoi = HandlerThread("divong-soi").apply { start() }
    private val soi = Handler(luongSoi.looper)

    private var reqId = 7000
    private fun nextReqId(): Int = ++reqId

    // ───────────────────────── Trạng thái ─────────────────────────

    @Volatile private var dangChay = false
    @Volatile private var loi1DangChay = false        // đang đi bằng startCruise
    @Volatile private var luot = 0                    // để bỏ qua callback của lượt cũ
    @Volatile private var chiSo = 0                   // điểm đang hướng tới (lối 2)
    @Volatile private var loiLienTiep = 0
    @Volatile private var moTa = "tắt"

    private var diem: List<String> = emptyList()
    private var tocDoThang = 0.5
    private var tocDoXoay = 0.8
    private var saiSo = 1.0

    /** Báo ngược lên lớp web: (trạng thái, mô tả). Xem Cau.baoDiVong. */
    var khiDoi: ((String, String) -> Unit)? = null

    fun dangDi(): Boolean = dangChay
    fun moTaHienTai(): String = moTa

    // ───────────────────────── Bật / tắt ─────────────────────────

    /**
     * Bắt đầu đi vòng.
     *
     * Gọi lại khi đang chạy thì KHÔNG khởi động lại — lớp web có một đồng hồ canh gác
     * gọi hàm này đều đặn để tự dựng lại vòng đi sau khi robot bị treo hay mất định vị.
     * Nếu mỗi lần gọi đều dựng lại từ đầu thì robot cứ năm giây lại quay về điểm một.
     */
    fun batDau(
        danhSachDiem: List<String>,
        tocThang: Double,
        tocXoay: Double,
        saiSoMet: Double
    ) {
        if (dangChay) { Log.d(TAG, "Đang đi rồi, bỏ qua lệnh bắt đầu"); return }
        if (danhSachDiem.size < 2) { Log.w(TAG, "Cần ít nhất hai điểm"); return }

        val vuong = RobotHelper.lyDoChuaSanSang()
        if (vuong != null) { Log.w(TAG, "Chưa đi được: $vuong"); bao("cho", vuong); return }

        diem = danhSachDiem
        tocDoThang = tocThang
        tocDoXoay = tocXoay
        saiSo = saiSoMet
        dangChay = true
        loiLienTiep = 0
        chiSo = 0
        luot++

        Log.d(TAG, "Bắt đầu đi vòng qua ${diem.size} điểm: ${diem.joinToString(" → ")}")
        thuLoi1()
    }

    /** Dừng hẳn. Gọi khi khách chạm màn hình, khi dẫn đường, khi app đóng. */
    fun dung(viSao: String) {
        if (!dangChay && !loi1DangChay) return
        Log.d(TAG, "Dừng đi vòng — $viSao")
        dangChay = false
        luot++                                  // vô hiệu mọi callback đang bay về
        soi.removeCallbacksAndMessages(null)
        main.removeCallbacksAndMessages(null)
        if (loi1DangChay) {
            loi1DangChay = false
            runCatching { RobotApi.getInstance().stopCruise(nextReqId()) }
        }
        runCatching { RobotApi.getInstance().stopNavigation(nextReqId()) }
        bao("dung", viSao)
    }

    // ───────────────────────── Lối 1: startCruise ─────────────────────────

    private fun thuLoi1() {
        val cacDiem = timPose(diem)
        if (cacDiem.size < 2) {
            Log.w(TAG, "Chỉ tìm thấy ${cacDiem.size}/${diem.size} điểm trên bản đồ — " +
                    "chuyển sang lối nối điểm để nó tự báo điểm nào thiếu")
            chayLoi2()
            return
        }

        val luotNay = luot
        // dockingPoints RỖNG = không dừng ở điểm nào. Đây là cả yêu cầu của bài toán.
        val khongDungODau = emptyList<Int>()
        val ma = runCatching {
            RobotApi.getInstance().startCruise(
                nextReqId(), cacDiem, 0, khongDungODau,
                tocDoThang, tocDoXoay, 0L,
                object : ActionListener() {
                    override fun onResult(status: Int, response: String?) {
                        if (luotNay != luot) return
                        Log.d(TAG, "startCruise onResult status=$status response=$response")
                        // Cruise kết thúc (đi hết vòng, hoặc bị hệ thống cắt) → dựng lại.
                        if (dangChay) main.postDelayed({ if (luotNay == luot && dangChay) thuLoi1() }, 1500)
                    }

                    override fun onError(errorCode: Int, errorString: String?) {
                        if (luotNay != luot) return
                        Log.w(TAG, "startCruise onError code=$errorCode msg=$errorString " +
                                "→ chuyển sang lối nối điểm")
                        loi1DangChay = false
                        if (dangChay) chayLoi2()
                    }

                    override fun onStatusUpdate(status: Int, data: String?) {
                        Log.d(TAG, "cruise status=$status data=$data")
                    }
                }
            )
        }.getOrElse { e ->
            Log.w(TAG, "startCruise ném ngoại lệ: ${e.javaClass.simpleName} ${e.message}")
            -1
        }

        Log.d(TAG, "startCruise trả mã = $ma")
        if (ma < 0) { chayLoi2(); return }

        loi1DangChay = true
        bao("di", "đi vòng bằng lệnh của hãng")
        doXemCoDiThat(luotNay)
    }

    /**
     * ĐO xem robot có thật sự nhúc nhích không.
     *
     * Không đo thì không biết: `startCruise` trả mã dương rồi im lặng là kiểu hỏng đã gặp
     * nhiều lần ở cả hai hãng. Hai mươi giây mà robot chưa nhích nổi ba mươi phân thì
     * coi như lệnh không tới được bánh xe, tự chuyển lối.
     */
    private fun doXemCoDiThat(luotNay: Int) {
        val moc = layViTri()
        if (moc == null) {
            // Không đọc được vị trí thì thôi không kết luận gì — cứ để lối 1 chạy.
            Log.w(TAG, "Không đọc được vị trí robot, bỏ qua phép đo")
            return
        }
        val batDauLuc = System.currentTimeMillis()

        fun nhip() {
            if (luotNay != luot || !dangChay || !loi1DangChay) return
            val nay = layViTri()
            if (nay != null) {
                val dx = (nay.x - moc.x).toDouble()
                val dy = (nay.y - moc.y).toDouble()
                val di = Math.sqrt(dx * dx + dy * dy)
                if (di >= NGUONG_DI_MET) {
                    Log.d(TAG, "Đo được robot đã đi %.2f m — lệnh của hãng chạy thật".format(di))
                    return                       // xong, không đo nữa
                }
            }
            if (System.currentTimeMillis() - batDauLuc >= HAN_DO_MS) {
                Log.w(TAG, "Hai mươi giây robot không nhúc nhích — startCruise nhận lệnh " +
                        "mà không lái bánh xe. Chuyển sang lối nối điểm.")
                loi1DangChay = false
                runCatching { RobotApi.getInstance().stopCruise(nextReqId()) }
                main.post { if (luotNay == luot && dangChay) chayLoi2() }
                return
            }
            soi.postDelayed(::nhip, NHIP_SOI_MS)
        }
        soi.postDelayed(::nhip, NHIP_SOI_MS)
    }

    private fun layViTri(): Pose? =
        runCatching { RobotApi.getInstance().currentPose }.getOrNull()

    /** Lọc ra Pose của những điểm mình cần, giữ ĐÚNG THỨ TỰ lộ trình đã khai. */
    private fun timPose(ten: List<String>): List<Pose> {
        val tatCa = runCatching { RobotApi.getInstance().placeList }.getOrNull().orEmpty()
        if (tatCa.isEmpty()) { Log.w(TAG, "Bản đồ không trả về điểm nào"); return emptyList() }
        val ra = ArrayList<Pose>()
        ten.forEach { t ->
            val p = tatCa.firstOrNull { it.name == t }
            if (p == null) Log.w(TAG, "Bản đồ KHÔNG có điểm '$t'") else ra.add(p)
        }
        return ra
    }

    /** Điểm nào chưa có trên bản đồ — dùng cho màn tự kiểm lúc lắp đặt. */
    fun diemConThieu(ten: List<String>): List<String> {
        val tatCa = runCatching { RobotApi.getInstance().placeList }.getOrNull().orEmpty()
        val co = tatCa.mapNotNull { it.name }.toSet()
        return ten.filter { it !in co }
    }

    // ───────────────────────── Lối 2: nối từng lệnh dẫn đường ─────────────────────────

    private fun chayLoi2() {
        if (!dangChay) return
        loi1DangChay = false
        diTiep()
    }

    private fun diTiep() {
        if (!dangChay) return
        val luotNay = luot
        val ten = diem[chiSo % diem.size]
        chiSo = (chiSo + 1) % diem.size
        bao("di", ten)
        Log.d(TAG, "Đi tới '$ten' (nối điểm)")

        RobotHelper.dieuHuongToi(
            ten,
            saiSoToaDo = saiSo,
            khiToiNoi = {
                if (luotNay != luot || !dangChay) return@dieuHuongToi
                loiLienTiep = 0
                /* KHÔNG nghỉ, KHÔNG nói gì — bắn ngay lệnh đi điểm kế. Đây chính là chỗ
                   quyết định robot có "đi liên tục" hay không. Chèn một cái postDelayed
                   ở đây là mỗi điểm robot đứng lại đúng bấy nhiêu mili giây. */
                diTiep()
            },
            khiLoi = { vs ->
                if (luotNay != luot || !dangChay) return@dieuHuongToi
                loiLienTiep++
                Log.w(TAG, "Không tới được '$ten' (lần thứ $loiLienTiep): $vs")
                RobotHelper.dungDieuHuong()
                val nghi = if (loiLienTiep >= LOI_LIEN_TIEP_TOI_DA) {
                    loiLienTiep = 0
                    bao("kho-khan", "nhiều điểm không tới được, tôi nghỉ một phút rồi thử lại")
                    NGHI_DAI_MS
                } else {
                    bao("bo-qua", ten)
                    NGHI_SAU_LOI_MS
                }
                /* Bỏ qua điểm này, thử điểm KẾ TIẾP. Thử lại đúng điểm vừa hỏng là robot
                   kẹt vĩnh viễn ở một cái ghế ai đó vừa kê chắn lối. */
                main.postDelayed({ if (luotNay == luot && dangChay) diTiep() }, nghi)
            },
            khiCapNhat = { }        // robot đang đi một mình, không báo gì lên màn hình
        )
    }

    // ───────────────────────── Báo lên lớp web ─────────────────────────

    private fun bao(trangThai: String, chiTiet: String) {
        moTa = when (trangThai) {
            "di"        -> "đang đi tới $chiTiet"
            "cho"       -> "chờ: $chiTiet"
            "bo-qua"    -> "bỏ qua $chiTiet"
            "kho-khan"  -> chiTiet
            "dung"      -> "tắt"
            else        -> trangThai
        }
        main.post { khiDoi?.invoke(trangThai, chiTiet) }
    }
}
