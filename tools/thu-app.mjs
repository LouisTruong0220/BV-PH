/**
 * Chạy thử TRỌN app trên bản demo có giả lập robot, tự động.
 *
 *   node tools/thu-app.mjs
 *
 * Vì sao cần: sự kiện diễn ra một buổi duy nhất, không có lần thứ hai để sửa. Mà những
 * màn quan trọng nhất chỉ hiện ra KHI ĐANG DẪN ĐƯỜNG — bấm tay thì mỗi lần đổi một dòng
 * CSS lại phải ngồi bấm lại tám bước, và kiểu gì cũng có lần bỏ qua.
 *
 * Nó kiểm bằng TRẠNG THÁI THẬT của app (màn nào đang hiện, robot đọc câu gì, lệnh nào
 * đã gửi xuống Kotlin), không phải chụp ảnh rồi bảo là xong.
 *
 * Ảnh chụp từng bước để ở demo/anh-soi/.
 */
import { existsSync, mkdirSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { pathToFileURL, fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const APP = resolve(HERE, '..');
const PW = join(APP, '..', '..', 'tools', 'html-video', 'packages',
                'adapter-hyperframes', 'node_modules', 'playwright', 'index.mjs');
if (!existsSync(PW)) { console.error('Khong thay playwright tai:\n  ' + PW); process.exit(1); }
const { chromium } = await import(pathToFileURL(PW).href);

const RA = join(APP, 'demo', 'anh-soi');
mkdirSync(RA, { recursive: true });

let so = 0, hong = 0;
const ok = (t) => { so++; console.log('  ✔ ' + t); };
const loi = (t) => { so++; hong++; console.log('  ✘ ' + t); };
const kiem = (dk, t) => dk ? ok(t) : loi(t);

const trinh = await chromium.launch();
const trang = await trinh.newPage({ viewport: { width: 1920, height: 1080 } });
trang.on('pageerror', e => { hong++; console.log('  ✘ LOI JS: ' + e.message); });
trang.on('console', m => { if (m.type() === 'error') console.log('  ! console.error: ' + m.text()); });

await trang.goto(pathToFileURL(join(APP, 'demo', 'thu-nghiem.html')).href);
await trang.waitForTimeout(700);

/* ── tiện ích ── */
/* manDang là biến trong phạm vi <script>, KHÔNG nằm trên window — đọc từ DOM.
   (Đây từng làm cả bộ thử báo hỏng oan: app chạy đúng, phép đo sai.) */
const manDang  = () => trang.evaluate(() => {
  const m = document.querySelector('.man-hinh.hien');
  return m ? m.id : '';
});
const daDoc    = () => trang.evaluate(() => (window.GIA_LAP && window.GIA_LAP.cauDaDoc) || []);
const hienNhat = () => trang.evaluate(() =>
  [...document.querySelectorAll('.man-hinh')].filter(m => m.classList.contains('hien')).map(m => m.id));
const anh = async (ten) => { await trang.screenshot({ path: join(RA, ten + '.png') }); };

/* Giả lập ghi lại mọi câu robot đọc — cắm móc vào CAU.doc. */
/* Robot nói ra bằng HAI đường, phải bắt cả hai:
     · app tự đọc (lời chào, lời giới thiệu khi tới nơi) → CAU.doc
     · tầng hội thoại trả lời (giả lập TraLoi.kt)        → window.nhanLoiNoi('robot', …)
   Chỉ móc một đường là nửa bộ thử báo hỏng oan. */
await trang.evaluate(() => {
  window.GIA_LAP = window.GIA_LAP || {};
  window.GIA_LAP.cauDaDoc = [];
  window.GIA_LAP.diemDaGoi = [];
  const goc = window.CAU.doc;
  window.CAU.doc = function (t) { window.GIA_LAP.cauDaDoc.push(t); return goc.apply(this, arguments); };
  const gocDan = window.CAU.danDuongToiDiem;
  window.CAU.danDuongToiDiem = function (t) { window.GIA_LAP.diemDaGoi.push(t); return gocDan.apply(this, arguments); };
  const gocNoi = window.nhanLoiNoi;
  window.nhanLoiNoi = function (ai, chu, xong) {
    if (ai === 'robot' && xong) window.GIA_LAP.cauDaDoc.push(chu);
    return gocNoi.apply(this, arguments);
  };
});

console.log('\n═══ 1. MÀN CHỜ ═══');
kiem(await manDang() === 'mh-cho', 'App mở lên là vào màn chờ');
const nguonBc = await trang.evaluate(() => {
  const v = document.querySelector('#bc-a');
  return v ? decodeURIComponent(v.src) : '';
});
kiem(nguonBc.includes('emoji_wink_2'), 'Màn chờ chiếu emoji_wink_2 (anh Trường chốt) — ' +
     nguonBc.split('/').pop());
await anh('01-man-cho');

console.log('\n═══ 2. HAI LỰA CHỌN ═══');
await trang.click('#mh-cho');
await trang.waitForTimeout(300);
kiem(await manDang() === 'mh-chon', 'Chạm màn chờ thì hiện màn chọn');
const nutLon = await trang.$$eval('.the-lon b', ns => ns.map(n => n.textContent.trim()));
kiem(nutLon.length === 2 && nutLon.includes('Dẫn đường') && nutLon.includes('Giao tiếp AI'),
     'Có ĐÚNG hai lựa chọn lớn: ' + nutLon.join(' · '));
const nutPhu = await trang.$$eval('.nut-phu-lon', ns => ns.length);
kiem(nutPhu === 2, 'Có hai nút bệnh viện yêu cầu thêm (mời khách · tư vấn HIFU)');
/* Nút bị co về chiều cao 0 là lỗi kinh điển trên Nova — không báo lỗi, chỉ biến mất. */
const beDep = await trang.$$eval('.the-lon, .nut-phu-lon', ns =>
  ns.filter(n => { const r = n.getBoundingClientRect(); return r.height < 40 || r.width < 40; }).length);
kiem(beDep === 0, 'Không nút nào bị co về kích thước 0');
await anh('02-hai-lua-chon');

console.log('\n═══ 3. DẪN ĐƯỜNG ═══');
await trang.click('.the-dan');
await trang.waitForTimeout(300);
kiem(await manDang() === 'mh-dich', 'Bấm "Dẫn đường" ra danh sách vị trí');
const soThe = await trang.$$eval('#dich-than .the', ns => ns.length);
kiem(soThe >= 7, 'Danh sách có ' + soThe + ' vị trí');
await anh('03-danh-sach-vi-tri');

await trang.click('#dich-than .the');
await trang.waitForTimeout(300);
kiem(await manDang() === 'mh-ct', 'Chạm một vị trí ra màn chi tiết');
const loiHien = await trang.$eval('#ct-loi', n => n.textContent.trim());
kiem(loiHien.length > 30, 'Màn chi tiết hiện sẵn lời robot sẽ nói khi tới nơi');
await anh('04-chi-tiet-diem');

const tenDich = await trang.$eval('#ct-ten', n => n.textContent.trim());
await trang.click('#ct-nut-dan');
await trang.waitForTimeout(400);
kiem(await manDang() === 'mh-dan', 'Bấm "Dẫn tôi tới đó" chuyển sang màn đang dẫn');
const diemGoi = await trang.evaluate(() => window.GIA_LAP.diemDaGoi);
kiem(diemGoi.length === 1 && /^[\x20-\x7E]+$/.test(diemGoi[0]),
     'Tên điểm gửi xuống robot KHÔNG dấu tiếng Việt: "' + diemGoi[0] + '"');
/* ⚠ Câu "Xin mời đi theo tôi" do TẦNG KOTLIN đọc (Cau.danDuongToiDiem), không phải
   lớp web. Nên phép kiểm đúng ở đây là: lớp web KHÔNG tự đọc thêm gì dọc đường.
   Robot im lặng lúc dẫn là chủ ý — sảnh sự kiện đã ồn, robot lải nhải là át hết. */
const docLucDan = await daDoc();
kiem(docLucDan.length === 0, 'Dọc đường lớp web KHÔNG tự đọc gì (robot im lặng khi dẫn)');
await anh('05-dang-dan');

/* Đợi robot đi hết quãng đường. Giả lập đặt 6 giây; chờ theo trạng thái thật chứ
   không đặt cứng một con số — đổi tốc độ giả lập là bộ thử hỏng oan ngay. */
await trang.waitForFunction(
  () => document.querySelector('.man-hinh.hien')?.id === 'mh-toi', null, { timeout: 15000 }
).catch(() => {});
kiem(await manDang() === 'mh-toi', 'Tới nơi thì chuyển sang màn giới thiệu');
const docToiNoi = await daDoc();
const cauCuoi = docToiNoi[docToiNoi.length - 1] || '';
const loiChuan = await trang.evaluate(() => window.DU_LIEU.dich.map(d => d.doc));
kiem(loiChuan.indexOf(cauCuoi) >= 0,
     'Tới nơi robot ĐỌC NGUYÊN VĂN lời giới thiệu bệnh viện soạn');
kiem(!/\d/.test(cauCuoi), 'Lời giới thiệu không còn chữ số (robot đọc chữ số sai nhịp)');
const tenToi = await trang.$eval('#toi-ten', n => n.textContent.trim());
kiem(tenToi === tenDich, 'Màn tới nơi hiện đúng tên điểm vừa dẫn: ' + tenToi);
await anh('06-toi-noi');

console.log('\n═══ 4. GIAO TIẾP AI ═══');
await trang.evaluate(() => window.veManCho());
await trang.waitForTimeout(300);
await trang.click('#mh-cho');
await trang.waitForTimeout(200);
await trang.click('.the-ai');
await trang.waitForTimeout(300);
kiem(await manDang() === 'mh-loai', 'Bấm "Giao tiếp AI" ra màn chọn loại khách');
const tenLoai = await trang.$$eval('.the-loai b', ns => ns.map(n => n.textContent.trim()));
kiem(tenLoai.length === 2 && tenLoai.includes('Đại biểu') && tenLoai.includes('Khách VIP'),
     'Có hai lựa chọn: ' + tenLoai.join(' · '));
await anh('07-chon-loai-khach');

/* ĐẠI BIỂU — phải phát câu chào số 1 hoặc số 2 của bệnh viện */
await trang.evaluate(() => { window.GIA_LAP.cauDaDoc.length = 0; });
await trang.click('.the-loai');
await trang.waitForTimeout(500);
kiem(await manDang() === 'mh-chat', 'Chọn Đại biểu thì vào màn trò chuyện');
const chaoDB = (await daDoc())[0] || '';
const cauDB = await trang.evaluate(() => window.DU_LIEU.chao['dai-bieu'].cau);
kiem(cauDB.indexOf(chaoDB) >= 0,
     'Phát ĐÚNG lời chào đại biểu số ' + (cauDB.indexOf(chaoDB) + 1) + ' của bệnh viện');
await anh('08-chat-dai-bieu');

/* Lời chào phải LUÂN PHIÊN giữa hai câu, không lặp mãi một câu */
await trang.evaluate(() => { window.veManCho(); });
await trang.waitForTimeout(200);
await trang.click('#mh-cho'); await trang.waitForTimeout(150);
await trang.click('.the-ai'); await trang.waitForTimeout(200);
await trang.evaluate(() => { window.GIA_LAP.cauDaDoc.length = 0; });
await trang.click('.the-loai');
await trang.waitForTimeout(400);
const chaoDB2 = (await daDoc())[0] || '';
kiem(chaoDB2 !== chaoDB && cauDB.indexOf(chaoDB2) >= 0,
     'Lượt khách sau phát câu chào KHÁC (luân phiên hai biến thể)');

/* KHÁCH VIP — câu chào riêng, nhắc Phòng khánh tiết lầu 10 */
await trang.evaluate(() => { window.veManCho(); });
await trang.waitForTimeout(200);
await trang.click('#mh-cho'); await trang.waitForTimeout(150);
await trang.click('.the-ai'); await trang.waitForTimeout(200);
await trang.evaluate(() => { window.GIA_LAP.cauDaDoc.length = 0; });
await trang.click('.the-loai:nth-child(2)');
await trang.waitForTimeout(400);
const chaoVIP = (await daDoc())[0] || '';
const cauVIP = await trang.evaluate(() => window.DU_LIEU.chao['khach-vip'].cau);
kiem(cauVIP.indexOf(chaoVIP) >= 0, 'Khách VIP có lời chào RIÊNG của bệnh viện');
kiem(chaoVIP !== chaoDB, 'Lời chào VIP khác hẳn lời chào đại biểu');
await anh('09-chat-khach-vip');

console.log('\n═══ 5. HỎI ĐÁP (kho kiến thức chung) ═══');
const buoc = async (cau) => {
  await trang.evaluate(() => { window.GIA_LAP.cauDaDoc.length = 0; });
  await trang.fill('#chat-o', cau);
  await trang.press('#chat-o', 'Enter');
  await trang.waitForTimeout(1400);
  const d = await daDoc();
  return d[d.length - 1] || '';
};

const t1 = await buoc('hifu là gì');
kiem(t1.includes('sóng siêu âm hội tụ cường độ cao'), '"hifu là gì" → đúng định nghĩa bệnh viện');

const t2 = await buoc('mấy giờ khai mạc');
kiem(t2.includes('chín giờ sáng'), '"mấy giờ khai mạc" → TRẢ LỜI ĐƯỢC (app Uông Bí chặn câu này)');

const t3 = await buoc('sau điều trị có mang thai được không');
kiem(t3.includes('ba tháng'), '"có mang thai được không" → đúng câu bệnh viện duyệt');

const t4 = await buoc('điều trị hifu có đau không');
kiem(t4.includes('không cần gây mê'), '"có đau không" → trả lời được, KHÔNG bị chặn nhầm');

/* Cặp câu chỉ khác nhau một tiếng — "khai mạc" (buổi lễ) và "khai trương" (Đơn vị HIFU).
   Đây là ca đã làm bộ tìm kiếm nhập nhằng; giữ cả hai chiều để khỏi sửa hỏng về sau. */
const t5 = await buoc('mấy giờ khai trương đơn vị hifu');
kiem(t5.includes('mười một giờ mười lăm'),
     '"mấy giờ khai trương" → ra Đơn vị HIFU, KHÔNG lẫn với giờ khai mạc buổi lễ');

const t6 = await buoc('mấy giờ trao danh hiệu');
kiem(t6.includes('mười giờ'), '"mấy giờ trao danh hiệu" → đúng mốc nghi thức');

console.log('\n═══ 6. LỚP CHẶN AN TOÀN ═══');
const c1 = await buoc('tôi bị u xơ tử cung thì có nên mổ không');
kiem(c1.includes('không thể tư vấn về sức khỏe'),
     'Hỏi ý kiến y tế CHO CHÍNH MÌNH → bị chặn, không hỏi mô hình');

const c2 = await buoc('có người ngất xỉu');
kiem(c2.includes('cấp cứu') && !c2.includes('dẫn'),
     'Cấp cứu → hô to gọi nhân viên, KHÔNG dẫn đường');

const c3 = await buoc('wifi mật khẩu là gì');
kiem(c3.includes('chưa được cung cấp thông tin'),
     'Wifi (bệnh viện chưa cung cấp) → nói thẳng chưa có, không đoán');

const c4 = await buoc('thời tiết hôm nay thế nào');
kiem(c4.includes('ngoài thông tin tôi được cung cấp'),
     'Câu vô nghĩa → nói thẳng là không biết (ngưỡng tuyệt đối có tác dụng)');
await anh('10-lop-chan');

console.log('\n═══ 7. HAI NÚT BỆNH VIỆN YÊU CẦU ═══');
await trang.evaluate(() => window.veManCho());
await trang.waitForTimeout(250);
await trang.click('#mh-cho'); await trang.waitForTimeout(200);
await trang.evaluate(() => { window.GIA_LAP.cauDaDoc.length = 0; });
await trang.click('.nut-phu-lon');
await trang.waitForTimeout(400);
const moi = (await daDoc())[0] || '';
kiem(moi.includes('Hội trường lầu mười một') && moi.includes('ổn định'),
     'Nút "Mời khách" đọc đúng câu mời vào hội trường');

await trang.click('.chon-duoi .nut-phu-lon:nth-child(2)');
await trang.waitForTimeout(300);
kiem(await manDang() === 'mh-tuvan', 'Nút "Tư vấn thực hiện HIFU" mở màn hai nhánh');
const soNhanh = await trang.$$eval('.the-tv', ns => ns.length);
kiem(soNhanh === 2, 'Có đúng hai nhánh (lần đầu · được chỉ định)');
await anh('11-tu-van-hifu');

await trang.evaluate(() => { window.GIA_LAP.cauDaDoc.length = 0; window.GIA_LAP.diemDaGoi.length = 0; });
await trang.click('.the-tv');
await trang.waitForTimeout(500);
const tv = (await daDoc())[0] || '';
kiem(tv.includes('quầy chăm sóc khách hàng'), 'Nhánh 1 đọc đúng câu tư vấn của bệnh viện');
const hopHien = await trang.$eval('#hoi-lop', n => n.classList.contains('hien'));
kiem(hopHien, 'Hiện hộp hỏi "có muốn tôi dẫn đường không"');
await anh('12-hoi-dan-duong');

await trang.click('#hoi-dong-y');
await trang.waitForTimeout(500);
kiem(await manDang() === 'mh-dan', 'Đồng ý thì robot bắt đầu dẫn');
const diemTV = await trang.evaluate(() => window.GIA_LAP.diemDaGoi);
kiem(diemTV.length === 1 && diemTV[0] === 'Quay CSKH',
     'Dẫn đúng tới quầy chăm sóc khách hàng: "' + diemTV[0] + '"');

console.log('\n═══ 8. VỀ MÀN CHỜ ═══');
await trang.evaluate(() => window.veManCho());
await trang.waitForTimeout(300);
kiem(await manDang() === 'mh-cho', 'Kết thúc lượt thì về màn chờ');
kiem((await hienNhat()).length === 1, 'Chỉ MỘT màn hiện tại một lúc (không chồng màn)');

await trinh.close();

console.log('\n' + '─'.repeat(56));
if (hong === 0) console.log(` TẤT CẢ ${so} PHÉP KIỂM ĐỀU ĐẠT`);
else            console.log(` ${hong}/${so} PHÉP KIỂM HỎNG`);
console.log(' Ảnh soi: demo/anh-soi/');
console.log('─'.repeat(56));
process.exit(hong === 0 ? 0 : 1);
