import streamlit as st
import base64
import pandas as pd
import os
from sqlalchemy import create_engine
from kmodes.kmodes import KModes
import plotly.express as px
import io 

st.set_page_config(
    page_title="Monitoring Try Out",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# SESSION LOGIN
# =========================

if "login_status" not in st.session_state:
    st.session_state.login_status = False

# =========================
# LOAD BACKGROUND IMAGE
# =========================

def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(
            img_file.read()
        ).decode()

bg_image = get_base64_image(
    "assets/background.jpeg"
)

# =========================
# DATABASE SUPABASE
# =========================

DATABASE_URL = os.getenv(
    "SUPABASE_DATABASE_URL",
    "postgresql://postgres.oqfjkxiubuwfvniqjbtk:TOTKASMPALMANSHUR123@aws-1-ap-northeast-2.pooler.supabase.com:5432/postgres"
)

engine = create_engine(
    DATABASE_URL
)

# =========================
# SIDEBAR
# =========================

with st.sidebar:

    if "menu" not in st.session_state:
        st.session_state.menu = None

    st.sidebar.button(
        "Menu Orang Tua",
        use_container_width=True,
        on_click=lambda: st.session_state.update(
            {"menu": "orang_tua"}
        )
    )

    st.sidebar.button(
        "Menu Admin",
        use_container_width=True,
        on_click=lambda: st.session_state.update(
            {"menu": "admin"}
        )
    )

    if st.session_state.menu == "admin":

        st.subheader("Login Admin")

        username = st.text_input(
            "Username"
        )

        password = st.text_input(
            "Password",
            type="password"
        )

        if st.button("Login"):

            if (
                username == "admin"
                and
                password == "admin123"
            ):

                st.session_state.login_status = True

            else:

                st.error(
                    "Username atau Password salah"
                )

    if st.session_state.login_status:

        st.success(
            "Login berhasil"
        )

        st.markdown("---")

        st.subheader(
            "Upload Data Terbaru"
        )

        batch_to = st.selectbox(
            "Pilih Batch TO",
            [
                "TO 1",
                "TO 2",
                "TO 3",
                "TO 4",
                "TO 5",
                "Lainnya"
            ]
        )

        if batch_to == "Lainnya":

            nomor_to = st.number_input(
                "Masukkan Nomor TO",
                min_value=6,
                step=1
            )

            batch_to = f"TO {nomor_to}"

        uploaded_file = st.file_uploader(
            "Upload File",
            type=["csv", "xlsx"]
        )

        if st.button(
            "Proses & Update Data"
        ):

            if uploaded_file:

                try:

                    # =====================
                    # BACA FILE
                    # =====================

                    if uploaded_file.name.endswith(
                        ".csv"
                    ):

                        df = pd.read_csv(
                            uploaded_file
                        )

                    else:

                        df = pd.read_excel(
                            uploaded_file
                        )

                    # =====================
                    # RENAME KOLOM
                    # =====================

                    df = df.rename(
                        columns={
                            "Nama Siswa":
                                "nama_siswa",

                            "Bilangan":
                                "bilangan",

                            "Aljabar":
                                "aljabar",

                            "Geometri":
                                "geometri",

                            "Peluang":
                                "peluang",

                            "Tekstual":
                                "tekstual",

                            "Inferensial":
                                "inferensial",

                            "Evaluasi":
                                "evaluasi"
                        }
                    )

                    # Hapus kolom No
                    if "No" in df.columns:

                        df = df.drop(
                            columns=["No"]
                        )

                    # Tambahkan batch TO
                    df["batch_to"] = batch_to

                    # =====================
                    # SIMPAN DATABASE
                    # =====================

                    df.to_sql(
                        "NILAI_TRYOUT",
                        engine,
                        if_exists="append",
                        index=False
                    )

                    st.success("BERHASIL MASUK TO_SQL")

                    st.success(
                        f"Data {batch_to} berhasil diupload"
                    )

                    st.info(
                        f"{len(df)} data siswa berhasil disimpan"
                    )

                except Exception as e:

                    import traceback

                    st.error(
                        f"Terjadi error: {e}"
                    )

                    st.code(
                        traceback.format_exc()
                    )

            else:

                st.warning(
                    "Silakan pilih file terlebih dahulu"
                )

        # =====================
        # RESET DATA
        # =====================

        st.markdown("---")

        st.subheader(
            "Reset Data"
        )

        konfirmasi_reset = st.checkbox(
            "Saya yakin ingin menghapus seluruh data"
        )

        if st.button(
            "Reset All Data",
            use_container_width=True
        ):

            if konfirmasi_reset:

                try:

                    with engine.begin() as conn:

                        conn.exec_driver_sql(
                            'DELETE FROM "NILAI_TRYOUT"'
                        )

                    st.success(
                        "Seluruh data berhasil dihapus"
                    )

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"Gagal reset data: {e}"
                    )

            else:

                st.warning(
                    "Centang konfirmasi terlebih dahulu"
                )

# =========================
# HALAMAN UTAMA
# =========================

st.markdown(f"""
<style>

.stApp {{

    background-image:
        linear-gradient(
            rgba(0,0,0,0.80),
            rgba(0,0,0,0.80)
        ),
        url("data:image/jpg;base64,{bg_image}");

    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;
}}

table {{
    border-collapse: collapse;
    table-layout: fixed;
}}

th,
td {{
    white-space: nowrap;
}}

.main-title {{
    text-align:center;
    color:white;
    font-size:70px;
    font-weight:bold;
    margin-top:120px;
}}

.sub-title {{
    text-align:center;
    color:#dddddd;
    font-size:28px;
}}

/* HEADER TABEL */
[data-testid="stDataFrame"] thead th {{
    color: white !important;
    font-weight: 700 !important;
    text-align: center !important;
}}

/* ISI TABEL */
[data-testid="stDataFrame"] td {{
    color: white !important;
    font-weight: 600 !important;
}}

/* NAMA SISWA */
[data-testid="stDataFrame"] tbody th {{
    color: white !important;
    font-weight: 700 !important;
}}

/* GARIS TABEL */
[data-testid="stDataFrame"] table {{
    border-color: rgba(255,255,255,0.2) !important;
}}

</style>
""",
unsafe_allow_html=True)

st.markdown(
    """
    <div class="main-title">
    SMP AL MANSHUR CANDI
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="sub-title">
    Sistem Monitoring Try Out TKA Siswa
    </div>
    """,
    unsafe_allow_html=True
)
# =========================
# TAMPILKAN DATA DATABASE
# =========================

st.markdown("<br><br>", unsafe_allow_html=True)

if (
    st.session_state.menu == "orang_tua"
    or
    st.session_state.login_status
):

    mata_pelajaran = st.segmented_control(
        "Pilih Mata Pelajaran",
        [
            "Matematika",
            "Bahasa Indonesia"
        ],
        default="Matematika"
    )

    data = pd.read_sql(
        """
        SELECT *
        FROM "NILAI_TRYOUT"
        """,
        engine
    )

    if mata_pelajaran == "Matematika":

        sub_mapel = [
            "bilangan",
            "aljabar",
            "geometri",
            "peluang"
        ]

    else:

        sub_mapel = [
            "tekstual",
            "inferensial",
            "evaluasi"
        ]

    hasil = []

    df_kategori = pd.DataFrame()
    df_status = pd.DataFrame()

    for sub in sub_mapel:

        pivot = data.pivot_table(
            index="nama_siswa",
            columns="batch_to",
            values=sub
        )

        # =====================
        # CARI 2 TO TERAKHIR
        # =====================

        daftar_to = list(pivot.columns)

        if len(daftar_to) >= 2:

            to_sebelumnya = daftar_to[-2]
            to_terakhir = daftar_to[-1]

            pivot["STATUS"] = pivot.apply(
                lambda row:
                "Meningkat"
                if row[to_terakhir] > row[to_sebelumnya]
                else
                "Menurun"
                if row[to_terakhir] < row[to_sebelumnya]
                else
                "Tetap",
                axis=1
            )

            to_terakhir = daftar_to[-1]

            if mata_pelajaran == "Matematika":

                pivot["KATEGORI"] = pivot[to_terakhir].apply(
                    lambda x:
                        "Sangat Baik" if x > 52.13
                        else "Baik" if x > 40.34
                        else "Kurang" if x > 29.34
                        else "Sangat Kurang"
                )
                df_kategori[sub] = pivot["KATEGORI"]
                df_status[sub] = pivot["STATUS"]

            else:

                pivot["KATEGORI"] = pivot[to_terakhir].apply(
                    lambda x:
                        "Sangat Baik" if x > 77.94
                        else "Baik" if x > 60.83
                        else "Kurang" if x > 43.72
                        else "Sangat Kurang"
                )
                df_kategori[sub] = pivot["KATEGORI"]
                df_status[sub] = pivot["STATUS"]

        else:

            pivot["STATUS"] = "-"

        # =====================
        # BUAT HEADER BERTINGKAT
        # =====================

        kolom_baru = []

        for col in pivot.columns:

            if col == "STATUS":

                kolom_baru.append(
                    (sub.title(), "STATUS")
                )

            else:

                kolom_baru.append(
                    (sub.title(), col)
                )

        pivot.columns = pd.MultiIndex.from_tuples(
            kolom_baru
        )

        hasil.append(pivot)

    tabel_final = pd.concat(
        hasil,
        axis=1
    )

    df_kategori.index.name = "nama_siswa"
    df_kategori = df_kategori.reset_index()

    # =====================
    # KMODES
    # =====================

    fitur_cluster = df_kategori.drop(
        columns=["nama_siswa"]
    )

    if fitur_cluster.empty:

        st.warning(
            "Belum ada data yang tersedia. Silakan upload data terlebih dahulu."
        )

        st.stop()

    km = KModes(
        n_clusters=2,
        init="Huang",
        n_init=10,
        random_state=42
    )

    cluster = km.fit_predict(
        fitur_cluster
    )

    df_kategori["CLUSTER"] = cluster
    skor_map = {
        "Sangat Kurang": 1,
        "Kurang": 2,
        "Baik": 3,
        "Sangat Baik": 4
    }

    fitur_skor = fitur_cluster.replace(
        skor_map
    )

    fitur_skor["CLUSTER"] = cluster

    rata_cluster = (
        fitur_skor
        .groupby("CLUSTER")
        .mean()
        .mean(axis=1)
    )
    cluster_siap = rata_cluster.idxmax()

    df_kategori["HASIL_AKHIR"] = df_kategori[
        "CLUSTER"
    ].apply(
        lambda x:
        "Siap Tes TKA"
        if x == cluster_siap
        else
        "Belum Siap Tes TKA"
    )

    # =====================
    # KPI DASHBOARD
    # =====================

    total_siswa = len(df_kategori)

    jumlah_siap = (
        df_kategori["HASIL_AKHIR"]
        .eq("Siap Tes TKA")
        .sum()
    )

    jumlah_belum = (
        df_kategori["HASIL_AKHIR"]
        .eq("Belum Siap Tes TKA")
        .sum()
    )

    persentase_siap = (
        jumlah_siap / total_siswa * 100
    )

    st.markdown(
        "<h2>Dashboard Try Out TKA Siswa</h2>",
        unsafe_allow_html=True
    )

    col1, col2, col3, col4 = st.columns(4)

    card_style = """
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 15px;
    padding: 20px;
    height: 120px;
    """

    with col1:
        st.markdown(
            f"""
            <div style="{card_style}">
                <div style="color:#E5E7EB;text-transform:uppercase;font-size:16px;letter-spacing:0.5px;font-weight:800;">
                    Total Siswa
                </div>
                <div style="font-size:42px;font-weight:bold;color:white;">
                    {total_siswa}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <div style="{card_style}">
                <div style="color:#E5E7EB;text-transform:uppercase;font-size:16px;letter-spacing:0.5px;font-weight:800;">
                    Siap Tes TKA
                </div>
                <div style="font-size:42px;font-weight:bold;color:white;">
                    {jumlah_siap}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            f"""
            <div style="{card_style}">
                <div style="color:#E5E7EB;text-transform:uppercase;font-size:16px;letter-spacing:0.5px;font-weight:800;">
                    Belum Siap Tes TKA
                </div>
                <div style="font-size:42px;font-weight:bold;color:white;">
                    {jumlah_belum}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col4:
        st.markdown(
            f"""
            <div style="{card_style}">
                <div style="color:#E5E7EB;text-transform:uppercase;font-size:16px;letter-spacing:0.5px;font-weight:800;">
                    Persentase Siap
                </div>
                <div style="font-size:42px;font-weight:bold;color:white;">
                    {persentase_siap:.1f}%
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # =====================
    # PIE CHART
    # =====================

    st.markdown("<br>", unsafe_allow_html=True)

    col_pie, col_kanan = st.columns([1, 2])

    with col_pie:

        data_pie = {
            "Status": [
                "Siap Tes TKA",
                "Belum Siap Tes TKA"
            ],
            "Jumlah": [
                jumlah_siap,
                jumlah_belum
            ]
        }

        fig_pie = px.pie(
            data_pie,
            names="Status",
            values="Jumlah",
            hole=0.45
        )

        fig_pie.update_traces(
            textinfo="percent",
            textfont=dict(
                size=18,
                color="white",
                family="Arial Black"
            ),
            marker=dict(
                colors=[
                    "#038031",
                    "#920000"
                ]
            )
        )

        fig_pie.update_layout(
            title=dict(
                text="Kesiapan Tes TKA",
                font=dict(
                    size=16,
                    color="#F3F4F6"
                )
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(
                color="white"
            ),
            legend=dict(
                orientation="h",
                y=-0.15,
                font=dict(
                    size=14,
                    color="white"
                )
            ),
            margin=dict(
                l=20,
                r=20,
                t=50,
                b=20
            )
        )

        st.plotly_chart(
            fig_pie,
            use_container_width=False
        )

    with col_kanan:

        if mata_pelajaran == "Matematika":

            col_kosong, col_filter = st.columns([1.75, 4])

            with col_filter:

                sub_dashboard = st.segmented_control(
                    "",
                    [
                        "Bilangan",
                        "Aljabar",
                        "Geometri",
                        "Peluang"
                    ],
                    default="Bilangan"
            )

        else:
            col_kosong, col_filter = st.columns([2, 4])

            with col_filter:

                sub_dashboard = st.segmented_control(
                    "",
                    [
                        "Tekstual",
                        "Inferensial",
                        "Evaluasi"
                    ],
                    default="Tekstual"
                )

        sub_dashboard = sub_dashboard.lower()

        kategori_urut = [
            "Sangat Baik",
            "Baik",
            "Kurang",
            "Sangat Kurang"
        ]

        kategori_count = (
            df_kategori[sub_dashboard]
            .value_counts()
            .reindex(kategori_urut, fill_value=0)
            .reset_index()
        )

        kategori_count.columns = [
            "Kategori",
            "Jumlah"
        ]

        status_count = (
            df_status[sub_dashboard]
            .value_counts()
            .reset_index()
        )

        status_count.columns = [
            "Status",
            "Jumlah"
        ]

        col_kategori, col_status = st.columns(2)

        with col_kategori:

            warna_kategori = {
                "Sangat Baik": "#038031",
                "Baik": "#8eac0a",
                "Kurang": "#b3560b",
                "Sangat Kurang": "#920000"
            }

            fig_kategori = px.bar(
                kategori_count,
                x="Jumlah",
                y="Kategori",
                orientation="h",
                text="Jumlah",
                color="Kategori",
                color_discrete_map=warna_kategori
            )

            fig_kategori.update_layout(
                title="Distribusi Kategori",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="white", size=14),
                xaxis_title=None,
                yaxis_title=None,
                showlegend=False,
                height=420,
                width=500,
                bargap=0.15,

                xaxis=dict(
                    tickfont=dict(
                        size=14,
                        color="white"
                    ),
                    showgrid=False
                ),

                yaxis=dict(
                    tickfont=dict(
                        size=14,
                        color="white"
                    )
                )
            )

            fig_kategori.update_traces(
                textposition="outside",
                width=0.7,
                textfont=dict(
                    color="white",
                    size=14
                )
            )

            fig_kategori.update_yaxes(
                automargin=True,
                categoryorder="array",
                categoryarray=[
                    "Sangat Kurang",
                    "Kurang",
                    "Baik",
                    "Sangat Baik"
                ],
                ticklabelposition="outside",
            )

            st.plotly_chart(
                fig_kategori,
                use_container_width=True
            )

        with col_status:

            status_order = [
                "Meningkat",
                "Tetap",
                "Menurun"
            ]

            status_count = (
                df_status[sub_dashboard]
                .value_counts()
                .reindex(
                    status_order,
                    fill_value=0
                )
                .reset_index()
            )

            status_count.columns = [
                "Status",
                "Jumlah"
            ]

            warna_status = {
                "Meningkat": "#038031",
                "Tetap": "#ca8a04",
                "Menurun": "#920000"
            }

            fig_status = px.bar(
                status_count,
                x="Jumlah",
                y="Status",
                orientation="h",
                text="Jumlah",
                color="Status",
                color_discrete_map=warna_status
            )

            fig_status.update_layout(
                title="Distribusi Status",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="white"),
                xaxis_title=None,
                yaxis_title=None,
                showlegend=False,
                height=420,
                width=500,
                bargap=0.15,

                xaxis=dict(
                    tickfont=dict(
                        size=14,
                        color="white"
                    )
                ),

                yaxis=dict(
                    tickfont=dict(
                        size=14,
                        color="white"
                    )
                )
            )

            fig_status.update_traces(
                textposition="outside",
                width=0.6,
                textfont=dict(
                    color="white",
                    size=14
                )
            )

            st.plotly_chart(
                fig_status,
                use_container_width=True
            )

    # =====================
    # AMBIL TO TERAKHIR
    # =====================

    to_terakhir = (
        data["batch_to"]
        .sort_values()
        .unique()[-1]
    )

    data_to_terakhir = (
        data[
            data["batch_to"] == to_terakhir
        ]
    )

    # =====================
    # RANKING SUB MAPEL
    # =====================

    if mata_pelajaran == "Matematika":

        daftar_sub = [
            "bilangan",
            "aljabar",
            "geometri",
            "peluang"
        ]

    else:

        daftar_sub = [
            "tekstual",
            "inferensial",
            "evaluasi"
        ]

    ranking_sub = []

    for sub in daftar_sub:

        rata2 = (
            data_to_terakhir[sub]
            .mean()
        )

        ranking_sub.append([
            sub.title(),
            round(rata2, 2)
        ])

    df_ranking_sub = pd.DataFrame(
        ranking_sub,
        columns=[
            "Sub Mapel",
            "Rata-rata"
        ]
    )

    df_ranking_sub = (
        df_ranking_sub
        .sort_values(
            by="Rata-rata",
            ascending=False
        )
        .reset_index(drop=True)
    )

    # =====================
    # TOP 5 SISWA
    # =====================

    to_terakhir = (
        data["batch_to"]
        .sort_values()
        .unique()[-1]
    )

    data_top = (
        data[
            data["batch_to"] == to_terakhir
        ]
        .copy()
    )

    if mata_pelajaran == "Matematika":

        data_top["RATA_MAPEL"] = (
            data_top[
                [
                    "bilangan",
                    "aljabar",
                    "geometri",
                    "peluang"
                ]
            ]
            .mean(axis=1)
        )

    else:

        data_top["RATA_MAPEL"] = (
            data_top[
                [
                    "tekstual",
                    "inferensial",
                    "evaluasi"
                ]
            ]
            .mean(axis=1)
        )

    df_top5 = (
        data_top[
            [
                "nama_siswa",
                "RATA_MAPEL"
            ]
        ]
        .sort_values(
            by="RATA_MAPEL",
            ascending=False
        )
        .head(5)
        .reset_index(drop=True)
    )

    # =====================
    # TABEL MINI DASHBOARD
    # =====================

    # =====================
    # SISWA SIAP TKA
    # =====================

    df_siap = (
        df_kategori[
            df_kategori["HASIL_AKHIR"] == "Siap Tes TKA"
        ][["nama_siswa"]]
        .reset_index(drop=True)
    )

    df_siap.index = (
        df_siap.index + 1
    )

    html_siap = """
    <div style="
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 15px;
        height: 260px;
        overflow-y: auto;
    ">

    <table style="
        width:100%;
        border-collapse:collapse;
        border-spacing:0;
    ">

    <thead>
    <tr>
    <th style="
        position:sticky;
        top:0;
        z-index:9999;
        background:#038031;
        color:white;
        padding:10px;
        text-align:center;
        font-size:16px;
        font-weight:800;
        box-shadow:0 2px 8px rgba(0,0,0,0.5);
    ">
        SISWA SIAP TES TKA
    </th>
    </tr>
    </thead>

    <tbody>
    """

    for nama in df_siap["nama_siswa"]:

        html_siap += (
            '<tr>'
            '<td style="'
            'padding:8px;'
            'color:white;'
            'border-bottom:1px solid rgba(255,255,255,0.08);'
            '">'
            f'{nama}'
            '</td>'
            '</tr>'
        )

    html_siap += """
    </tbody>
    </table>
    </div>
    """

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            html_siap,
            unsafe_allow_html=True
        )

    # =====================
    # SISWA BELUM SIAP TKA
    # =====================

    df_belum = (
        df_kategori[
            df_kategori["HASIL_AKHIR"] == "Belum Siap Tes TKA"
        ][["nama_siswa"]]
        .reset_index(drop=True)
    )

    df_belum.index = (
        df_belum.index + 1
    )

    html_belum = """
    <div style="
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 15px;
        height: 260px;
        overflow-y: auto;
    ">

    <table style="
        width:100%;
        border-collapse:collapse;
        border-spacing:0;
    ">

    <thead>
    <tr>
    <th style="
        position:sticky;
        top:0;
        z-index:9999;
        background:#920000;
        color:white;
        padding:10px;
        text-align:center;
        font-size:16px;
        font-weight:800;
        box-shadow:0 2px 8px rgba(0,0,0,0.5);
    ">
        SISWA BELUM SIAP TES TKA
    </th>
    </tr>
    </thead>

    <tbody>
    """

    for nama in df_belum["nama_siswa"]:

        html_belum += (
            '<tr>'
            '<td style="'
            'padding:8px;'
            'color:white;'
            'border-bottom:1px solid rgba(255,255,255,0.08);'
            '">'
            f'{nama}'
            '</td>'
            '</tr>'
        )

    html_belum += """
    </tbody>
    </table>
    </div>
    """

    with col2:
        st.markdown(
            html_belum,
            unsafe_allow_html=True
        )
    
    # =====================
    # RANKING SUBMAPEL
    # =====================

    html_ranking = """
    <div style="
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 15px;
        height: 260px;
        overflow-y: auto;
    ">

    <table style="
        width:100%;
        border-collapse:collapse;
    ">

    <thead>
    <tr>
    <th colspan="3" style="
        position:sticky;
        top:0;
        z-index:9999;
        background:#1e40af;
        color:white;
        padding:10px;
        text-align:center;
        font-size:16px;
        font-weight:800;
    ">
        RANKING SUB MAPEL (TO TERBARU)
    </th>
    </tr>

    <tr>
    <th style="
        padding:8px;
        color:white;
        text-align:center;
        font-weight:700;
    ">
        NO
    </th>

    <th style="
        padding:8px;
        color:white;
        text-align:center;
        font-weight:700;
    ">
        SUB MAPEL
    </th>

    <th style="
        padding:8px;
        color:white;
        text-align:center;
        font-weight:700;
    ">
        RATA-RATA
    </th>
    </tr>
    </thead>

    <tbody>
    """

    for i, row in df_ranking_sub.iterrows():

        html_ranking += (
            "<tr>"
            f"<td style='padding:8px;color:white;text-align:center'>{i+1}</td>"
            f"<td style='padding:8px;color:white;text-align:center'>{row['Sub Mapel']}</td>"
            f"<td style='padding:8px;color:white;text-align:center'>{row['Rata-rata']}</td>"
            "</tr>"
        )

    html_ranking += """
    </tbody>
    </table>
    </div>
    """

    with col3:
        st.markdown(
            html_ranking,
            unsafe_allow_html=True
        )

    # =====================
    # HTML TOP 5 SISWA
    # =====================

    html_top5 = """
    <div style="
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 15px;
        height: 260px;
        overflow-y: auto;
        overflow-x: auto;
    ">

    <table style="
        min-width:320px;
        border-collapse:collapse;
        border-spacing:0;
    ">

    <thead>
    <tr>
    <th colspan="3" style="
        position:sticky;
        top:0;
        z-index:9999;
        background:#7c3aed;
        color:white;
        padding:10px;
        text-align:center;
        font-size:16px;
        font-weight:800;
    ">
        TOP 5 NILAI SISWA (TO TERBARU)
    </th>
    </tr>

    <tr>
    <th style="
        padding:8px;
        color:white;
        text-align:center;
    ">
        NO
    </th>

    <th style="
        padding:8px;
        color:white;
        text-align:center;
    ">
        NAMA SISWA
    </th>

    <th style="
        padding:8px;
        color:white;
        text-align:center;
    ">
        NILAI
    </th>
    </tr>
    </thead>

    <tbody>
    """

    for i, row in df_top5.iterrows():

        html_top5 += (
            "<tr>"
            f"<td style='padding:8px;color:white;text-align:center'>{i+1}</td>"
            f"""
            <td style="
                padding:8px;
                color:white;
                min-width:170px;
                white-space:nowrap;
            ">
                {row['nama_siswa']}
            </td>
            """
            f"<td style='padding:8px;color:white;text-align:center'>{row['RATA_MAPEL']:.2f}</td>"
            "</tr>"
        )

    html_top5 += """
    </tbody>
    </table>
    </div>
    """

    with col4:
        st.markdown(
            html_top5,
            unsafe_allow_html=True
        )


    st.markdown("<br><br>", unsafe_allow_html=True)

    st.header("Tampilan Data Hasil Try Out TKA Siswa")

    st.markdown("""
    <style>

    /* Selectbox */
    div[data-baseweb="select"] > div {
        background: rgba(255,255,255,0.03) !important;
        border: 1px solid rgba(255,255,255,0.25) !important;
        border-radius: 10px !important;
        color: white !important;
    }

    /* Hover */
    div[data-baseweb="select"] > div:hover {
        border: 1px solid rgba(255,255,255,0.45) !important;
    }

    /* Text */
    div[data-baseweb="select"] span {
        color: white !important;
    }

    /* Label */
    label {
        color: white !important;
        font-weight: 600 !important;
    }

    </style>
    """, unsafe_allow_html=True)

    col_filter1, col_filter2, col_filter3, col_filter4 = st.columns([1,1,1,1])

    with col_filter1:

        filter_nama = st.selectbox(
            "Nama Siswa",
            ["Semua"] +
            sorted(
                df_kategori["nama_siswa"]
                .unique()
                .tolist()
            )
        )

    with col_filter2:

        if mata_pelajaran == "Matematika":

            filter_sub = st.selectbox(
                "Sub Mata Pelajaran",
                [
                    "Semua",
                    "Bilangan",
                    "Aljabar",
                    "Geometri",
                    "Peluang"
                ]
            )

        else:

            filter_sub = st.selectbox(
                "Sub Mata Pelajaran",
                [
                    "Semua",
                    "Tekstual",
                    "Inferensial",
                    "Evaluasi"
                ]
            )

    with col_filter3:

        daftar_batch = sorted(
            data["batch_to"].unique().tolist()
        )

        filter_batch = st.selectbox(
            "Batch TO",
            ["Semua"] + daftar_batch
        )

    with col_filter4:

        filter_hasil = st.selectbox(
            "Kesimpulan Akhir",
            [
                "Semua",
                "Siap Tes TKA",
                "Belum Siap Tes TKA"
            ]
        )


    df_filter = df_kategori.copy()

    if filter_nama != "Semua":
        df_filter = df_filter[
            df_filter["nama_siswa"] == filter_nama
        ]
    
    if filter_hasil != "Semua":
        df_filter = df_filter[
            df_filter["HASIL_AKHIR"] == filter_hasil
        ]

    nama_terfilter = df_filter["nama_siswa"]

    tabel_final = tabel_final.loc[
        nama_terfilter
    ]

    if filter_sub != "Semua":

        tabel_final = tabel_final.loc[
            :,
            tabel_final.columns.get_level_values(0)
            == filter_sub
        ]

    if filter_batch != "Semua":

        kolom_dipilih = []

        for col in tabel_final.columns:

            # kolom biasa
            if not isinstance(col, tuple):
                kolom_dipilih.append(col)
                continue

            level0, level1 = col

            # No dan Nama
            if level0 in ["No", "Nama Siswa"]:
                kolom_dipilih.append(col)

            # hanya batch yg dipilih
            elif level1 == filter_batch:
                kolom_dipilih.append(col)

        tabel_final = tabel_final[kolom_dipilih]

    tabel_final[("HASIL AKHIR", "")] = (
        df_kategori
        .set_index("nama_siswa")
        ["HASIL_AKHIR"]
    )

    # pindahkan nama_siswa jadi kolom biasa
    tabel_final = tabel_final.reset_index()

    # hapus index numerik bawaan
    if "index" in tabel_final.columns:
        tabel_final = tabel_final.drop(
            columns=["index"]
        )

    tabel_final.insert(
        0,
        "No",
        range(1, len(tabel_final) + 1)
    )

    # buat header bertingkat untuk Nama Siswa
    kolom_baru = [
        ("No", ""),
        ("Nama Siswa", "")
    ]

    kolom_baru.extend(
        tabel_final.columns[2:]
    )

    tabel_final.columns = pd.MultiIndex.from_tuples(
        kolom_baru
    )

    # Hilangkan tulisan batch_to
    tabel_final.columns.names = [None, None]

    # Hilangkan angka desimal
    tabel_final = tabel_final.fillna("")
    tabel_final = tabel_final.astype(object)

    for col in tabel_final.columns:
        tabel_final[col] = tabel_final[col].apply(
            lambda x: int(x)
            if isinstance(x, (int, float))
            and str(x) != ""
            else x
            )

    def warna_status(val):

        if str(val) == "Meningkat":
            return """
                background-color: rgba(34, 197, 94, 0.25);
                color: #bbf7d0;
                font-weight: bold;
            """

        elif str(val) == "Menurun":
            return """
                background-color: rgba(239, 68, 68, 0.25);
                color: #fecaca;
                font-weight: bold;
            """

        return ""
    
    def warna_kategori(val):

        if str(val) == "Sangat Baik":
            return """
                background-color: rgba(34, 197, 94, 0.25);
                color: #86efac;
                font-weight: bold;
            """

        elif str(val) == "Baik":
            return """
                background-color: rgba(163, 230, 53, 0.25);
                color: #d9f99d;
                font-weight: bold;
            """

        elif str(val) == "Kurang":
            return """
                background-color: rgba(249, 115, 22, 0.25);
                color: #fdba74;
                font-weight: bold;
            """

        elif str(val) == "Sangat Kurang":
            return """
                background-color: rgba(239, 68, 68, 0.25);
                color: #fca5a5;
                font-weight: bold;
            """

        return ""

    styled_table = tabel_final.style

    # cek STATUS
    if "STATUS" in tabel_final.columns.get_level_values(1):
        styled_table = styled_table.map(
            warna_status,
            subset=pd.IndexSlice[:, pd.IndexSlice[:, "STATUS"]]
        )

    # cek KATEGORI
    if "KATEGORI" in tabel_final.columns.get_level_values(1):
        styled_table = styled_table.map(
            warna_kategori,
            subset=pd.IndexSlice[:, pd.IndexSlice[:, "KATEGORI"]]
        )

    # LANJUTKAN STYLING
    styled_table = styled_table.set_properties(**{
        "text-align": "center",
        "font-weight": "bold",
        "color": "#FFFFFF"
    }).set_table_styles([
        {
            "selector": "th.col_heading",
            "props": [
                ("background-color", "#1E293B"),
                ("color", "#FFFFFF"),
                ("font-size", "15px"),
                ("font-weight", "bold"),
                ("text-align", "center"),
                ("white-space", "nowrap")
            ]
        },
        {
            "selector": "th.index_name",
            "props": [
                ("background-color", "transparent"),
                ("color", "#FFFFFF"),
                ("font-size", "14px"),
                ("font-weight", "bold")
            ]
        },
        {
            "selector": "th.row_heading",
            "props": [
                ("background-color", "transparent"),
                ("color", "#FFFFFF"),
                ("font-size", "14px"),
                ("font-weight", "normal")
            ]
        },
        {
            "selector": "td",
            "props": [
                ("font-size", "14px"),
                ("font-weight", "normal"),
                ("text-align", "center"),
                ("white-space", "nowrap")
            ]
        }
    ])   

    html_table = (
        styled_table
        .hide(axis="index")
        .to_html()
    )

    html_table = html_table.replace(
        '<th colspan="1" class="col_heading level0 col1" >Nama Siswa</th>',
        '<th colspan="1" class="col_heading level0 col1" style="width:180px;">Nama Siswa</th>'
    )

    st.markdown(
        f"""
        <div style="
            overflow-x:auto;
            width:100%;
        ">
            {html_table}
        """,
        unsafe_allow_html=True
    )

    buffer = io.BytesIO()

    tabel_download = tabel_final.copy()

    tabel_download.columns = [
        f"{a}_{b}" if b != "" else str(a)
        for a, b in tabel_download.columns
    ]

    with pd.ExcelWriter(
        buffer,
        engine="openpyxl"
    ) as writer:

        tabel_download.to_excel(
            writer,
            sheet_name="Hasil TO",
            index=False
        )

    st.download_button(
        label="Download Data",
        data=buffer.getvalue(),
        file_name="hasil_tryout.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )