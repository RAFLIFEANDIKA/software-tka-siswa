import streamlit as st
import base64
import pandas as pd
import os
from sqlalchemy import create_engine

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
    "SUPABASE_DATABASE_URL"
)

engine = create_engine(
    DATABASE_URL
)

# =========================
# SIDEBAR
# =========================

with st.sidebar:

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
                        "nilai_tryout",
                        engine,
                        if_exists="append",
                        index=False
                    )

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

if st.session_state.login_status:

    st.markdown("<br>", unsafe_allow_html=True)

    st.header("Tampilan Data Hasil Try Out TKA Siswa")

    data = pd.read_sql(
        """
        SELECT *
        FROM nilai_tryout
        """,
        engine
    )

    mata_pelajaran = st.segmented_control(
        "Pilih Mata Pelajaran",
        [
            "Matematika",
            "Bahasa Indonesia"
        ],
        default="Matematika"
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

    for sub in sub_mapel:

        pivot = data.pivot_table(
            index="nama_siswa",
            columns="batch_to",
            values=sub
        )

        pivot.columns = pd.MultiIndex.from_product(
            [[sub.title()], pivot.columns]
        )

        hasil.append(pivot)

    tabel_final = pd.concat(
        hasil,
        axis=1
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

    styled_table = (
        tabel_final.style
        .set_properties(**{
            "text-align": "center",
            "font-weight": "bold",
            "color": "#FFFFFF"
        })

        .set_table_styles([
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
                    ("background-color", "transparent"),
                    ("color", "#FFFFFF"),
                    ("font-size", "14px"),
                    ("font-weight", "normal"),
                    ("text-align", "center"),
                    ("white-space", "nowrap")
                ]
            }
        ])
    )

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