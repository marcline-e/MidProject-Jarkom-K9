1. Goals Anggota C
   Fokus utama: Soal 6 (GRE + IPsec), Soal 7 (OSPF + L7), Soal 8 (Layanan Aplikasi Smart City), dan Demo Uji 1 & 2.
1. Layanan Aplikasi Smart City (Soal 8 - 10 Poin):

- Domain k9.smartcity.lab aktif via DNS Server (LAN Server & Storage DC). Record: www, ftp, mail.
- Web Server (LAN Balai Kota): Page HTML "Portal Smart City Surabaya" + Kelompok 9 bisa dibuka dari seluruh LAN.
- FTP Server (LAN Server DC): User auth aktif, upload rekaman CCTV dari PC LAN CCTV berhasil.
- Email Server: Domain mail aktif, user Balai Kota & Pelabuhan saling kirim-terima mail.

2. GRE Tunnel & Bonus IPsec (Soal 6 - 10 + 5 Poin):

- Tunnel GRE antara R-PUSAT (192.168.9.1/30) dan R-PELABUHAN (192.168.9.2/30).
- Rute spesifik LAN Balai Kota <-> LAN Pelabuhan dipaksa lewat tunnel (verifikasi traceroute).
- Bonus (+5): Enkripsi tunnel pakai IPsec (crypto isakmp, transform-set, crypto map / ipsec profile).
- Analisis teori siap: alasan router pilih tunnel vs physical path, dan mengapa GRE polos tanpa enkripsi.

3. OSPF Dynamic Routing & Link L7 (Soal 7 - 10 Poin):

- Buat file baru: K9_VLSM_OSPF.pkt (atau K9_CIDR_OSPF.pkt) duplikasi dari file statis utama.
- Pasang link cadangan L7 antara R-DC dan R-UTARA (alokasi subnet baru).
- Hapus static route antar-router, ganti router ospf.
- passive-interface aktif di seluruh LAN host pengguna.
- Default route ISP disebar otomatis dari R-PUSAT via default-information originate.
- Uji failover otomatis (putus link backbone, traffic tetap jalan via L7).

4. Demo Readiness & Final Deliverable (Soal 9 & Output - 25 Poin):

- Dua file .pkt siap: base static (K9*\*.pkt) dan OSPF (K9*\*\_OSPF.pkt).
- Dokumentasi GitHub Markdown lengkap (analisis teknis, screenshot uji 6, 7, 8).
- Siap troubleshooting individu 10 menit (Uji 2).

2. Steps Pengerjaan
   Prasyarat: Tunggu Anggota A (tabel IP, static route, NAT) dan Anggota B (topologi, IP interface/server, DHCP) tuntas, seluruh host bisa saling ping & ping 8.8.8.8.
   Phase 1: Setup Layanan Aplikasi (File Utama K9\_\*.pkt)
1. DNS (LAN Server DC): Aktifkan service DNS, buat A-record:

- k9.smartcity.lab -> IP Web Server Balai Kota
- www.k9.smartcity.lab -> IP Web Server Balai Kota
- ftp.k9.smartcity.lab -> IP FTP Server DC
- mail.k9.smartcity.lab -> IP Email Server DC (atau Balai Kota)

2. Web Server (LAN Balai Kota): Nyalakan HTTP/HTTPS, edit index.html dengan heading "Portal Smart City Surabaya - Kelompok 9".
3. FTP Server (LAN Server DC): Nyalakan service FTP, buat akun user/pass (hak: Write, Read, Delete, List). Tes upload file dari PC CCTV via command prompt (ftp ftp.k9.smartcity.lab -> put file.txt).
4. Email Server: Setup domain k9.smartcity.lab. Buat akun user-pusat dan user-pelabuhan. Setup email client di PC Balai Kota & PC Pelabuhan, kirim test email, verifikasi inbox.
   Phase 2: GRE Tunnel & IPsec (File Utama K9\_\*.pkt)
5. Buat interface Tunnel0 di R-PUSAT:

- IP: 192.168.9.1 255.255.255.252
- Tunnel source: interface fisik R-PUSAT arah internal / loopback
- Tunnel destination: IP interface fisik R-PELABUHAN

2. Buat interface Tunnel0 di R-PELABUHAN:

- IP: 192.168.9.2 255.255.255.252
- Tunnel source & destination matching R-PUSAT.

3. Rute spesifik Balai Kota <-> Pelabuhan via IP next-hop tunnel (192.168.9.2 dan 192.168.9.1).
4. Pasang enkripsi IPsec (Bonus): ISAKMP policy, pre-shared key, transform-set ESP-AES/SHA, crypto map / ipsec profile bind ke tunnel.
5. Verifikasi traceroute dari host Balai Kota ke Pelabuhan membuktikan lompatan via 192.168.9.x.
   Phase 3: Migrasi OSPF & L7 Cadangan (File Baru K9\_\*\_OSPF.pkt)
6. Copy file: Salin file dasar menjadi K9_VLSM_OSPF.pkt (atau CIDR).
7. Tambah Link L7: Hubungkan kabel serial/gigabit antara R-DC dan R-UTARA. Pasang subnet baru (misal /30).
8. Konfigurasi OSPF:

- Hapus static route antar-router (kecuali default route ISP di R-PUSAT).
- Setup router ospf 1 di seluruh router internal.
- Daftarkan network dengan wildcard mask di area 0.
- Set passive-interface untuk seluruh port yang menghadap Switch/PC LAN.
- Di R-PUSAT: default-information originate.

4. Verifikasi Failover: Ping loop / trace, matikan link utama (L1/L2), pastikan rute beralih otomatis via L7 tanpa putus total.
   Phase 4: Latihan Demo & Dokumentasi
1. Tulis penjelasan: (a) Mengapa rute tunnel dipilih (longest prefix match / static route specific metric), (b) Alasan GRE plain-text tanpa integritas/enkripsi.
1. Ambil screenshot bukti uji 6, 7, 8 untuk laporan.
1. Latihan Uji 2: Simulasi perbaikan link putus, DNS salah IP, OSPF network mask typo, atau tunnel mismatch dalam <10 menit.
1. Tools yang Bisa & Perlu Digunakan
1. Cisco Packet Tracer (v8.x+):

- Workspace GUI utama untuk verifikasi visual layanan (Web browser desktop PC, email client PT, FTP prompt).

2. Headless CLI / Scripting (pkt-core Python):

- Decode/inspect file .pkt tanpa buka GUI untuk audit config IOS (interface Tunnel, crypto, router ospf, DNS records).

3. MCP Packet Tracer (caixax/packet-tracer-mcp atau Builder-MCP.pts):

- Jika butuh agent menginjeksi command IOS router secara headless via bridge port :54321.

4. CLI Built-in PT Host:

- ping, tracert, ftp, ipconfig /all, nslookup untuk validasi Soal 6, 7, 8.

5. Git / GitHub Markdown:

- Dokumentasi laporan pengujian mandiri dan link commit tim.

6. ZIP Utility:

- Packaging akhir: MidProject Jarkom*K9*<NRP1>_<NRP2>_<NRP3>.ZIP.
