import streamlit as st

st.set_page_config(
    page_title="Công cụ tính giờ Thở máy/Thở oxy",
    layout="centered"
)

# ===== HEADER LOGO + TÊN BỆNH VIỆN + TÊN KHOA =====
col1, col2 = st.columns([1, 5])

with col1:
    st.image("logo.png", width=140)

with col2:
    st.markdown(
        """
        <div style="margin-top:18px; line-height:1.5; text-align:center;">
            <h1 style="color:#1E90FF; font-weight:bold; margin-bottom:12px;font-size:30px;">
                 BỆNH VIỆN ĐA KHOA ĐỒNG THÁP
            <h1 style="color:#66CC66; font-weight:bold; margin-bottom:12px;font-size:22px;">
                 Hôm nay phải tốt hơn ngày qua
            </h1>
            <h4 style="color:#FFA500; font-weight:700; margin-top:10px;font-size:23px;">
                Khoa Hồi sức Tích cực – Chống độc
            </h4>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("---")
st.title("💻 Công cụ tính tiền Qui đổi giờ Thở máy/Thở oxy dành cho Điều dưỡng")

st.markdown(
    """
    **🔴Công cụ này chỉ dùng để Tính toán và hiển thị kết quả**, không lưu dữ liệu, không tốn dung lượng, **không đăng nhập bất cứ ID hay Useremail/mật khẩu** nào.  
    🔴Hỗ trợ sử dụng **Qui đổi thời gian Thở máy (ngày giường HSCC – HSTC) & thời gian Thở Oxy**.

    **🩺Được xây dựng bởi**:**CNĐD**.**Phan Tấn Lãm**;  
    **🟠Đơn vị:** **Khoa Hồi sức Tích cực - Chống độc**;    
    **🔴Bệnh viện:** 🏥 **Bệnh viện Đa khoa Đồng Tháp**.
    
    ⛔ **Lưu ý chuyên môn (tóm tắt):**
    - **Qui đổi ngày giường** theo tổng thời gian **Thở máy trong từng ngày**:
        - `< 0.3`  → `1` Ngày **HSCC**  
        - `0.3 – 0.8` → `0.5` **HSCC** + `0.5` **HSTC**  
        - `> 0.8`  → `1` Ngày **HSTC**  
    - BN nằm **≤ 4 giờ**: **Tính Công khám**.  
    - BN nằm **> 4 giờ** nhưng **< 24 giờ**: Tính **1 ngày giường** (HSCC hoặc HSTC theo thực tế).  
    - BN được **Chuyển qua nhiều khoa liên tiếp**: **Khoa trung gian **không** tính ngày giường**  
      (VD: CCTH → **NTH** → HSTC thì **NTH** không tính 0.5 ngày giường, **khoa hiện tại tính ngày giường còn lại**).  
    - BN **chuyển viện theo yêu cầu**: **Không tính ngày giường ngày hiện tại**.
    """
)
## ===== CSS LÀM CHỮ TAB TO RÕ =====
st.markdown("""
<style>
div[role="tablist"] > button {
    font-size: 28px !important;
    padding: 10px 20px !important;
    font-weight: bold !important;
    line-height: 1.2 !important;
}

div[role="tablist"] > button[aria-selected="true"],
div[role="tablist"] > button[data-selected="true"] {
    color: #FF4500 !important;
    border-bottom: 4px solid #FF4500 !important;
}

@media (max-width: 600px) {
    div[role="tablist"] > button {
        font-size: 28px !important;
        padding: 8px 14px !important;
    }
}
</style>
""", unsafe_allow_html=True)
# ===== END CSS TAB =====
tab_may, tab_oxy = st.tabs(["⏰ Giờ thở máy (ngày giường)", "⏰ Giờ thở oxy"])


# =========================
# HÀM XỬ LÝ GIỜ CHUNG
# =========================
def doi_sang_phut(text: str):
    """
    Nhập: 09:15, 09h15, 9h, 9, 24:00 ...
    Trả về: (tổng_phút, lỗi)
    """
    try:
        t = text.strip().lower()
        if not t:
            return None, "Chưa nhập giờ."

        # bỏ hậu tố phút
        for suffix in ["phút", "phut", "p", "’", "'"]:
            if t.endswith(suffix):
                t = t[: -len(suffix)].strip()

        t = t.replace("giờ", "h")
        t = t.replace(" ", "")
        t = t.replace("h", ":")

        if ":" not in t:
            t = t + ":00"

        parts = t.split(":")
        if len(parts) != 2:
            return None, "Định dạng giờ không hợp lệ. Ví dụ: 09:15 hoặc 09h15."

        h = int(parts[0]) if parts[0] != "" else 0
        m = int(parts[1]) if parts[1] != "" else 0

        if h < 0 or h > 24 or m < 0 or m > 59:
            return None, "Giờ hoặc phút không hợp lệ (giờ 0–24, phút 0–59)."

        if h == 24 and m > 0:
            return None, "24 giờ chỉ được nhập là 24:00."

        return h * 60 + m, None

    except Exception:
        return None, "Phải nhập giờ đúng kiểu 09:15, 9h15, 9h hoặc 9."


def tinh_phut(t_bd: str, t_kt: str):
    """Tính tổng phút trong cùng 1 ngày, tối đa 24h."""
    bd, err1 = doi_sang_phut(t_bd)
    kt, err2 = doi_sang_phut(t_kt)

    if err1:
        return None, err1
    if err2:
        return None, err2

    if kt <= bd:
        return None, "Giờ kết thúc phải LỚN HƠN giờ bắt đầu (trong cùng 1 ngày)."

    tong = kt - bd
    if tong > 1440:
        return None, "Tổng thời gian không được vượt quá 24 giờ."

    return tong, None


def quy_doi_ngay_giuong(tong_ngay: float):
    """
    Quy đổi 1 ngày (đã tính /24) → số ngày HSCC, HSTC và chuỗi mô tả.
    Giới hạn tối đa 1.0 cho mỗi ngày.
    """
    if tong_ngay > 1.0:
        tong_ngay = 1.0

    if tong_ngay < 0.3:
        return 1.0, 0.0, "1 ngày giường HSCC"
    elif 0.3 <= tong_ngay <= 0.8:
        return 0.5, 0.5, "0.5 ngày HSCC + 0.5 ngày HSTC"
    else:
        return 0.0, 1.0, "1 ngày giường HSTC"

# ===============================
# 🔵 TAB: GIỜ THỞ OXY
# ===============================
with tab_oxy:
    # -------- PHẦN 1: 1 KHOẢNG THỞ OXY TRONG NGÀY --------
    st.subheader("🔵 TÍNH GIỜ THỞ OXY (một khoảng trong ngày)")

    st.markdown("Nhập giờ dạng: `09h15`, `13:30`, `22h`, `24:00` …")

    col3, col4 = st.columns(2)
    with col3:
        bd_oxy = st.text_input(
            "Giờ bắt đầu thở oxy",
            placeholder="VD: 13h30",
            key="oxy_bd",
        )
    with col4:
        kt_oxy = st.text_input(
            "Giờ kết thúc thở oxy",
            placeholder="VD: 24:00",
            key="oxy_kt",
        )

    # Nút tính 1 khoảng
    if st.button("✅ TÍNH GIỜ THỞ OXY (một khoảng)"):
        tong_phut_oxy, err_oxy = tinh_phut(bd_oxy, kt_oxy)

        if err_oxy:
            st.error("⛔ " + err_oxy)
        else:
            tong_gio_oxy = tong_phut_oxy / 60
            ket_qua_oxy = round(tong_gio_oxy, 2)

            st.success(
                f"Tổng thời gian thở oxy: {tong_gio_oxy:.2f} giờ ({tong_phut_oxy} phút) – Giờ oxy (giờ thẳng): {ket_qua_oxy}"
            )

    # -------- PHẦN 2: NHIỀU NGÀY THỞ OXY (tính độc lập từng ngày) --------
    st.markdown("---")
    st.subheader("📋 NHIỀU NGÀY THỞ OXY (tính độc lập từng ngày)")

    # Khởi tạo list lưu các phiên oxy
    if "rows_oxy" not in st.session_state:
        st.session_state["rows_oxy"] = []

    d1, d2, d3, d4 = st.columns([1.4, 1, 1, 0.8])
    with d1:
        ngay_oxy = st.text_input(
            "Ngày",
            placeholder="VD: 02/12/2025",
            key="oxy_row_ngay",
        )
    with d2:
        bd_oxy_row = st.text_input(
            "Giờ bắt đầu",
            placeholder="VD: 0h",
            key="oxy_row_bd",
        )
    with d3:
        kt_oxy_row = st.text_input(
            "Giờ kết thúc",
            placeholder="VD: 10h",
            key="oxy_row_kt",
        )
    with d4:
        add_oxy_row = st.button("➕ Thêm phiên OXY")

    # Khi bấm thêm 1 phiên oxy
    if add_oxy_row:
        if not ngay_oxy:
            st.error("⛔ Vui lòng nhập ngày.")
        else:
            tong_phut_oxy_row, err_oxy_row = tinh_phut(bd_oxy_row, kt_oxy_row)
            if err_oxy_row:
                st.error("⛔ " + err_oxy_row)
            else:
                gio_oxy_row = round(tong_phut_oxy_row / 60, 2)
                giatri_oxy_row = round(gio_oxy_row / 24, 3)

                st.session_state["rows_oxy"].append(
                    {
                        "Ngày": ngay_oxy,
                        "Bắt đầu": bd_oxy_row,
                        "Kết thúc": kt_oxy_row,
                        "Giờ oxy": gio_oxy_row,
                        "Giá trị /24": giatri_oxy_row,
                    }
                )

    # Nút xóa hết
    if st.button("🗑️ Xóa tất cả thời gian thở OXY"):
        st.session_state["rows_oxy"] = []

    # Nếu có dữ liệu oxy đã nhập
    if st.session_state["rows_oxy"]:
        st.markdown("### 🧾 CÁC PHIÊN THỞ OXY ĐÃ NHẬP")
        st.table(st.session_state["rows_oxy"])

        # Tính tổng theo từng ngày
        tong_theo_ngay_oxy = {}
        gio_theo_ngay_oxy = {}
        for r in st.session_state["rows_oxy"]:
            ngay = r["Ngày"]
            tong_theo_ngay_oxy.setdefault(ngay, 0.0)
            gio_theo_ngay_oxy.setdefault(ngay, 0.0)
            tong_theo_ngay_oxy[ngay] += r["Giá trị /24"]
            gio_theo_ngay_oxy[ngay] += r["Giờ oxy"]

        st.markdown("## ✅ KẾT QUẢ GIỜ OXY THEO TỪNG NGÀY")

        bang_ket_qua_oxy = []
        for ngay, giatri in sorted(tong_theo_ngay_oxy.items()):
            gio_ngay = gio_theo_ngay_oxy[ngay]
            bang_ket_qua_oxy.append(
                {
                    "Ngày": ngay,
                    "Tổng giờ oxy": round(gio_ngay, 2),
                    "Tổng /24": round(giatri, 3),
                }
            )

        st.table(bang_ket_qua_oxy)

        # ====== CỘNG DỒN TOÀN BỘ GIỜ OXY (KHÔNG TÍNH /24) ======
        st.markdown("## 📊 TỔNG GIỜ OXY TOÀN BỘ")

        tong_gio_oxy_all = sum(r["Giờ oxy"] for r in st.session_state["rows_oxy"])

        st.success(f"✅ TỔNG GIỜ OXY TOÀN BỘ: {round(tong_gio_oxy_all, 2)} giờ")
