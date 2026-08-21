<#
    Cài app lên robot Nova — dành cho người KHÔNG phải lập trình viên.

    Cách dùng: nháy phải vào file này → "Run with PowerShell"
    Hoặc mở PowerShell rồi gõ:
        .\cai-len-robot.ps1                      # cáp USB
        .\cai-len-robot.ps1 -Ip 192.168.1.50     # qua Wi-Fi

    Script tự tìm adb, tự tìm file APK, tự kiểm tra sau khi cài.
    Mọi thông báo đều bằng tiếng Việt.
#>
param(
    [string]$Ip,
    [switch]$GoCai      # gỡ app ra khỏi robot (dùng khi cần cài lại từ đầu)
)

$ErrorActionPreference = "Stop"
$Goc = Split-Path -Parent $PSScriptRoot
$Goi = "vn.roboworld.hungvuong"

function Buoc($n, $chu) { Write-Host "`n[$n] $chu" -ForegroundColor Cyan }
function Xong($chu)     { Write-Host "  OK   $chu" -ForegroundColor Green }
function Loi($chu)      { Write-Host "  LOI  $chu" -ForegroundColor Red }
function Nhac($chu)     { Write-Host "       $chu" -ForegroundColor Yellow }

# ── 1. Tìm adb ────────────────────────────────────────────────
# ⚠ PHẢI dùng adb 1.0.41 của Android SDK. Bản C:\Windows\adb.exe là adb 1.0.39 của
#   PUDU — lệch phiên bản với adb server nên hai bên giết tiến trình của nhau, rớt
#   kết nối liên tục và không ai hiểu vì sao.
Buoc 1 "Tim adb"
$AdbExe = "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe"
if (-not (Test-Path $AdbExe)) {
    Loi "Chua co adb cua Android SDK."
    Nhac "Cach cai nhanh nhat: tai 'SDK Platform-Tools for Windows' o trang"
    Nhac "  https://developer.android.com/tools/releases/platform-tools"
    Nhac "Giai nen ra: $env:LOCALAPPDATA\Android\Sdk\platform-tools\"
    Nhac ""
    Nhac "DUNG dung C:\Windows\adb.exe — do la ban 1.0.39 cu cua PUDU, dung se rot lien tuc."
    exit 1
}
function Adb { & $AdbExe @args }
$ver = (Adb version | Select-Object -First 1)
Xong "$AdbExe  ($ver)"

# ── 2. Kết nối robot ──────────────────────────────────────────
Buoc 2 "Ket noi robot"
if ($Ip) {
    Write-Host "  Ket noi qua Wi-Fi toi $Ip ..."
    Adb connect "${Ip}:5555" | Write-Host
} else {
    Write-Host "  Dung cap USB — cam vao cong o PHAN DAU robot (khong phai than may)."
}

$ds = (Adb devices) -split "`n" | Where-Object { $_ -match "\sdevice$" }
if (-not $ds) {
    Loi "Khong thay robot nao."
    Nhac "Kiem lai ba thu:"
    Nhac " 1. Robot da bat 'Go loi lau dai' VA DA KHOI DONG LAI chua?"
    Nhac "    (chi bat 'Bat go loi' thoi thi mat sau khi tat may)"
    Nhac " 2. Cap USB cam vao dau robot, va la cap truyen du lieu (khong phai cap chi sac)"
    Nhac " 3. Neu dung Wi-Fi: may tinh va robot phai CUNG mot mang"
    exit 1
}
Xong "Da ket noi: $($ds -join ', ')"

$sn  = (Adb shell "getprop ro.serialno").Trim()
$rom = (Adb shell "getprop ro.build.display.id").Trim()
Write-Host "  So may (SN) : $sn"
Write-Host "  Ban ROM     : $rom"

# ── Gỡ app (nếu được yêu cầu) ─────────────────────────────────
if ($GoCai) {
    Buoc "-" "Go app khoi robot"
    Adb uninstall $Goi | Write-Host
    Xong "Da go $Goi"
    exit 0
}

# ── 3. Tìm file APK ───────────────────────────────────────────
Buoc 3 "Tim file APK"
$apk = Get-ChildItem (Join-Path $Goc "apk") -Filter "*.apk" -EA SilentlyContinue |
       Sort-Object Name -Descending | Select-Object -First 1
if (-not $apk) {
    # chưa có trong apk/ thì lấy bản vừa build
    $thu = Join-Path $Goc "android\app\build\outputs\apk\debug\app-debug.apk"
    if (Test-Path $thu) { $apk = Get-Item $thu }
}
if (-not $apk) {
    Loi "Khong thay file APK nao."
    Nhac "File APK phai nam trong thu muc:  $Goc\apk\"
    Nhac "Tai ve tu: https://github.com/LouisTruong0220/BV-PH"
    exit 1
}
$mb = [math]::Round($apk.Length / 1MB, 2)
Xong "$($apk.Name)  ($mb MB)"

# ── 4. Cài ────────────────────────────────────────────────────
Buoc 4 "Cai app len robot"
Write-Host "  Dang cai, mat khoang 30 giay — dung tat cua so nay."
$kq = Adb install -r $apk.FullName 2>&1
$kq | Write-Host
if ($kq -match "Success") { Xong "Cai xong" } else { Loi "Cai that bai — doc thong bao o tren"; exit 1 }

# ── 5. Kiểm tra lại ───────────────────────────────────────────
Buoc 5 "Kiem tra lai"
$daCo = (Adb shell "pm list packages $Goi").Trim()
if ($daCo -match $Goi) { Xong "Robot da co app: $Goi" }
else { Loi "Khong thay app tren robot — cai chua thanh cong" ; exit 1 }

# ── 6. Nhắc việc cuối ─────────────────────────────────────────
Write-Host "`n────────────────────────────────────────────────────" -ForegroundColor DarkGray
Write-Host " VIEC CUOI — lam TREN MAN HINH ROBOT:" -ForegroundColor Yellow
Write-Host ""
Write-Host " 1. Mo app bang cach bam bieu tuong tren man hinh chinh cua robot"
Write-Host "    (RobotOS Home). TEN APP: 'Robot le tan Benh vien Hung Vuong'"
Write-Host ""
Write-Host "    KHONG mo bang lenh 'am start' hay bang nut Run cua Android Studio."
Write-Host "    Mo kieu do thi robot khong uy quyen cho app: bam nut dan duong se"
Write-Host "    KHONG CO PHAN UNG GI, ma cung khong bao loi."
Write-Host ""
Write-Host " 2. Quet ban do va dat 10 diem — xem file huong-dan-cai-dat.html"
Write-Host ""
Write-Host " 3. Tu kiem: o man hai lua chon, BAM GIU bieu tuong benh vien goc tren"
Write-Host "    trai 1,2 giay -> hien man kiem tra ban do."
Write-Host "────────────────────────────────────────────────────`n" -ForegroundColor DarkGray
