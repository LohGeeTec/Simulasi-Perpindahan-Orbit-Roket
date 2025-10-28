# ==========================================================
# PERPINDAHAN ORBIT ROKET (dengan opsi tambah anggaran berulang)
# Revisi final: validasi input > 0 untuk R1, R2, massa_kosong, anggaran
#               + batas wajar radius orbit: [R_earth, 1_500_000_000] meter
# ==========================================================

## --- KAMUS (disusun ulang agar lebih mudah dibaca) ---
# nama_bahan_bakar[]     : array/list nama jenis bahan bakar yang dapat digunakan
# isp_bahan_bakar[]      : array nilai specific impulse (Isp) tiap bahan bakar (s)
# harga_bahan_bakar[]    : array harga per satuan tiap bahan bakar ($)
# jumlah_bahan_bakar     : jumlah jenis bahan bakar (integer)
# massa_bahan_bakar[]    : array massa bahan bakar (kg) yang diperlukan per jenis
# biaya_bahan_bakar[]    : array perkiraan biaya (USD) per jenis bahan bakar
# massa_kosong           : massa roket tanpa bahan bakar (kg)
# anggaran               : total anggaran yang dimiliki pengguna (USD)
# jari_orbit_awal (R1)   : jari-jari orbit awal (meter) — dari pusat Bumi
# jari_orbit_akhir (R2)  : jari-jari orbit tujuan (meter) — dari pusat Bumi
# kecepatan_R1           : kecepatan orbit pada R1 (m/s)
# deltaV1                : ΔV tahap 1 (m/s)
# deltaV2                : ΔV tahap 2 (m/s)
# kecepatan_buang        : effective exhaust velocity (~ Isp * g0) (m/s)
# daftar_mampu_beli[]    : daftar indeks bahan bakar yang bisa dibeli dengan anggaran
# jumlah_mampu_beli      : panjang daftar_mampu_beli (integer)
# indeks / i / j / k     : variabel indeks untuk loop
# pilihan / dipilih      : input pilihan pengguna (string / int)
# sisa_uang              : sisa anggaran setelah pembelian (USD)
# jari_orbit_maks (R3)   : orbit maksimum yang dapat dicapai jika anggaran terbatas (meter)
# batas_loop             : pembatas jumlah iterasi dalam loop perhitungan
# exp1 / exp2            : nilai eksp (e ** (-|ΔV| / ve)) pada iterasi
# ==========================================================

# Konstanta
e = 2.71828
G = 6.67430 * (10 ** -11)
massa_bumi = 5.972 * (10 ** 24)
gravitasi_bumi = 9.80665

# Batas wajar radius orbit (meter)
RADIUS_BUMI = 6_371_000            # radius rata-rata Bumi (m)
RADIUS_ATAS_MAX = 1_500_000_000    # batas atas wajar (m) — ~1.5e9 m

# Daftar bahan bakar
nama_bahan_bakar = [
    "RP-1 / LOX",
    "LH2 / LOX",
    "CH4 / LOX (Metana)",
    "Hypergolic (MMH/UDMH)",
    "Monopropellant (Hydrazine)",
    "Solid propellant",
    "Electric (Xenon ion/Hall)"
]

isp_bahan_bakar = [330, 450, 360, 320, 220, 270, 3000]
harga_bahan_bakar = [3.0, 20.0, 5.0, 300.0, 50.0, 6.0, 20000.0]

# Hitung jumlah bahan bakar 
jumlah_bahan_bakar = 0
for _ in nama_bahan_bakar:
    jumlah_bahan_bakar += 1

# --- Informasi referensi jari-orbit (semua sebagai jari-jari dari pusat Bumi, dalam meter) ---
print("\nReferensi jari-jari orbit (dari pusat Bumi), nilai perkiraan:")
print("  • Radius rata-rata Bumi  ≈", RADIUS_BUMI, "m")
print("  • LEO (Low Earth Orbit) contoh jari-jari:  (R = 6_371_000 + ketinggian di atas permukaan)")
print("      - 160 km  → R ≈ 6_531_000 m")
print("      - 400 km (ISS) → R ≈ 6_771_000 m")
print("      - 2000 km → R ≈ 8_371_000 m")
print("  • MEO (contoh GPS) → altitude ≈ 20_200 km → R ≈ 26_571_000 m")
print("  • GEO (geostationary) → R ≈ 42_164_000 m (altitude ≈ 35_786 km di atas permukaan)")
print("  • Batas wajar input radius orbit: antara", RADIUS_BUMI, "m dan", RADIUS_ATAS_MAX, "m\n")

# --- Validasi input R1 (harus > 0 dan dalam batas wajar) ---
while True:
    try:
        jari_orbit_awal = float(input("Masukkan jari-jari orbit awal R1 (m) [> 0 dan >= radius Bumi]: "))
        if jari_orbit_awal <= 0:
            print("Input tidak valid: R1 harus lebih besar dari 0. Silakan coba lagi.")
            continue
        if jari_orbit_awal < RADIUS_BUMI:
            print("Input tidak valid: R1 tidak boleh lebih kecil dari radius Bumi (", RADIUS_BUMI, "m). Coba lagi.")
            continue
        if jari_orbit_awal > RADIUS_ATAS_MAX:
            print("Input tidak valid: R1 terlalu besar (maks", RADIUS_ATAS_MAX, "m). Coba lagi.")
            continue
        break
    except:
        print("Input tidak valid: masukkan angka numerik (mis. 6771000). Coba lagi.")

# --- Validasi input R2 (harus > 0 dan dalam batas wajar) ---
while True:
    try:
        jari_orbit_akhir = float(input("Masukkan jari-jari orbit akhir R2 (m) [> 0 dan dalam batas wajar]: "))
        if jari_orbit_akhir <= 0:
            print("Input tidak valid: R2 harus lebih besar dari 0. Silakan coba lagi.")
            continue
        if jari_orbit_akhir < RADIUS_BUMI:
            print("Input tidak valid: R2 tidak boleh lebih kecil dari radius Bumi (", RADIUS_BUMI, "m). Coba lagi.")
            continue
        if jari_orbit_akhir > RADIUS_ATAS_MAX:
            print("Input tidak valid: R2 terlalu besar (maks", RADIUS_ATAS_MAX, "m). Coba lagi.")
            continue
        break
    except:
        print("Input tidak valid: masukkan angka numerik (mis. 42164000). Coba lagi.")

# Jika R2 < R1 beri tahu bahwa roket akan menurunkan orbit dan perhitungan akan sama namun burn 'ke belakang'
if jari_orbit_akhir < jari_orbit_awal:
    print("\nCatatan: R2 < R1 — ini berarti manuver menurunkan orbit.")
    print("Perhitungan bahan bakar & biaya akan dilakukan sama seperti kasus kenaikan orbit,")
    print("tetapi arah pembakaran (prograde/retrograde) berbeda (burn 'ke belakang' untuk menurunkan orbit).\n")
elif jari_orbit_akhir == jari_orbit_awal:
    print("\nCatatan: R2 = R1 — tidak perlu manuver menaikkan atau menurunkan orbit.\n")
    quit()
else:
    print("\nCatatan: R2 > R1 — ini berarti manuver menaikkan orbit.\n")

# Saat diminta input massa roket kosong, tampilkan referensi massa beberapa roket populer (perkiraan)
print("Referensi massa roket kosong:")
print("  • Falcon 9 ≈ 22_800 kg")
print("  • Rocket Lab Electron ≈ 950 kg")
print("  • Soyuz ≈ 6_545 kg")
print("  • Ariane 5 ≈ 14_700 kg")
print("  • Starship ≈ 100_000 kg\n")

# --- Validasi input massa_kosong (harus > 0) ---
while True:
    try:
        massa_kosong = float(input("Masukkan massa roket kosong (kg) [> 0]: "))
        if massa_kosong <= 0:
            print("Input tidak valid: massa roket kosong harus > 0. Silakan coba lagi.")
            continue
        break
    except:
        print("Input tidak valid: masukkan angka numerik (mis. 22800). Coba lagi.")

# Hitung ΔV (gunakan tanda sesuai rumus; magnitude dipakai untuk exponent)
kecepatan_R1 = ((G * massa_bumi) / jari_orbit_awal) ** 0.5
deltaV1 = kecepatan_R1 * (((2 * jari_orbit_akhir) / (jari_orbit_awal + jari_orbit_akhir)) ** 0.5 - 1)
deltaV2 = kecepatan_R1 * ((jari_orbit_awal / jari_orbit_akhir) ** 0.5) * (1 - ((2 * jari_orbit_awal) / (jari_orbit_awal + jari_orbit_akhir)) ** 0.5)

print("\nRingkasan ΔV (nilai positif = magnitudo ΔV):")
print("Kecepatan di orbit awal =", round(kecepatan_R1, 2), "m/s")
print("ΔV1 =", round(deltaV1, 2), "m/s ; ΔV2 =", round(deltaV2, 2), "m/s\n")

# Siapkan array kosong manual
massa_bahan_bakar = [0] * jumlah_bahan_bakar
biaya_bahan_bakar = [0] * jumlah_bahan_bakar

# Perhitungan utama — hitung kebutuhan bahan bakar dan biaya tiap propellant
i = 0
while i < jumlah_bahan_bakar:
    isp = isp_bahan_bakar[i]
    harga = harga_bahan_bakar[i]
    kecepatan_buang = isp * gravitasi_bumi

    # gunakan magnitude ΔV untuk perhitungan exponent agar tidak menghasilkan exp>1
    abs_dV1 = deltaV1 if deltaV1 >= 0 else -deltaV1
    abs_dV2 = deltaV2 if deltaV2 >= 0 else -deltaV2

    massa_total = massa_kosong + 1000.0
    j = 0
    while j < 20:
        exp1 = e ** (-abs_dV1 / kecepatan_buang)
        exp2 = e ** (-abs_dV2 / kecepatan_buang)
        bahan_bakar_tahap1 = massa_total * (1 - exp1)
        bahan_bakar_tahap2 = (massa_total - bahan_bakar_tahap1) * (1 - exp2)
        massa_total = massa_kosong + bahan_bakar_tahap1 + bahan_bakar_tahap2
        j += 1

    # Pastikan non-negatif (safety)
    if bahan_bakar_tahap1 < 0:
        bahan_bakar_tahap1 = 0.0
    if bahan_bakar_tahap2 < 0:
        bahan_bakar_tahap2 = 0.0

    total_bahan_bakar = bahan_bakar_tahap1 + bahan_bakar_tahap2
    if total_bahan_bakar < 0:
        total_bahan_bakar = 0.0

    total_biaya = total_bahan_bakar * harga
    if total_biaya < 0:
        total_biaya = 0.0

    massa_bahan_bakar[i] = total_bahan_bakar
    biaya_bahan_bakar[i] = total_biaya

    # Cetak info propellant (ini juga dijadikan panduan saat meminta anggaran)
    print(">>>", nama_bahan_bakar[i])
    print("   Isp (s):", isp, "| Kecepatan buang (m/s) ≈", round(kecepatan_buang, 2))
    print("   Kebutuhan bahan bakar (kg):", round(total_bahan_bakar, 2))
    print("   Biaya perkiraan ($):", round(total_biaya, 2))
    i += 1

# --- Sekarang minta input anggaran, user sudah melihat detail tiap propellant ---
print("\nSekarang masukkan total budget (USD). Gunakan informasi biaya di atas sebagai panduan.")

# --- Validasi input anggaran (harus > 0) ---
while True:
    try:
        anggaran = float(input("Masukkan total budget ($) [> 0]: "))
        if anggaran <= 0:
            print("Input tidak valid: anggaran harus lebih besar dari 0. Silakan masukkan jumlah positif.")
            continue
        break
    except:
        print("Input tidak valid: masukkan angka numerik (mis. 60000). Coba lagi.")

# Pengecekan anggaran awal
print("\n=== Pengecekan anggaran ===")
daftar_mampu_beli = []
i = 0
while i < jumlah_bahan_bakar:
    # hanya tambahkan bila biaya terhitung (>=0) dan anggaran cukup
    if biaya_bahan_bakar[i] >= 0 and anggaran >= biaya_bahan_bakar[i]:
        daftar_mampu_beli += [i]
    i += 1

# Hitung jumlah bahan bakar yang mampu dibeli 
jumlah_mampu_beli = 0
for _ in daftar_mampu_beli:
    jumlah_mampu_beli += 1

# Jika ada yang dapat dibeli, biarkan memilih (dengan validasi ketat)
if jumlah_mampu_beli > 0 and anggaran > 0:
    print("Anda punya cukup anggaran untuk mencapai orbit akhir dengan bahan bakar berikut:")
    k = 0
    while k < jumlah_mampu_beli:
        indeks = daftar_mampu_beli[k]
        print("  [", indeks, "]", nama_bahan_bakar[indeks], "- biaya:", round(biaya_bahan_bakar[indeks], 2), "$")
        k += 1

    # Validasi pilihan sampai benar
    valid = False
    while not valid:
        pilihan = input("Masukkan indeks bahan bakar pilihan: ")
        p = 0
        valid = False
        while p < jumlah_mampu_beli:
            if pilihan == str(daftar_mampu_beli[p]):
                valid = True
                dipilih = daftar_mampu_beli[p]
                break
            p += 1
        if not valid:
            print("Pilihan tidak valid. Silakan coba lagi.")

    sisa_uang = anggaran - biaya_bahan_bakar[dipilih]
    print("✅ Anda memilih:", nama_bahan_bakar[dipilih])
    print("   Biaya:", round(biaya_bahan_bakar[dipilih], 2), "$")
    print("   Sisa uang:", round(sisa_uang, 2), "$")

else:
    # Tidak cukup — tampilkan R3 untuk anggaran sekarang
    print("Maaf — anggaran TIDAK cukup untuk mencapai orbit akhir dengan semua bahan bakar.")
    print("Menampilkan orbit maksimum (R3 perkiraan) untuk setiap bahan bakar dengan anggaran sekarang:")

    i = 0
    while i < jumlah_bahan_bakar:
        isp = isp_bahan_bakar[i]
        harga = harga_bahan_bakar[i]
        kecepatan_buang = isp * gravitasi_bumi

        jari_orbit_maks = jari_orbit_awal
        langkah = jari_orbit_awal * 0.05
        if langkah < 1000:
            langkah = 1000.0

        orbit_mampu_beli_terakhir = jari_orbit_awal
        batas_loop = 0
        while batas_loop < 2000:
            kecepatan_R1_temp = ((G * massa_bumi) / jari_orbit_awal) ** 0.5
            deltaV1_temp = kecepatan_R1_temp * (((2 * jari_orbit_maks) / (jari_orbit_awal + jari_orbit_maks)) ** 0.5 - 1)
            deltaV2_temp = kecepatan_R1_temp * ((jari_orbit_awal / jari_orbit_maks) ** 0.5) * (1 - ((2 * jari_orbit_awal) / (jari_orbit_awal + jari_orbit_maks)) ** 0.5)

            massa_total_temp = massa_kosong + 1000.0
            dalam = 0
            while dalam < 10:
                # gunakan magnitude ΔV di sini juga
                abs_dV1_temp = deltaV1_temp if deltaV1_temp >= 0 else -deltaV1_temp
                abs_dV2_temp = deltaV2_temp if deltaV2_temp >= 0 else -deltaV2_temp

                exp1 = e ** (-abs_dV1_temp / kecepatan_buang)
                exp2 = e ** (-abs_dV2_temp / kecepatan_buang)
                bahan_bakar1_temp = massa_total_temp * (1 - exp1)
                bahan_bakar2_temp = (massa_total_temp - bahan_bakar1_temp) * (1 - exp2)
                massa_total_temp = massa_kosong + bahan_bakar1_temp + bahan_bakar2_temp
                dalam += 1

            total_bahan_temp = bahan_bakar1_temp + bahan_bakar2_temp
            if total_bahan_temp < 0:
                total_bahan_temp = 0.0
            total_biaya_temp = total_bahan_temp * harga

            if total_biaya_temp <= anggaran:
                orbit_mampu_beli_terakhir = jari_orbit_maks
                jari_orbit_maks += langkah
            else:
                break

            batas_loop += 1

        print("- Dengan", nama_bahan_bakar[i], "orbit maksimum R3 ≈", round(orbit_mampu_beli_terakhir, 2), "m (perkiraan)")
        i += 1

    # Loop: beri pengguna opsi menambah anggaran berulang kali sampai ada yang cukup atau pengguna memilih berhenti
    while True:
        tambah = input("Apakah Anda ingin menambahkan anggaran? (y/n): ")
        if tambah.lower() == 'y':
            tambahan_str = input("Masukkan jumlah tambahan anggaran ($): ")

            # Validasi manual string angka (hanya digit dan maksimal satu titik desimal, tidak negatif)
            valid_input = True
            titik = 0
            # kosong tidak valid
            kosong_flag = True
            for ch in tambahan_str:
                kosong_flag = False
                if ch == '.':
                    titik += 1
                elif ch >= '0' and ch <= '9':
                    pass
                else:
                    valid_input = False
            if kosong_flag:
                valid_input = False
            if titik > 1:
                valid_input = False

            if not valid_input:
                print("Input jumlah tambahan tidak valid (masukkan angka positif, mis. 1500.50). Coba lagi.")
                # kembali ke awal loop untuk menanyakan lagi
            else:
                # konversi aman karena sudah tervalidasi
                tambahan = float(tambahan_str)
                if tambahan <= 0:
                    print("Jumlah tambahan harus lebih dari 0. Silakan coba lagi.")
                else:
                    anggaran = anggaran + tambahan
                    print("Anggaran baru Anda: $", round(anggaran, 2))

                    # Update daftar_mampu_beli berdasarkan biaya yang sudah dihitung
                    daftar_mampu_beli = []
                    i = 0
                    while i < jumlah_bahan_bakar:
                        if biaya_bahan_bakar[i] >= 0 and anggaran >= biaya_bahan_bakar[i]:
                            daftar_mampu_beli += [i]
                        i += 1

                    jumlah_mampu_beli = 0
                    for _ in daftar_mampu_beli:
                        jumlah_mampu_beli += 1

                    if jumlah_mampu_beli > 0:
                        print("Dengan anggaran baru, Anda bisa mencapai orbit akhir menggunakan:")
                        k = 0
                        while k < jumlah_mampu_beli:
                            indeks = daftar_mampu_beli[k]
                            print("  [", indeks, "]", nama_bahan_bakar[indeks], "- biaya:", round(biaya_bahan_bakar[indeks], 2), "$")
                            k += 1

                        # Pilihan dengan validasi ketat dan pengulangan sampai valid
                        valid = False
                        while not valid:
                            pilihan = input("Masukkan indeks bahan bakar pilihan (angka di dalam [ ]): ")
                            p = 0
                            valid = False
                            while p < jumlah_mampu_beli:
                                if pilihan == str(daftar_mampu_beli[p]):
                                    valid = True
                                    dipilih = daftar_mampu_beli[p]
                                    break
                                p += 1
                            if not valid:
                                print("Pilihan tidak valid. Silakan coba lagi.")

                        sisa_uang = anggaran - biaya_bahan_bakar[dipilih]
                        print("✅ Anda memilih:", nama_bahan_bakar[dipilih])
                        print("   Biaya:", round(biaya_bahan_bakar[dipilih], 2), "$")
                        print("   Sisa uang:", round(sisa_uang, 2), "$")
                        break  # keluar dari loop tambah anggaran karena sudah selesai

                    else:
                        print("Meski sudah menambah, anggaran masih belum cukup untuk mencapai orbit akhir.")
                        print("Menampilkan orbit maksimum (R3 perkiraan) untuk setiap bahan bakar dengan anggaran baru:")

                        i = 0
                        while i < jumlah_bahan_bakar:
                            isp = isp_bahan_bakar[i]
                            harga = harga_bahan_bakar[i]
                            kecepatan_buang = isp * gravitasi_bumi

                            jari_orbit_maks = jari_orbit_awal
                            langkah = jari_orbit_awal * 0.05
                            if langkah < 1000:
                                langkah = 1000.0

                            orbit_mampu_beli_terakhir = jari_orbit_awal
                            batas_loop = 0
                            while batas_loop < 2000:
                                kecepatan_R1_temp = ((G * massa_bumi) / jari_orbit_awal) ** 0.5
                                deltaV1_temp = kecepatan_R1_temp * (((2 * jari_orbit_maks) / (jari_orbit_awal + jari_orbit_maks)) ** 0.5 - 1)
                                deltaV2_temp = kecepatan_R1_temp * ((jari_orbit_awal / jari_orbit_maks) ** 0.5) * (1 - ((2 * jari_orbit_awal) / (jari_orbit_awal + jari_orbit_maks)) ** 0.5)

                                massa_total_temp = massa_kosong + 1000.0
                                dalam = 0
                                while dalam < 10:
                                    abs_dV1_temp = deltaV1_temp if deltaV1_temp >= 0 else -deltaV1_temp
                                    abs_dV2_temp = deltaV2_temp if deltaV2_temp >= 0 else -deltaV2_temp

                                    exp1 = e ** (-abs_dV1_temp / kecepatan_buang)
                                    exp2 = e ** (-abs_dV2_temp / kecepatan_buang)
                                    bahan_bakar1_temp = massa_total_temp * (1 - exp1)
                                    bahan_bakar2_temp = (massa_total_temp - bahan_bakar1_temp) * (1 - exp2)
                                    massa_total_temp = massa_kosong + bahan_bakar1_temp + bahan_bakar2_temp
                                    dalam += 1

                                total_bahan_temp = bahan_bakar1_temp + bahan_bakar2_temp
                                if total_bahan_temp < 0:
                                    total_bahan_temp = 0.0
                                total_biaya_temp = total_bahan_temp * harga

                                if total_biaya_temp <= anggaran:
                                    orbit_mampu_beli_terakhir = jari_orbit_maks
                                    jari_orbit_maks += langkah
                                else:
                                    break

                                batas_loop += 1

                            print("- Dengan", nama_bahan_bakar[i], "orbit maksimum R3 ≈", round(orbit_mampu_beli_terakhir, 2), "m (perkiraan)")
                            i += 1

                        # kembali ke awal loop tambah anggaran untuk memberi opsi menambah lagi
        elif tambah.lower() == 'n':
            print("Anda memilih untuk tidak menambah anggaran. Misi dibatalkan. Program selesai.")
            break
        else:
            print("Input tidak dikenali. Masukkan 'y' atau 'n'.")

print("\n=== Program selesai ===")