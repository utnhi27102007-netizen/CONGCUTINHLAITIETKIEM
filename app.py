import streamlit as st
import pandas as pd

# ============================================================
# CẤU HÌNH TRANG
# ============================================================

st.set_page_config(
    page_title="Tính lãi gửi tiết kiệm",
    page_icon="💰",
    layout="wide"
)

# ============================================================
# TIÊU ĐỀ
# ============================================================

st.title("💰 ỨNG DỤNG TÍNH LÃI GỬI TIẾT KIỆM")
st.write(
    "Nhập thông tin khoản tiền gửi để tính tiền lãi định kỳ "
    "và tổng số tiền nhận được."
)

st.divider()

# ============================================================
# NHẬP THÔNG TIN
# ============================================================

col1, col2 = st.columns(2)

with col1:
    so_tien = st.number_input(
        "💵 Số tiền gửi (VNĐ)",
        min_value=0.0,
        value=100_000_000.0,
        step=1_000_000.0,
        format="%.0f"
    )

    ky_han = st.number_input(
        "📅 Kỳ hạn (tháng)",
        min_value=1,
        max_value=600,
        value=12,
        step=1
    )

    lai_suat = st.number_input(
        "📈 Lãi suất (%/năm)",
        min_value=0.0,
        max_value=100.0,
        value=5.0,
        step=0.1,
        format="%.2f"
    )

with col2:
    hinh_thuc_nhan_lai = st.selectbox(
        "💳 Hình thức nhận lãi",
        [
            "Cuối kỳ",
            "Hàng tháng",
            "Hàng quý"
        ]
    )

    loai_lai = st.radio(
        "🧮 Phương pháp tính lãi",
        [
            "Lãi đơn (Simple Interest)",
            "Lãi kép (Compound Interest)"
        ]
    )

st.divider()

# ============================================================
# HÀM ĐỊNH DẠNG TIỀN
# ============================================================

def format_money(value):
    return f"{value:,.0f} VNĐ"


# ============================================================
# TÍNH TOÁN
# ============================================================

if st.button("🧮 TÍNH LÃI", type="primary", use_container_width=True):

    if so_tien <= 0:
        st.error("Vui lòng nhập số tiền gửi lớn hơn 0.")
        st.stop()

    if lai_suat < 0:
        st.error("Lãi suất không được nhỏ hơn 0.")
        st.stop()

    # Lãi suất theo tháng
    lai_suat_nam = lai_suat / 100
    lai_suat_thang = lai_suat_nam / 12

    # ========================================================
    # TRƯỜNG HỢP 1: LÃI ĐƠN
    # ========================================================

    if loai_lai == "Lãi đơn (Simple Interest)":

        # Tổng lãi sau toàn bộ kỳ hạn
        tong_lai = so_tien * lai_suat_nam * (ky_han / 12)

        tong_tien = so_tien + tong_lai

        # Số tháng trong mỗi kỳ nhận lãi
        if hinh_thuc_nhan_lai == "Cuối kỳ":
            so_ky = 1
            thang_moi_ky = ky_han

        elif hinh_thuc_nhan_lai == "Hàng tháng":
            so_ky = ky_han
            thang_moi_ky = 1

        else:  # Hàng quý
            so_ky = ky_han // 3

            # Nếu kỳ hạn không chia hết cho 3,
            # tạo thêm kỳ cuối
            if ky_han % 3 != 0:
                so_ky += 1

            thang_moi_ky = 3

        # Tạo bảng chi tiết
        data = []

        for i in range(1, so_ky + 1):

            if hinh_thuc_nhan_lai == "Cuối kỳ":
                thang = ky_han
                lai_ky = tong_lai

            elif hinh_thuc_nhan_lai == "Hàng tháng":
                thang = 1
                lai_ky = so_tien * lai_suat_thang

            else:
                # Quý cuối có thể ít hơn 3 tháng
                if i < so_ky:
                    thang = 3
                else:
                    thang = ky_han - (so_ky - 1) * 3

                lai_ky = so_tien * lai_suat_nam * (thang / 12)

            data.append({
                "Kỳ": i,
                "Số tháng": thang,
                "Tiền lãi": lai_ky,
                "Tổng tiền": so_tien + lai_ky
            })

    # ========================================================
    # TRƯỜNG HỢP 2: LÃI KÉP
    # ========================================================

    else:

        # ----------------------------------------------------
        # Lãi kép cuối kỳ
        # ----------------------------------------------------

        if hinh_thuc_nhan_lai == "Cuối kỳ":

            # Lãi kép theo tháng
            tong_tien = so_tien * (1 + lai_suat_thang) ** ky_han
            tong_lai = tong_tien - so_tien

            data = [{
                "Kỳ": 1,
                "Số tháng": ky_han,
                "Tiền lãi": tong_lai,
                "Tổng tiền": tong_tien
            }]

        # ----------------------------------------------------
        # Lãi kép nhận hàng tháng
        # ----------------------------------------------------

        elif hinh_thuc_nhan_lai == "Hàng tháng":

            data = []

            tien_hien_tai = so_tien
            tong_lai = 0

            for thang in range(1, ky_han + 1):

                lai_ky = tien_hien_tai * lai_suat_thang
                tien_hien_tai += lai_ky
                tong_lai += lai_ky

                data.append({
                    "Kỳ": thang,
                    "Số tháng": 1,
                    "Tiền lãi": lai_ky,
                    "Tổng tiền": tien_hien_tai
                })

            tong_tien = tien_hien_tai

        # ----------------------------------------------------
        # Lãi kép nhận hàng quý
        # ----------------------------------------------------

        else:

            data = []

            tien_hien_tai = so_tien
            tong_lai = 0
            so_quy = ky_han // 3

            # Xử lý các quý đầy đủ
            for quy in range(1, so_quy + 1):

                lai_quy = tien_hien_tai * (
                    (1 + lai_suat_nam / 4) ** 1 - 1
                )

                tien_hien_tai += lai_quy
                tong_lai += lai_quy

                data.append({
                    "Kỳ": quy,
                    "Số tháng": 3,
                    "Tiền lãi": lai_quy,
                    "Tổng tiền": tien_hien_tai
                })

            # Nếu còn tháng lẻ
            thang_le = ky_han % 3

            if thang_le > 0:

                lai_ky_cuoi = tien_hien_tai * (
                    (1 + lai_suat_thang) ** thang_le - 1
                )

                tien_hien_tai += lai_ky_cuoi
                tong_lai += lai_ky_cuoi

                data.append({
                    "Kỳ": len(data) + 1,
                    "Số tháng": thang_le,
                    "Tiền lãi": lai_ky_cuoi,
                    "Tổng tiền": tien_hien_tai
                })

            tong_tien = tien_hien_tai

    # ========================================================
    # KẾT QUẢ
    # ========================================================

    st.success("✅ Đã tính toán thành công!")

    st.subheader("📊 KẾT QUẢ")

    # 3 ô kết quả
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "💰 Tiền lãi định kỳ",
            format_money(data[0]["Tiền lãi"])
        )

    with col2:
        st.metric(
            "📈 Tổng tiền lãi",
            format_money(tong_lai)
        )

    with col3:
        st.metric(
            "💵 Tổng gốc + lãi",
            format_money(tong_tien)
        )

    # ========================================================
    # THÔNG TIN KHOẢN GỬI
    # ========================================================

    st.subheader("📋 Thông tin khoản gửi")

    info_col1, info_col2, info_col3, info_col4 = st.columns(4)

    with info_col1:
        st.write("**Số tiền gửi**")
        st.write(format_money(so_tien))

    with info_col2:
        st.write("**Kỳ hạn**")
        st.write(f"{ky_han} tháng")

    with info_col3:
        st.write("**Lãi suất**")
        st.write(f"{lai_suat:.2f}%/năm")

    with info_col4:
        st.write("**Phương pháp**")
        st.write(loai_lai)

    # ========================================================
    # BẢNG CHI TIẾT
    # ========================================================

    st.subheader("📑 Chi tiết tiền lãi")

    df = pd.DataFrame(data)

    # Format tiền
    df["Tiền lãi"] = df["Tiền lãi"].apply(format_money)
    df["Tổng tiền"] = df["Tổng tiền"].apply(format_money)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    # ========================================================
    # CÔNG THỨC
    # ========================================================

    with st.expander("📚 Xem công thức tính"):

        if loai_lai == "Lãi đơn (Simple Interest)":

            st.markdown("""
            ### Lãi đơn — Simple Interest

            **Công thức:**

            `Tiền lãi = Tiền gốc × Lãi suất năm × Thời gian`

            Trong đó:

            - Tiền gốc = số tiền ban đầu
            - Lãi suất = lãi suất theo năm
            - Thời gian = số năm gửi

            **Tổng tiền = Tiền gốc + Tiền lãi**
            """)

        else:

            st.markdown("""
            ### Lãi kép — Compound Interest

            **Công thức:**

            `A = P × (1 + r)^n`

            Trong đó:

            - `A` = Tổng số tiền nhận được
            - `P` = Tiền gốc ban đầu
            - `r` = Lãi suất mỗi kỳ
            - `n` = Số kỳ tính lãi

            **Tiền lãi = A - P**
            """)

# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "💡 Công cụ mang tính chất tham khảo. "
    "Lãi suất thực tế của ngân hàng có thể áp dụng các quy định "
    "và cách tính riêng."
)
