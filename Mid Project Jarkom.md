Sifat : Kelompok 3–4 orang
Deadline : Minggu, 1 November 2026, pukul 23.59 WIB
Jadwal Demo : TBA (minggu ke-10)

Pemerintah Kota Surabaya membangun jaringan Smart City. Rancangan pengalamatan kalian hitung saat UTS dengan dua cara: VLSM dan CIDR. Pilih salah satu skema, lalu bangun jaringan tersebut di Cisco Packet Tracer, lengkap dengan routing, layanan internet, dan layanan aplikasi yang dibutuhkan oleh sebuah kota cerdas.

Catatan: Kebutuhan host untuk setiap LAN dan pengalamatannya akan diberikan saat UTS. Kalian bisa berlatih terlebih dahulu dengan mencoba merakit topologi dan melakukan konfigurasi menggunakan alamat sementara.
![Referensi topologi backbone L1–L6 dari catatan UTS Kelompok 9](./UTS%20Tulis/WhatsApp%20Image%202026-10-23%20at%2015.45.30%20%281%29.jpeg)

*Lampiran gambar soal asli tidak tersedia dalam repository. Gambar di atas adalah salinan topologi pada catatan UTS.*

## Pengalamatan Jaringan

Seluruh subnet menggunakan hasil dari UTS setiap kelompok. Gateway setiap LAN adalah alamat host pertama. Berikut adalah alamat tambahan yang tidak dihitung saat UTS (K = nomor kelompok):
|No.|Keperluan|Alamat|
|---|---|---|
|1|Link R-PUSAT ke R-ISP|203.0.113.(4 × K)/30|
|2|Server internet|8.8.8.0/24<br><br>Server 8.8.8.8, gateway 8.8.8.1 di R-ISP|
|3|Tunnel GRE|192.168.K.0/30<br><br>Tunnel R-PUSAT .1, tunnel R-PELABUHAN .2|

## Soal

1. Perancangan topologi (10)

- Bangun topologi di Cisco Packet Tracer sesuai skema yang kalian pilih (VLSM atau CIDR).
  - Hubungan antar-router (backbone, link L1–L6), termasuk R-ISP dan server 8.8.8.8, wajib mengikuti Gambar 1.
  - Desain setiap lokasi silakan dirancang sendiri, mencakup susunan switch, jenis perangkat yang dipasang (PC, perangkat mobile, atau server), media link (kabel atau wireless), serta penambahan port pada router. Tuliskan pertimbangan dan alasannya dalam dokumentasi.
  - Cukup pasang 1 perangkat perwakilan di setiap LAN. Perhitungan subnet tetap menggunakan jumlah host penuh.
- Ganti nama bawaan setiap perangkat (misalnya Router0, Switch1, PC2) dengan nama yang menunjukkan tempatnya, seperti R-PUSAT, SW-BALAIKOTA, atau PC-CCTV-KOTA.
- Tambahkan label di setiap LAN yang berisi nama subnet, Network ID/prefix, dan jumlah host.

2. Tabel subnetting (5)

- Menggunakan VLSM dan CIDR, buat tabel di spreadsheet yang berisi nama subnet, network ID, prefix, rentang host, alamat broadcast, dan gateway untuk setiap subnet sesuai dengan lembar jawaban UTS.
- Kesalahan hitung di UTS boleh diperbaiki, tetapi perbaikan wajib dicatat dalam tabel revisi: subnet, jawaban di UTS, perbaikan, dan alasan kesalahannya. Perubahan yang tidak dicatat dianggap sebagai “ketidakkonsistenan”.

3. Static routing (15)

- Seluruh LAN dapat saling berkomunikasi hanya dengan static route (dan default route untuk arah keluar).
- Default route hanya boleh mengarah ke router di atasnya / keluar. Misalnya, default route R-DC ke R-PUSAT, R-PELABUHAN ke R-UTARA, dan R-PUSAT ke R-ISP.
- R-PUSAT dan R-UTARA wajib memiliki static route ke jaringan di bawahnya (ke dalam):
  - R-PUSAT: ke semua LAN milik R-DC, R-UTARA, R-PELABUHAN, R-SELATAN, R-TIMUR, dan R-BARAT.
  - R-UTARA: ke semua LAN milik R-PELABUHAN.

4. DHCP (10)

- Interface router dan seluruh server menggunakan IP statis.
- Perangkat pengguna mendapat IP dinamis secara otomatis, lengkap dengan gateway dan DNS server (soal 8), tanpa bentrok dengan alamat IP statis.
- Khusus untuk subnet CCTV Kota (subnet R-DC) mendapatkan alamat dari server DHCP di LAN Server dan Storage DC, bukan dari router.

5. NAT (5). Seluruh host dapat mengakses server 8.8.8.8 menggunakan satu IP publik milik R-PUSAT. R-ISP tidak boleh memiliki rute ke alamat privat internal.
6. Tunnel GRE (10)

- Bangun tunnel GRE antara R-PUSAT dan R-PELABUHAN.
- Lalu lintas antara subnet Balai Kota dan subnet Pelabuhan harus melewati tunnel.
- Jelaskan dalam dokumentasi mengapa router memilih jalur tunnel dibandingkan jalur lain ke pelabuhan, dan mengapa GRE saja tidak mengenkripsi data.
- Bonus (+5): Buat lalu lintas di dalam tunnel terenkripsi dengan IPsec.

7. Dynamic routing OSPF (10). Kerjakan di file terpisah (copy file utama).

- Tambahkan link baru (cadangan) L7 antara R-DC dan R-UTARA. Berikan alamat yang belum digunakan.
- Ganti seluruh static route antar-router dengan OSPF. Ketentuannya:
  - Router tidak mengirim pesan OSPF ke arah LAN pengguna.
  - Default route ke internet hanya dikonfigurasi di R-PUSAT, dan router lain mendapatkannya secara otomatis melalui OSPF.

- Jika salah satu link backbone putus, konektivitas harus pulih secara otomatis melalui jalur lain.

8. Layanan aplikasi Smart City (10). Gunakan domain internal

k<nomor kelompok>.smartcity.lab.

a.          DNS di LAN Server dan Storage DC. Nama www, ftp, dan mail dapat diakses dari seluruh wilayah.

b.          Web di LAN Server Balai Kota, berupa halaman "Portal Smart City Surabaya" yang mencantumkan nomor kelompok dan dapat dibuka dengan nama domain dari semua wilayah.

c.          FTP di LAN Server dan Storage DC sebagai penyimpanan rekaman CCTV, dengan akun login. Perangkat di LAN CCTV Kota dapat mengunggah file ke sana.

d.          Email antarpegawai. Pengguna di Balai Kota dan Pelabuhan dapat saling mengirim dan menerima email.

9. Demo (25)

a.          Uji 1, kelompok (10): dosen atau asisten menjalankan test case untuk soal 1–8 dan menanyakan konfigurasi kalian secara singkat. (15 menit)

b.          Uji 2, individu (15): dosen atau asisten merusak konfigurasi menjadi 3 skenario kesalahan. Setiap anggota, dengan laptop masing-masing, harus menemukan, memperbaiki, dan menjelaskan satu kesalahan dalam 10 menit.

Output yang Dikumpulkan

- File Packet Tracer:

- K<nomor kelompok>\_VLSM.pkt / K<nomor kelompok>\_CIDR.pkt
- K<nomor kelompok>\_VLSM_OSPF.pkt / K<nomor kelompok>\_CIDR_OSPF.pkt: file OSPF (soal 7).

- Spreadsheet (.xlsx) berisi tabel VLSM dan CIDR dari UTS, supernet per router (untuk CIDR), serta tabel revisi (jika ada perbaikan dibanding UTS, beserta alasannya).
- Dokumentasi (link GitHub Markdown):

- Gambar topologi (screenshot) beserta alasan pemilihan skema (CIDR / VLSM).
- Penjelasan desain topologi.
- Penjelasan semua konfigurasi.
- Bukti pengujian mandiri untuk setiap soal (screenshot).

Semua file di atas dikompres dalam satu file .ZIP dengan format nama:

MidProject `Jarkom_K<nomor kelompok>_<3 angka NRP terakhir 1>_<2>_<3>.ZIP`

## Rubrik Penilaian

| No. | Kriteria                                                                                           | Bobot |
| --- | -------------------------------------------------------------------------------------------------- | ----- |
| 1   | Perancangan topologi: backbone sesuai Gambar 1, desain per LAN, penamaan dan label lengkap         | 10    |
| 2   | Tabel subnetting: sesuai lembar jawaban UTS, revisi tercatat beserta alasannya                     | 5     |
| 3   | Static routing: rute sesuai skema dan aturan default route, seluruh LAN terhubung                  | 15    |
| 4   | DHCP: perangkat pengguna mendapat alamat, gateway, dan DNS; CCTV Kota dilayani server DHCP di DC   | 10    |
| 5   | NAT: semua wilayah dapat mengakses 8.8.8.8, R-ISP tanpa rute ke blok privat                        | 5     |
| 6   | Tunnel GRE: lalu lintas Balai Kota ke Pelabuhan lewat tunnel, penjelasan benar (bonus IPsec +5)    | 10    |
| 7   | Dynamic routing OSPF: L7 link cadangan, OSPF berjalan, konektivitas pulih otomatis saat link putus | 10    |
| 8   | Layanan aplikasi: DNS, web, FTP, dan email berjalan dari semua wilayah                             | 10    |
| 9   | Demo Uji 1 (kelompok): test case berhasil dan tanya jawab dijawab dengan benar                     | 10    |
| 10  | Demo Uji 2 (individu): kesalahan berhasil ditemukan, diperbaiki, dan dijelaskan                    | 15    |
|     | Total                                                                                              | 100   |
