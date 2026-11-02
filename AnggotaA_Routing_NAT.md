# Anggota A — Subnetting, Static Routing, dan NAT (Kelompok 9, skema VLSM)

Sumber angka: `K9_Subnetting.xlsx` (sheet **VLSM** dan **IP Interface VLSM**).
Blok dasar: `10.72.0.0/16` (oktet ke-2 = 8 × 9 = 72).

## 1. Tabel VLSM (hasil revisi)

| No | Router | Subnet | Host | Network ID/Prefix | Rentang Host | Broadcast | Gateway |
|---|---|---|---|---|---|---|---|
| 1 | R-UTARA | WiFi Publik Utara | 11.000 | 10.72.0.0/18 | 10.72.0.1 – 10.72.63.254 | 10.72.63.255 | 10.72.0.1 |
| 2 | R-SELATAN | WiFi Publik Selatan | 6.500 | 10.72.64.0/19 | 10.72.64.1 – 10.72.95.254 | 10.72.95.255 | 10.72.64.1 |
| 3 | R-DC | CCTV Kota | 6.000 | 10.72.96.0/19 | 10.72.96.1 – 10.72.127.254 | 10.72.127.255 | 10.72.96.1 |
| 4 | R-TIMUR | WiFi Publik Timur | 5.500 | 10.72.128.0/19 | 10.72.128.1 – 10.72.159.254 | 10.72.159.255 | 10.72.128.1 |
| 5 | R-PELABUHAN | Sensor dan SCADA Pelabuhan | 5.000 | 10.72.160.0/19 | 10.72.160.1 – 10.72.191.254 | 10.72.191.255 | 10.72.160.1 |
| 6 | R-BARAT | WiFi Publik Barat | 4.500 | 10.72.192.0/19 | 10.72.192.1 – 10.72.223.254 | 10.72.223.255 | 10.72.192.1 |
| 7 | R-PUSAT | Pegawai Balai Kota | 1.800 | 10.72.224.0/21 | 10.72.224.1 – 10.72.231.254 | 10.72.231.255 | 10.72.224.1 |
| 8 | R-TIMUR | Sensor Banjir Timur | 700 | 10.72.232.0/22 | 10.72.232.1 – 10.72.235.254 | 10.72.235.255 | 10.72.232.1 |
| 9 | R-UTARA | Sensor Lalu Lintas Utara | 450 | 10.72.236.0/23 | 10.72.236.1 – 10.72.237.254 | 10.72.237.255 | 10.72.236.1 |
| 10 | R-BARAT | Puskesmas dan Sekolah Barat | 220 | 10.72.238.0/24 | 10.72.238.1 – 10.72.238.254 | 10.72.238.255 | 10.72.238.1 |
| 11 | R-DC | Server dan Storage DC | 180 | 10.72.239.0/24 | 10.72.239.1 – 10.72.239.254 | 10.72.239.255 | 10.72.239.1 |
| 12 | R-PELABUHAN | Kantor Pelabuhan | 120 | 10.72.240.0/25 | 10.72.240.1 – 10.72.240.126 | 10.72.240.127 | 10.72.240.1 |
| 13 | R-SELATAN | PJU Pintar Selatan | 90 | 10.72.240.128/25 | 10.72.240.129 – 10.72.240.254 | 10.72.240.255 | 10.72.240.129 |
| 14 | R-PUSAT | Server Balai Kota | 20 | 10.72.241.0/27 | 10.72.241.1 – 10.72.241.30 | 10.72.241.31 | 10.72.241.1 |
| 15 | PUSAT–DC | L1 | 2 | 10.72.241.32/30 | .33 (PUSAT) – .34 (DC) | 10.72.241.35 | – |
| 16 | PUSAT–UTARA | L2 | 2 | 10.72.241.36/30 | .37 (PUSAT) – .38 (UTARA) | 10.72.241.39 | – |
| 17 | PUSAT–SELATAN | L3 | 2 | 10.72.241.40/30 | .41 (PUSAT) – .42 (SELATAN) | 10.72.241.43 | – |
| 18 | PUSAT–TIMUR | L4 | 2 | 10.72.241.44/30 | .45 (PUSAT) – .46 (TIMUR) | 10.72.241.47 | – |
| 19 | PUSAT–BARAT | L5 | 2 | 10.72.241.48/30 | .49 (PUSAT) – .50 (BARAT) | 10.72.241.51 | – |
| 20 | UTARA–PELABUHAN | L6 | 2 | 10.72.241.52/30 | .53 (UTARA) – .54 (PELABUHAN) | 10.72.241.55 | – |

Pemakaian VLSM: 42.092 / 65.536 = **64,23%** (blok induk /16). Alamat kosong pertama `10.72.241.56` → disarankan untuk link L7 (OSPF): `10.72.241.56/30`.

Tambahan dari soal Mid-Project: R-PUSAT–R-ISP `203.0.113.36/30` (PUSAT `.37`, ISP `.38`), server `8.8.8.8/24` (gateway `8.8.8.1`), tunnel GRE `192.168.9.0/30`.

## 2. Static Routing (Soal 3)

Prinsip:
- Router cabang (R-DC, R-SELATAN, R-TIMUR, R-BARAT, R-PELABUHAN) cukup **default route ke router di atasnya**.
- R-UTARA: default route ke R-PUSAT + static route ke LAN R-PELABUHAN.
- R-PUSAT: default route ke R-ISP + static route ke **semua LAN** di bawahnya.
- Route ditulis memakai **next-hop IP**, jadi tidak bergantung pada nama port fisik yang dipilih Anggota B.

### R-PUSAT
```
! Default route keluar ke internet
ip route 0.0.0.0 0.0.0.0 203.0.113.38
! R-DC (via L1)
ip route 10.72.96.0 255.255.224.0 10.72.241.34
ip route 10.72.239.0 255.255.255.0 10.72.241.34
! R-UTARA (via L2)
ip route 10.72.0.0 255.255.192.0 10.72.241.38
ip route 10.72.236.0 255.255.254.0 10.72.241.38
! R-PELABUHAN (via L2 -> R-UTARA), termasuk link L6
ip route 10.72.160.0 255.255.224.0 10.72.241.38
ip route 10.72.240.0 255.255.255.128 10.72.241.38
ip route 10.72.241.52 255.255.255.252 10.72.241.38
! R-SELATAN (via L3)
ip route 10.72.64.0 255.255.224.0 10.72.241.42
ip route 10.72.240.128 255.255.255.128 10.72.241.42
! R-TIMUR (via L4)
ip route 10.72.128.0 255.255.224.0 10.72.241.46
ip route 10.72.232.0 255.255.252.0 10.72.241.46
! R-BARAT (via L5)
ip route 10.72.192.0 255.255.224.0 10.72.241.50
ip route 10.72.238.0 255.255.255.0 10.72.241.50
```

### R-UTARA
```
ip route 0.0.0.0 0.0.0.0 10.72.241.37
ip route 10.72.160.0 255.255.224.0 10.72.241.54
ip route 10.72.240.0 255.255.255.128 10.72.241.54
```

### R-DC
```
ip route 0.0.0.0 0.0.0.0 10.72.241.33
```

### R-SELATAN
```
ip route 0.0.0.0 0.0.0.0 10.72.241.41
```

### R-TIMUR
```
ip route 0.0.0.0 0.0.0.0 10.72.241.45
```

### R-BARAT
```
ip route 0.0.0.0 0.0.0.0 10.72.241.49
```

### R-PELABUHAN
```
ip route 0.0.0.0 0.0.0.0 10.72.241.53
```

### R-ISP
Tidak ada `ip route` sama sekali. Kedua jaringannya (`203.0.113.36/30` dan `8.8.8.0/24`) terhubung langsung, dan R-ISP **tidak boleh** tahu rute ke `10.72.0.0`.

## 3. NAT Overload (Soal 5)

Ganti nama interface di dalam `< >` dengan port yang dipakai Anggota B di R-PUSAT. Versi dengan nama port final ada di `K9_PT_Config.md`.

```
! ACL: seluruh alamat privat internal kelompok 9
access-list 1 permit 10.72.0.0 0.0.255.255

! Interface ke R-ISP
interface <IF-KE-R-ISP>
 ip address 203.0.113.37 255.255.255.252
 ip nat outside
 no shutdown

! Semua interface ke arah dalam: L1, L2, L3, L4, L5, LAN Pegawai, LAN Server Balai Kota
interface <IF-L1>
 ip nat inside
interface <IF-L2>
 ip nat inside
interface <IF-L3>
 ip nat inside
interface <IF-L4>
 ip nat inside
interface <IF-L5>
 ip nat inside
interface <IF-LAN-PEGAWAI>
 ip nat inside
interface <IF-LAN-SERVER-BALAIKOTA>
 ip nat inside

! PAT: semua host keluar memakai IP publik 203.0.113.37
ip nat inside source list 1 interface <IF-KE-R-ISP> overload
```

R-ISP (hanya IP, tanpa route):
```
interface <IF-KE-R-PUSAT>
 ip address 203.0.113.38 255.255.255.252
 no shutdown
interface <IF-KE-SERVER>
 ip address 8.8.8.1 255.255.255.0
 no shutdown
```
Server 8.8.8.8: IP `8.8.8.8`, mask `255.255.255.0`, gateway `8.8.8.1`.

## 4. Verifikasi & Screenshot

| Cek | Perintah | Hasil yang diharapkan |
|---|---|---|
| Tabel routing R-PUSAT | `show ip route static` | 13 route `S` ke LAN + `S*` 0.0.0.0/0 via 203.0.113.38 |
| Tabel routing R-UTARA | `show ip route static` | `S*` via .37 + 2 route ke LAN Pelabuhan via .54 |
| R-ISP bersih | `show ip route` di R-ISP | Hanya `C`/`L` untuk 203.0.113.36/30 dan 8.8.8.0/24, **tanpa 10.x** |
| Antar-LAN | Ping dari PC Kantor Pelabuhan ke PC CCTV Kota, dari WiFi Barat ke Server DC, dst. | Reply |
| Internet | `ping 8.8.8.8` dari 1 host tiap wilayah (Balai Kota, DC, Utara, Pelabuhan, Selatan, Timur, Barat) | Reply |
| Translasi NAT | `show ip nat translations` di R-PUSAT (setelah ping) | Inside global `203.0.113.37`, inside local `10.72.x.x` |
| Konfigurasi NAT | `show running-config \| include nat` | Baris `ip nat inside/outside` dan `overload` |

Screenshot untuk laporan: sheet VLSM, CIDR, Supernet CIDR, dan Revisi; output `show ip route` R-PUSAT, R-UTARA, R-ISP; `show running-config | include nat`; `show ip nat translations`; `ping 8.8.8.8` dari setiap wilayah.

## 5. Catatan untuk anggota lain

- **Anggota B**: IP interface router, gateway, dan alamat server ada di sheet **IP Interface VLSM**. Di link, router atas memakai host pertama dan router bawah host kedua; next-hop di atas bergantung pada aturan ini. Pool DHCP: exclude `.1` (gateway) dan IP server statis.
- **Anggota C (GRE)**: tunnel destination dari R-PUSAT = `10.72.241.54` (R-PELABUHAN, L6), sudah bisa dijangkau lewat route `10.72.241.52/30`. Agar trafik Balai Kota ↔ Pelabuhan lewat tunnel, ubah next-hop route LAN Pelabuhan di R-PUSAT menjadi `192.168.9.2`. Di R-PELABUHAN, tambahkan route `10.72.224.0/21` dan `10.72.241.0/27` via `192.168.9.1`.
- **Anggota C (OSPF)**: L7 R-DC ↔ R-UTARA memakai `10.72.241.56/30` (alamat kosong pertama setelah L6).
