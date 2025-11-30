# 💻 Công cụ tính giờ Thở máy – Thở oxy & qui đổi ngày giường HSCC – HSTC

✅ Công cụ hỗ trợ **Điều dưỡng – Bác sĩ khoa Hồi sức tích cực - Chống độc – Hồi sức Cấp cứu**  
✅ Dùng để:
- Tính **giờ thở máy**
- Tính **giờ thở oxy**
- Quy đổi **ngày giường HSCC – HSTC**
- Tính **theo từng ngày độc lập**
- Cộng dồn **tổng số ngày giường toàn đợt điều trị**

> ⚠️ Công cụ **chỉ dùng để tính toán – hiển thị kết quả**,  
> **KHÔNG lưu dữ liệu**, **KHÔNG thay thế phần mềm bệnh viện**.

---

## 👤 Tác giả

- **CNĐD Phan Tấn Lãm**
- **Khoa:** **Hồi sức Tích cực – Chống độc**
- **Đơn vị:**Bệnh viện Đa khoa Đồng Tháp**

---

## 🎯 Chức năng chính

### ✅ 1. Tính giờ thở máy (1 khoảng trong ngày)
- Nhập:
  - `09h15`, `13:40`, `22h`, `24:00`…
- Tự động:
  - Tính tổng phút
  - Quy đổi sang giờ
  - Quy đổi /24
  - Kết luận:
    - `< 0.3` → 1 ngày **HSCC**
    - `0.3 – 0.8` → **0.5 HSCC + 0.5 HSTC**
    - `> 0.8` → 1 ngày **HSTC**

---

### ✅ 2. Tính nhiều phiên thở máy trong nhiều ngày
- Mỗi ngày có thể nhập:
  - Nhiều phiên (ví dụ: 0h–10h, 11h05–24h)
- Hệ thống sẽ:
  - Cộng tất cả phiên **trong cùng 1 ngày**
  - Giới hạn tối đa **1.0 / ngày**
  - Quy đổi **ra HSCC – HSTC cho từng ngày**
- Mỗi ngày được tính **ĐỘC LẬP**
- **Không cộng dồn sai sang ngày khác**

---

### ✅ 3. Cộng dồn toàn bộ ngày giường
Tự động tính:
- ✅ Tổng **HSCC**
- ✅ Tổng **HSTC**
- ✅ Tổng **số ngày giường toàn đợt**

---

### ✅ 4. Tính giờ thở oxy
- Nhập:
  - Giờ bắt đầu – giờ kết thúc
- Kết quả:
  - Tổng giờ oxy
  - Tổng phút oxy

---

## 🧠 Nguyên tắc tính toán

- Mỗi ngày:
  - Tổng quy đổi **Tối đa = 1.0**
- Quy tắc:
  - `< 0.3` → HSCC
  - `0.3 – 0.8` → 0.5 HSCC + 0.5 HSTC
  - `> 0.8` → HSTC
- **Không cộng dồn giờ của ngày sau vào ngày trước**

---

## ▶️ Cách chạy chương trình

### Bước 1: Cài đặt thư viện
```bash
pip install streamlit
