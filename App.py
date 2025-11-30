import streamlit as st

# =========================
# CẤU HÌNH & GIỚI THIỆU
# =========================
st.set_page_config(
    page_title="Công cụ tính giờ Thở máy/Thở oxy",
    layout="centered"
)

st.title("💻 Công cụ tính giờ Thở máy/Thở oxy dành cho điều dưỡng")

st.markdown(
    """
    Công cụ này chỉ dùng để ** Tính toán và hiển thị kết quả **, không lưu dữ liệu, không tốn dung lượng, không đăng nhập bất cứ ID hay Usermail và mật khẩu nào.  
    Hỗ trợ sử dụng tính toán ** Qui đổi thời gian Thở máy (Ngày giường HSCC – HSTC) & thời gian Thở Oxy **.
    **Được xây dựng bởi:** CNĐD. **Phan Tấn Lãm**, **Đơn vị:** Khoa Hồi sức tích cực - Chống độc, **Bệnh viện:**🏥 Bệnh viện Đa khoa Đồng Tháp.
    ⛔ Lưu ý: Thời gian Thở máy qui ra (Ngày giường HSCC – HSTC) phải dựa theo thực tế. Phần mềm Không thể tính chính xác **Tuyệt đối**.
    < 0.3 → 1 HSCC, >= 0.3 – <= 0.8 → 0.5 HSCC + 0.5 HSTC, >= 0.8 → 1 HSTC, Bệnh nhân thời gian nằm dưới <= 4giờ tính công khám,  Bệnh nhân thời gian nằm dưới >4giờ tính 1 Ngày giường HSCC hoặc HSTC,
    ** Thời điểm nằm 2 khoa liên tiếp khoa chuyển tiếp không tính ngày giường (Ví dụ: Nếu BN nằm CCTH - NTH - HSTC,  thì  NTH sẽ không tính 0.5 ngày giường, HSTC sẽ tính ngày giường)**.
    ** Bệnh nhân Chuyển viện theo yêu cầu: Không tính ngày giường ngày hiện tại cho dù Bác sĩ Tiên lượng nặng, trung binh, không thay đổi,...)**.
    ** Thời điểm Bệnh nhân nằm <24h tính 1 ngày giường Ngày giường HSCC hoặc HSTC**.
    
    """
)

tab_may, tab_oxy = st.tabs(["⏰ Giờ thở máy + ngày giường", "⏰ Giờ thở oxy"])


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
# ⏰ TAB: GIỜ THỞ MÁY + NGÀY GIƯỜNG
# ===============================
with tab_may:
    # -------- PHẦN 1: 1 KHOẢNG TRONG NGÀY --------
    st.subheader("💊 Tính GIỜ THỞ MÁY và NGÀY GIƯỜNG (1 khoảng trong ngày)")

    st.markdown("Nhập giờ dạng: `09h15`, `13:40`, `22h`, `24:00` …")

    col1, col2 = st.columns(2)
    with col1:
        bd_may = st.text_input("Giờ bắt đầu thở máy", placeholder="VD: 10h00")
    with col2:
        kt_may = st.text_input("Giờ kết thúc thở máy", placeholder="VD: 24:00")

    if st.button("✅ TÍNH GIỜ THỞ MÁY (1 khoảng)"):
        tong_phut, err = tinh_phut(bd_may, kt_may)

        if err:
            st.error("⛔ " + err)
        else:
            tong_gio = tong_phut / 60
            ket_qua = round(tong_gio / 24, 3)
            hscc_1, hstc_1, loai_text = quy_doi_ngay_giuong(ket_qua)

            st.markdown("---")
            st.markdown(
                f"""
                <div style="
                    text-align:center;
                    padding:18px;
                    border:2px solid red;
                    border-radius:14px;
                    background-color:#FFA500;
                ">
                    <div style="
                        font-size:22px;
                        color:#0066FF;
                        font-weight:600;
                    ">
                        ⏰ Tổng thời gian thở máy
                    </div>

                    <div style="
                        font-size:34px;
                        font-weight:bold;
                        color:red;
                    ">
                        {tong_gio:.2f} GIỜ ({tong_phut} phút)
                    </div>

                    <br>

                    <div style="
                        font-size:22px;
                        color:#0066FF;
                        font-weight:600;
                    ">
                        🧮 Kết quả quy đổi /24
                    </div>

                    <div style="
                        font-size:42px;
                        font-weight:bold;
                        color:red;
                    ">
                        {ket_qua}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

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
                    🛏️ Ngày ước tính: HSCC = {hscc_1} &nbsp;&nbsp;|&nbsp;&nbsp; HSTC = {hstc_1}
                </div>
                """,
                unsafe_allow_html=True
            )

            # Chọn màu cho khung tóm tắt
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
                unsafe_allow_html=True
            )

    # -------- PHẦN 2: NHIỀU PHIÊN, NHIỀU NGÀY --------
    st.markdown("---")
    st.subheader("📋 NHIỀU NGÀY THỞ MÁY (tính độc lập từng ngày)")

    if "rows_may" not in st.session_state:
        st.session_state["rows_may"] = []

    c1, c2, c3, c4 = st.columns([1.4, 1, 1, 0.8])
    with c1:
        ngay_label = st.text_input("Ngày", placeholder="VD: 29/11/2025", key="row_ngay")
    with c2:
        bd_row = st.text_input("Giờ bắt đầu", placeholder="VD: 0h", key="row_bd")
    with c3:
        kt_row = st.text_input("Giờ kết thúc", placeholder="VD: 10h", key="row_kt")
    with c4:
        add_row = st.button("➕ Thêm phiên")

    if add_row:
        if not ngay_label:
            st.error("⛔ Vui lòng nhập ngày.")
        else:
            tong_phut_row, err_row = tinh_phut(bd_row, kt_row)
            if err_row:
                st.error("⛔ " + err_row)
            else:
                gio_row = round(tong_phut_row / 60, 2)
                giatri_row = round(gio_row / 24, 3)

                st.session_state["rows_may"].append(
                    {
                        "Ngày": ngay_label,
                        "Bắt đầu": bd_row,
                        "Kết thúc": kt_row,
                        "Giờ thở máy": gio_row,
                        "Giá trị /24": giatri_row,
                    }
                )

    if st.button("🗑️ Xóa tất cả phiên"):
        st.session_state["rows_may"] = []

    if st.session_state["rows_may"]:
        st.markdown("### 🧾 Các phiên thở máy đã nhập")
        st.table(st.session_state["rows_may"])

        # Gom tổng theo từng ngày
        tong_theo_ngay = {}
        for r in st.session_state["rows_may"]:
            ngay = r["Ngày"]
            tong_theo_ngay.setdefault(ngay, 0.0)
            tong_theo_ngay[ngay] += r["Giá trị /24"]

        st.markdown("## ✅ KẾT QUẢ NGÀY GIƯỜNG THEO TỪNG NGÀY")

        tong_hscc = 0.0
        tong_hstc = 0.0
        bang_ket_qua = []

        # Duyệt từng ngày (sắp xếp theo tên ngày cho dễ nhìn)
        for ngay, tong_ngay_raw in sorted(tong_theo_ngay.items()):
            tong_ngay = tong_ngay_raw
            if tong_ngay > 1.0:
                tong_ngay = 1.0  # mỗi ngày tối đa 1.0

            hscc, hstc, loai = quy_doi_ngay_giuong(tong_ngay)
            tong_hscc += hscc
            tong_hstc += hstc

            bang_ket_qua.append({
                "Ngày": ngay,
                "Tổng /24 (giới hạn 1.0)": round(tong_ngay, 3),
                "HSCC": hscc,
                "HSTC": hstc,
                "Kết luận": loai,
            })

        st.table(bang_ket_qua)

        # CỘNG DỒN TẤT CẢ CÁC NGÀY
        tong_cong = round(tong_hscc + tong_hstc, 2)

        st.markdown("## 📊 CỘNG DỒN TOÀN BỘ NGÀY GIƯỜNG")

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
                ✅ TỔNG CỘNG TOÀN BỘ NGÀY GIƯỜNG: {tong_cong}
            </div>
            """,
            unsafe_allow_html=True
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
                font-size:22px;
                font-weight:bold;
            ">
                ✅ TỔNG HSCC: {tong_hscc}
            </div>
            """,
            unsafe_allow_html=True
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
                font-size:22px;
                font-weight:bold;
            ">
                ✅ TỔNG HSTC: {tong_hstc}
            </div>
            """,
            unsafe_allow_html=True
        )


# ===============================
# 🔵 TAB: GIỜ THỞ OXY
# ===============================
with tab_oxy:
    st.subheader("🔵 Tính GIỜ THỞ OXY")

    st.markdown("Nhập giờ dạng: `09h15`, `13:30`, `22h`, `24:00` …")

    col3, col4 = st.columns(2)
    with col3:
        bd_oxy = st.text_input("Giờ bắt đầu thở oxy", placeholder="VD: 13h30", key="oxy_bd")
    with col4:
        kt_oxy = st.text_input("Giờ kết thúc thở oxy", placeholder="VD: 24:00", key="oxy_kt")

    if st.button("✅ TÍNH GIỜ THỞ OXY"):
        tong_phut_oxy, err_oxy = tinh_phut(bd_oxy, kt_oxy)

        if err_oxy:
            st.error("⛔ " + err_oxy)
        else:
            tong_gio_oxy = tong_phut_oxy / 60
            ket_qua_oxy = round(tong_gio_oxy, 2)

            st.markdown("---")
            st.markdown(
                f"""
                <div style="
                    text-align:center;
                    padding:18px;
                    border:2px solid red;
                    border-radius:14px;
                    background-color:#1E90FF;
                ">
                    <div style="
                        font-size:22px;
                        color:#FFFFFF;
                        font-weight:600;
                    ">
                        🕒 Tổng thời gian thở oxy
                    </div>

                    <div style="
                        font-size:34px;
                        font-weight:bold;
                        color:orange;
                    ">
                        {tong_gio_oxy:.2f} GIỜ ({tong_phut_oxy} phút)
                    </div>

                    <br>

                    <div style="
                        font-size:22px;
                        color:#FFFFFF;
                        font-weight:600;
                    ">
                        ⏰ Giờ oxy 
                    </div>

                    <div style="
                        font-size:42px;
                        font-weight:bold;
                        color:orange;
                    ">
                        {ket_qua_oxy}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
