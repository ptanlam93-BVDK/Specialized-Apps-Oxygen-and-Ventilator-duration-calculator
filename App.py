import streamlit as st

# =========================
# CẤU HÌNH TRANG
# =========================
st.set_page_config(
    page_title="Công cụ tính giờ Thở máy/Thở oxy",
    layout="centered"
)

# ===== HEADER LOGO + TÊN BỆNH VIỆN + TÊN KHOA =====
col1, col2 = st.columns([1, 5])

with col1:
    # Đảm bảo file logo.png nằm cùng thư mục app.py
    st.image("logo.png", width=140)

with col2:
    st.markdown(
        """
<div style="margin-top:18px; line-height:1.5; text-align:center;">
    <h1 style="color:#1E90FF; font-weight:bold; margin-bottom:12px;font-size:30px;">
        BỆNH VIỆN ĐA KHOA ĐỒNG THÁP
    </h1>
    <h2 style="color:#66CC66; font-weight:bold; margin-bottom:12px;font-size:22px;">
        Hôm nay phải tốt hơn ngày qua
    </h2>
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
**🔴 Công cụ này chỉ dùng để Tính toán và hiển thị kết quả**, không lưu dữ liệu, không tốn dung lượng,  
**không đăng nhập bất cứ ID hay Useremail/mật khẩu** nào.  

🔴 Hỗ trợ sử dụng **Qui đổi thời gian Thở máy (ngày giường HSCC – HSTC) & thời gian Thở Oxy**.

**🩺 Được xây dựng bởi:** **CNĐD. Phan Tấn Lãm**  
**🟠 Đơn vị:** **Khoa Hồi sức Tích cực - Chống độc**  
**🔴 Bệnh viện:** 🏥 **Bệnh viện Đa khoa Đồng Tháp**  

⛔ **Lưu ý chuyên môn (tóm tắt):**
- **Qui đổi ngày giường** theo tổng thời gian **Thở máy trong từng ngày**:
    - `< 0.3`  → `1` Ngày **HSCC**  
    - `0.3 – 0.8` → `0.5` **HSCC** + `0.5` **HSTC**  
    - `> 0.8`  → `1` Ngày **HSTC**  
- BN nằm **≤ 4 giờ**: **Tính Công khám**.  
- BN nằm **> 4 giờ** nhưng **< 24 giờ**: Tính **1 ngày giường** (HSCC hoặc HSTC theo thực tế).  
- BN được **Chuyển qua nhiều khoa liên tiếp**: **Khoa trung gian không tính ngày giường**  
  (VD: CCTH → **NTH** → HSTC thì **NTH** không tính 0.5 ngày giường, **khoa hiện tại tính ngày giường còn lại**).  
- BN **chuyển viện theo yêu cầu**: **Không tính ngày giường ngày hiện tại**.
    """
)

# ===== CSS LÀM CHỮ TAB TO RÕ =====
st.markdown("""
<style>
div[role="tablist"] > button {
    font-size: 24px !important;
    padding: 8px 16px !important;
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
        font-size: 20px !important;
        padding: 6px 10px !important;
    }
}
</style>
""", unsafe_allow_html=True)
# ===== END CSS TAB =====


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


# ===== TẠO HAI TAB =====
tab_may, tab_oxy = st.tabs(["⏰ Giờ thở máy (ngày giường)", "⏰ Giờ thở oxy"])


# ===============================
# ⏰ TAB: GIỜ THỞ MÁY + NGÀY GIƯỜNG
# ===============================
with tab_may:
    # -------- PHẦN 1: 1 KHOẢNG TRONG NGÀY --------
    st.subheader("💊 TÍNH GIỜ THỞ MÁY + NGÀY GIƯỜNG (Một khoảng trong ngày/24h)")
    st.markdown("Nhập giờ dạng: `09h15`, `13:40`, `22h`, `24:00` …")

    col1, col2 = st.columns(2)
    with col1:
        bd_may = st.text_input("Giờ bắt đầu thở máy", placeholder="VD: 10h00")
    with col2:
        kt_may = st.text_input("Giờ kết thúc thở máy", placeholder="VD: 24:00")

    if st.button("✅ TÍNH GIỜ THỞ MÁY (Một khoảng)"):
        tong_phut_may, err_may = tinh_phut(bd_may, kt_may)
        if err_may:
            st.error("⛔ " + err_may)
        else:
            tong_gio_may = tong_phut_may / 60
            ket_qua_may = round(tong_gio_may / 24, 3)
            hscc_1, hstc_1, loai_text = quy_doi_ngay_giuong(ket_qua_may)

            # Ô kết quả giờ thở máy
            html_may = f"""
<div style="text-align:center; padding:18px; border:2px solid red;
            border-radius:14px; background-color:#FFA500;">
  <div style="font-size:22px; color:#0066FF; font-weight:600;">
    ⏰ Tổng thời gian thở máy
  </div>

  <div style="font-size:34px; font-weight:bold; color:red; margin-top:6px;">
    {tong_gio_may:.2f} GIỜ ({tong_phut_may} phút)
  </div>

  <br>

  <div style="font-size:22px; color:#0066FF; font-weight:600;">
    🧮 Kết quả quy đổi /24
  </div>

  <div style="font-size:42px; font-weight:bold; color:red; margin-top:4px;">
    {ket_qua_may}
  </div>
</div>
"""
            st.markdown(html_may, unsafe_allow_html=True)

            # Dòng ngày ước tính
            st.markdown(
                f"""
<div style="
    margin-top:10px;
    text-align:center;
    padding:10px;
    border-radius:10px;
    background-color:#f0f8ff;
    font-size:20px;
    font-weight:600;
">
    🛏️ Ngày ước tính: HSCC = {hscc_1} | HSTC = {hstc_1}
</div>
                """,
                unsafe_allow_html=True,
            )

            # Chọn màu tóm tắt
            if hscc_1 == 1.0:
                tomtat_color_1 = "#4da6ff"   # xanh HSCC
            elif hscc_1 == 0.5:
                tomtat_color_1 = "#ffa500"   # cam 0.5–0.5
            else:
                tomtat_color_1 = "#ff4d4d"   # đỏ HSTC

            st.markdown("---")
            st.subheader("📌 Tóm tắt nhanh – Ngày giường thở máy (1 khoảng)")
            st.markdown(
                f"""
<div style="
    text-align:center;
    padding:18px;
    border-radius:14px;
    background-color:{tomtat_color_1};
    color:white;
    font-size:24px;
    font-weight:bold;
">
    ✅ {loai_text}
</div>
                """,
                unsafe_allow_html=True,
            )

    # -------- PHẦN 2: NHIỀU NGÀY THỞ MÁY --------
    st.markdown("---")
    st.subheader("📋 NHIỀU NGÀY THỞ MÁY (tính độc lập từng ngày)")

    if "rows_may" not in st.session_state:
        st.session_state["rows_may"] = []

    c1, c2, c3, c4 = st.columns([1.4, 1, 1, 0.8])
    with c1:
        ngay_may = st.text_input("Ngày", placeholder="VD: 29/11/2025", key="may_row_ngay")
    with c2:
        bd_may_row = st.text_input("Giờ bắt đầu", placeholder="VD: 0h", key="may_row_bd")
    with c3:
        kt_may_row = st.text_input("Giờ kết thúc", placeholder="VD: 10h", key="may_row_kt")
    with c4:
        add_may_row = st.button("➕ Thêm phiên THỞ MÁY")

    if add_may_row:
        if not ngay_may:
            st.error("⛔ Vui lòng nhập ngày.")
        else:
            tong_phut_may_row, err_may_row = tinh_phut(bd_may_row, kt_may_row)
            if err_may_row:
                st.error("⛔ " + err_may_row)
            else:
                gio_may_row = round(tong_phut_may_row / 60, 2)
                giatri_may_row = round(gio_may_row / 24, 3)
                st.session_state["rows_may"].append(
                    {
                        "Ngày": ngay_may,
                        "Bắt đầu": bd_may_row,
                        "Kết thúc": kt_may_row,
                        "Giờ thở máy": gio_may_row,
                        "Giá trị /24": giatri_may_row,
                    }
                )

    if st.button("🗑️ Xóa tất cả thời gian thở MÁY"):
        st.session_state["rows_may"] = []

    if st.session_state["rows_may"]:

        # KHUNG ĐẸP
        st.markdown(
            """
<div style="
    border-radius:14px;
    padding:16px;
    background-color:#f0f8ff;
    border:2px solid #1E90FF;
    margin-top:20px;
">
    <h3 style="color:#1E90FF; text-align:center; margin-bottom:12px;">
        🧾 CÁC PHIÊN THỞ MÁY ĐÃ NHẬP
    </h3>
</div>
            """,
            unsafe_allow_html=True,
        )

        # Header
        c1h, c2h, c3h, c4h, c5h, c6h = st.columns([2, 2, 2, 2, 2, 1])
        with c1h:
            st.markdown("**Ngày**")
        with c2h:
            st.markdown("**Bắt đầu**")
        with c3h:
            st.markdown("**Kết thúc**")
        with c4h:
            st.markdown("**Giờ thở máy**")
        with c5h:
            st.markdown("**Giá trị /24**")
        with c6h:
            st.markdown("**Xóa**")

        st.markdown("---")

        # Dòng dữ liệu + nút xóa
        for i, r in enumerate(st.session_state["rows_may"]):
            c1r, c2r, c3r, c4r, c5r, c6r = st.columns([2, 2, 2, 2, 2, 1])

            with c1r:
                st.write(r["Ngày"])
            with c2r:
                st.write(r["Bắt đầu"])
            with c3r:
                st.write(r["Kết thúc"])
            with c4r:
                st.write(r["Giờ thở máy"])
            with c5r:
                st.write(r["Giá trị /24"])
            with c6r:
                if st.button("❌", key=f"xoa_may_{i}"):
                    st.session_state["rows_may"].pop(i)
                    st.rerun()

        # TÍNH THEO TỪNG NGÀY
        tong_theo_ngay_may = {}
        for r in st.session_state["rows_may"]:
            ngay = r["Ngày"]
            tong_theo_ngay_may.setdefault(ngay, 0.0)
            tong_theo_ngay_may[ngay] += r["Giá trị /24"]

        st.markdown("## ✅ KẾT QUẢ NGÀY GIƯỜNG THỞ MÁY THEO TỪNG NGÀY")

        bang_ket_qua_may = []
        tong_hscc_all = 0.0
        tong_hstc_all = 0.0

        for ngay, giatri_raw in sorted(tong_theo_ngay_may.items()):
            giatri = min(giatri_raw, 1.0)
            hscc, hstc, loai = quy_doi_ngay_giuong(giatri)
            tong_hscc_all += hscc
            tong_hstc_all += hstc

            bang_ket_qua_may.append(
                {
                    "Ngày": ngay,
                    "Tổng /24 (tối đa 1.0)": round(giatri, 3),
                    "HSCC": hscc,
                    "HSTC": hstc,
                    "Kết luận": loai,
                }
            )

        st.table(bang_ket_qua_may)

        tong_ngay_giuong = round(tong_hscc_all + tong_hstc_all, 2)

        st.markdown(
            f"""
<div style="
    text-align:center;
    padding:16px;
    border-radius:14px;
    background-color:#1E90FF;
    color:white;
    font-size:22px;
    font-weight:bold;
">
    ✅ TỔNG NGÀY GIƯỜNG: {tong_ngay_giuong}
</div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
<div style="
    margin-top:10px;
    text-align:center;
    padding:16px;
    border-radius:14px;
    background-color:#4da6ff;
    color:white;
    font-size:20px;
    font-weight:bold;
">
    ✅ TỔNG HSCC: {tong_hscc_all}
</div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
<div style="
    margin-top:10px;
    text-align:center;
    padding:16px;
    border-radius:14px;
    background-color:#ff4d4d;
    color:white;
    font-size:20px;
    font-weight:bold;
">
    ✅ TỔNG HSTC: {tong_hstc_all}
</div>
            """,
            unsafe_allow_html=True,
        )


# ===============================
# 🔵 TAB: GIỜ THỞ OXY
# ===============================
with tab_oxy:
    # -------- PHẦN 1: 1 KHOẢNG THỞ OXY TRONG NGÀY --------
    st.subheader("🔵 TÍNH GIỜ THỞ OXY (Một khoảng trong ngày/24h)")
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

    if st.button("✅ TÍNH GIỜ THỞ OXY (Một khoảng)"):
        tong_phut_oxy, err_oxy = tinh_phut(bd_oxy, kt_oxy)

        if err_oxy:
            st.error("⛔ " + err_oxy)
        else:
            tong_gio_oxy = tong_phut_oxy / 60
            ket_qua_oxy = round(tong_gio_oxy, 2)

            html_oxy = f"""
<div style="text-align:center; padding:18px; border:2px solid red;
            border-radius:14px; background-color:#1E90FF;">
  <div style="font-size:22px; color:#FFFFFF; font-weight:600;">
    🕒 Tổng thời gian thở oxy
  </div>

  <div style="font-size:34px; font-weight:bold; color:orange; margin-top:6px;">
    {tong_gio_oxy:.2f} GIỜ ({tong_phut_oxy} phút)
  </div>

  <br>

  <div style="font-size:22px; color:#FFFFFF; font-weight:600;">
    ⏰ Giờ oxy (giờ thẳng)
  </div>

  <div style="font-size:42px; font-weight:bold; color:orange; margin-top:4px;">
    {ket_qua_oxy}
  </div>
</div>
"""
            st.markdown(html_oxy, unsafe_allow_html=True)

    # -------- PHẦN 2: NHIỀU NGÀY THỞ OXY --------
    st.markdown("---")
    st.subheader("📋 NHIỀU NGÀY THỞ OXY (tính độc lập từng ngày)")

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

    if st.button("🗑️ Xóa tất cả thời gian thở OXY"):
        st.session_state["rows_oxy"] = []

    if st.session_state["rows_oxy"]:

        st.markdown(
            """
<div style="
    border-radius:14px;
    padding:16px;
    background-color:#f0f8ff;
    border:2px solid #1E90FF;
    margin-top:20px;
">
    <h3 style="color:#1E90FF; text-align:center; margin-bottom:12px;">
        🧾 CÁC THỜI GIAN THỞ OXY ĐÃ NHẬP
    </h3>
</div>
            """,
            unsafe_allow_html=True,
        )

        c1h, c2h, c3h, c4h, c5h, c6h = st.columns([2, 2, 2, 2, 2, 1])
        with c1h:
            st.markdown("**Ngày**")
        with c2h:
            st.markdown("**Bắt đầu**")
        with c3h:
            st.markdown("**Kết thúc**")
        with c4h:
            st.markdown("**Giờ oxy**")
        with c5h:
            st.markdown("**Giá trị /24**")
        with c6h:
            st.markdown("**Xóa**")

        st.markdown("---")

        for i, r in enumerate(st.session_state["rows_oxy"]):
            c1r, c2r, c3r, c4r, c5r, c6r = st.columns([2, 2, 2, 2, 2, 1])

            with c1r:
                st.write(r["Ngày"])
            with c2r:
                st.write(r["Bắt đầu"])
            with c3r:
                st.write(r["Kết thúc"])
            with c4r:
                st.write(r["Giờ oxy"])
            with c5r:
                st.write(r["Giá trị /24"])
            with c6r:
                if st.button("❌", key=f"xoa_oxy_{i}"):
                    st.session_state["rows_oxy"].pop(i)
                    st.rerun()

        # TÍNH THEO TỪNG NGÀY
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

        # TỔNG GIỜ OXY TOÀN BỘ
        st.markdown("## 📊 TỔNG GIỜ OXY TOÀN BỘ")

        tong_gio_oxy_all = sum(gio_theo_ngay_oxy.values())

        st.markdown(
            f"""
<div style="
    text-align:center;
    padding:16px;
    border-radius:14px;
    background-color:#1E90FF;
    color:white;
    font-size:22px;
    font-weight:bold;
">
    ✅ TỔNG GIỜ OXY TOÀN BỘ: {round(tong_gio_oxy_all, 2)} GIỜ
</div>
            """,
            unsafe_allow_html=True,
        )
