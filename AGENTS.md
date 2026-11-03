# AGENTS.md

Panduan otomatis pengerjaan Mid Project Jarkom Smart City Surabaya - **Kelompok 9** (3 Anggota).
Jika user menyebut role (`Anggota A`, `Anggota B`, atau `Anggota C`), asisten langsung mengeksekusi instruksi role terkait.

### Parameter Kelompok 9 (K = 9):
- **Link R-PUSAT ke R-ISP**: `203.0.113.36/30` (4 × 9 = 36) -> R-PUSAT `.37`, R-ISP `.38`
- **Server Internet**: `8.8.8.8` (Gateway `8.8.8.1` di R-ISP)
- **Tunnel GRE**: `192.168.9.0/30` -> R-PUSAT `192.168.9.1`, R-PELABUHAN `192.168.9.2`
- **Domain Internal**: `k9.smartcity.lab`
- **Nama File Utama**: `K9_VLSM.pkt` / `K9_CIDR.pkt` dan `K9_VLSM_OSPF.pkt` / `K9_CIDR_OSPF.pkt`
- **Nama Arsip ZIP**: `MidProject Jarkom_K9_<NRP1>_<NRP2>_<NRP3>.ZIP`

---

## 1. Timeline Ketergantungan (Dependency Graph)

```text
[Phase 1: Anggota A]
Tabel Subnetting (VLSM & CIDR) -> Spreadsheet .xlsx & tabel revisi UTS
  │
  ▼ (Wajib selesai sebelum konfigurasi perangkat)
[Phase 2: Anggota B]
Rakit Topologi Packet Tracer, penamaan, label, & alokasi IP statis interface/server
  │
  ├────────────────────────────────────────┐
  ▼                                        ▼
[Phase 3: Anggota A]                    [Phase 3: Anggota B]
- Static Route & Default Route          - DHCP Router (User LANs)
- NAT di R-PUSAT -> 8.8.8.8             - DHCP Server DC (khusus CCTV LAN)
  │                                        │
  └───────────────────┬────────────────────┘
                      ▼ (Verifikasi: seluruh host bisa saling ping & ping 8.8.8.8)
              [Phase 4: Anggota C]
              - GRE Tunnel (PUSAT <-> PELABUHAN) + Bonus IPsec
              - Layanan Aplikasi (DNS, Web, FTP, Mail)
                      │
                      ▼ (Gandakan .pkt -> *_OSPF.pkt)
              [Phase 5: Anggota C]
              - Link cadangan L7 (R-DC <-> R-UTARA)
              - Migrasi OSPF & uji failover link
                      │
                      ▼
              [Phase 6: Seluruh Anggota]
              - Latihan Uji 2 Demo (simulasi troubleshooting 10 menit per orang)
              - Kompilasi laporan GitHub Markdown & ZIP akhir
```

---

## 2. Instruksi Role Spesifik

### Jika User = "Anggota A" (Fondasi Subnetting, Routing Statis, & NAT)
Fokus: Soal 2, Soal 3, Soal 5.

**Langkah Kerja:**
1. **Spreadsheet Subnetting (Soal 2)**:
   - Buat tabel VLSM dan CIDR dari data UTS: Network ID, prefix, host range, broadcast, gateway (host pertama).
   - Buat tabel supernet per router untuk CIDR.
   - Buat tabel revisi jika ada perbaikan nilai UTS (format: `Subnet`, `Jawaban UTS`, `Perbaikan`, `Alasan`).
2. **Static Routing (Soal 3)**:
   - Aturan default route: hanya boleh mengarah ke upstream (R-DC -> R-PUSAT, R-PELABUHAN -> R-UTARA, R-PUSAT -> R-ISP).
   - R-PUSAT: wajib punya static route ke seluruh LAN internal (R-DC, R-UTARA, R-PELABUHAN, R-SELATAN, R-TIMUR, R-BARAT).
   - R-UTARA: wajib punya static route ke seluruh LAN milik R-PELABUHAN.
3. **NAT Overload (Soal 5)**:
   - Konfigurasi NAT di R-PUSAT menuju IP link R-ISP `203.0.113.36/30` (IP R-PUSAT: `203.0.113.37`).
   - Pastikan R-ISP **TIDAK** memiliki routing balik ke subnet privat internal. Seluruh host harus bisa ping `8.8.8.8`.
4. **Dokumentasi & Verifikasi**:
   - Screenshot tabel spreadsheet, perintah routing statis, running config NAT, dan bukti `ping 8.8.8.8` dari perwakilan LAN.

---

### Jika User = "Anggota B" (Topologi, Perangkat Fisik, & DHCP)
Fokus: Soal 1, Soal 4.

**Langkah Kerja:**
1. **Perancangan Topologi (Soal 1)**:
   - Susun backbone router L1–L6 sesuai Gambar 1 soal, termasuk R-ISP dan Server 8.8.8.8.
   - Desain LAN setiap wilayah: pasang 1 perwakilan host per subnet (PC/laptop/server).
   - Ganti display name perangkat sesuai lokasi (contoh: `R-PUSAT`, `SW-BALAIKOTA`, `PC-CCTV-KOTA`).
   - Beri label teks di Packet Tracer untuk setiap subnet: Nama Subnet, Net ID/Prefix, dan Jumlah Host.
   - Konfigurasi IP statis pada seluruh interface router dan server berdasarkan tabel Anggota A. Gateway = IP host pertama.
2. **DHCP Services (Soal 4)**:
   - Subnet pengguna umum: Konfigurasi DHCP pool langsung di masing-masing router lokal (exclude IP statis router/server, sertakan default gateway & DNS `LAN Server DC`).
   - **Khusus Subnet CCTV Kota**: Dilarang DHCP dari router. Konfigurasi DHCP Service di server LAN Server & Storage DC. Aktifkan `ip helper-address` pada interface router yang mengarah ke LAN CCTV jika beda segmen.
3. **Dokumentasi & Verifikasi**:
   - Screenshot topologi lengkap dengan label, konfigurasi DHCP pool router, konfigurasi DHCP server DC, serta hasil `ipconfig /renew` pada client (memastikan IP, gateway, dan DNS otomatis terisi).

---

### Jika User = "Anggota C" (Tunnel GRE/IPsec, Layanan Aplikasi, & OSPF)
Fokus: Soal 6, Soal 7, Soal 8.

**Langkah Kerja:**
1. **Layanan Aplikasi Smart City (Soal 8)**:
   - Domain internal: `k9.smartcity.lab`.
   - DNS Server di LAN Server DC: Record untuk `www`, `ftp`, `mail`.
   - Web Server di LAN Balai Kota: Halaman HTML "Portal Smart City Surabaya" + Kelompok 9.
   - FTP Server di LAN Server DC: User login dengan izin upload rekaman CCTV.
   - Email Server: Setup domain mail, akun pengguna Balai Kota & Pelabuhan, verifikasi kirim-terima email.
2. **GRE Tunnel & IPsec (Soal 6)**:
   - Buat interface tunnel antara R-PUSAT (`192.168.9.1/30`) dan R-PELABUHAN (`192.168.9.2/30`).
   - Arahkan rute spesifik subnet Balai Kota <-> Pelabuhan agar via tunnel. Buktikan via `traceroute`.
   - Bonus (+5): Tambahkan crypto policy, transform-set, dan crypto map IPsec pada link tunnel.
3. **OSPF Dynamic Routing (Soal 7)**:
   - **PENTING**: Duplikasi file `.pkt` utama menjadi `K9_<skema>_OSPF.pkt`. Jangan sentuh file static!
   - Tambahkan link L7 antara R-DC dan R-UTARA dengan subnet baru.
   - Hapus static route antar-router, ganti `router ospf`.
   - Pasang `passive-interface` pada seluruh interface yang mengarah ke LAN host pengguna.
   - Default route ke ISP hanya di R-PUSAT; sebarkan ke router lain via OSPF (`default-information originate`).
   - Uji pemulihan otomatis (putuskan salah satu link backbone, buktikan traffic tetap tembus).
4. **Dokumentasi & Verifikasi**:
   - Penjelasan teknis: Mengapa jalur memilih GRE tunnel dibanding jalur fisik, dan mengapa GRE tanpa IPsec tidak terenkripsi.
   - Screenshot traceroute GRE, tes browser web portal, login/upload FTP, kirim email, dan tes failover OSPF.

---

## 3. Format Output & Pengumpulan Akhir
- File `.pkt`:
  - `K9_VLSM.pkt` atau `K9_CIDR.pkt` (Base: Static + NAT + DHCP + GRE + Services).
  - `K9_VLSM_OSPF.pkt` atau `K9_CIDR_OSPF.pkt` (OSPF + L7).
- File `.xlsx`: Tabel subnetting lengkap + revisi.
- Repository GitHub: Laporan Markdown dan screenshot bukti uji.
- Arsip ZIP: `MidProject Jarkom_K9_<3 digit NRP 1>_<NRP 2>_<NRP 3>.ZIP`.

---

## 4. Automasi Cisco Packet Tracer oleh Agent

### Metode Utama (Default): Headless / Code Generator (`pkt-core`)
- Gunakan library Python `pkt-core` untuk decode/encode file `.pkt` tanpa membuka GUI Packet Tracer.
- Instalasi: `pip install pkt-core`
- Workflow: Agent generate script Python pembuat topologi, konfigurasi interface/IOS, lalu compile ke `K9_VLSM.pkt` atau `K9_CIDR.pkt`.

### Metode Alternatif (On-Demand): Live Control via MCP Server
- Digunakan saat butuh GUI live, real-time testing, atau interaksi langsung dengan Packet Tracer aktif.
- Setup:
  1. Pasang extension script `Builder-MCP.pts` di Packet Tracer via menu **Extensions > Scripting > Configure PT Script Modules** (set **On Startup**).
  2. Pasang server MCP: `pip install packet-tracer-mcp` (dari `caixax/packet-tracer-mcp` atau `Mats2208/MCP-Packet-Tracer`).
  3. Konfigurasi MCP client OpenCode/Claude Code ke command `packet-tracer-mcp` (HTTP bridge ke `:54321`).
