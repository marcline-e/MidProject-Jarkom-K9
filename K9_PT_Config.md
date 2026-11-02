# Konfigurasi Packet Tracer — dari `MID PROJECT_SAVE2.pkt` ke `K9_VLSM.pkt`

Dokumen ini disesuaikan dengan port dan kabel yang **sudah ada** di `MID PROJECT_SAVE2.pkt`, jadi tidak perlu ada kabel yang dipindah.
File tersebut masih memakai alamat latihan `10.9.x.x/24`. Langkah di bawah memindahkannya ke alamat VLSM hasil UTS (`10.72.0.0/16`, lihat `K9_Subnetting.xlsx`).

Urutan: **(1) ganti IP interface → (2) DHCP → (3) IP statis server → (4) static route → (5) NAT → (6) verifikasi → simpan sebagai `K9_VLSM.pkt`**.
Langkah 1–3 bagian Anggota B, langkah 4–6 bagian Anggota A.

## 0. Pemetaan port (kondisi file saat ini → alamat baru)

| Router | Port | Fungsi | IP lama | IP baru |
|---|---|---|---|---|
| R-PUSAT | Gi0/0 | ke R-ISP | 203.0.113.37/30 | (tetap) |
| R-PUSAT | Gi0/1 | L1 → R-DC | 10.9.0.1/30 | 10.72.241.33/30 |
| R-PUSAT | Gi0/2 | L2 → R-UTARA | 10.9.0.5/30 | 10.72.241.37/30 |
| R-PUSAT | Vlan10 (Fa0/0/0) | L3 → R-SELATAN | 10.9.0.9/30 | 10.72.241.41/30 |
| R-PUSAT | Vlan20 (Fa0/0/1) | L4 → R-TIMUR | 10.9.0.13/30 | 10.72.241.45/30 |
| R-PUSAT | Vlan30 (Fa0/0/2) | L5 → R-BARAT | 10.9.0.17/30 | 10.72.241.49/30 |
| R-PUSAT | Vlan40 (Fa0/0/3) | LAN Server Balai Kota | 10.9.1.1/24 | 10.72.241.1/27 |
| R-PUSAT | Vlan50 (Fa0/1/0) | LAN Pegawai Balai Kota | 10.9.11.1/24 | 10.72.224.1/21 |
| R-DC | Gi0/0 | L1 → R-PUSAT | 10.9.0.2/30 | 10.72.241.34/30 |
| R-DC | Gi0/1 | LAN Server dan Storage DC | 10.9.2.1/24 | 10.72.239.1/24 |
| R-DC | Gi0/2 | LAN CCTV Kota | 10.9.3.1/24 | 10.72.96.1/19 |
| R-UTARA | Gi0/0 | L2 → R-PUSAT | 10.9.0.6/30 | 10.72.241.38/30 |
| R-UTARA | Gi0/1 | L6 → R-PELABUHAN | 10.9.0.21/30 | 10.72.241.53/30 |
| R-UTARA | Gi0/2 | LAN Sensor Lalu Lintas Utara | 10.9.4.1/24 | 10.72.236.1/23 |
| R-UTARA | Vlan60 (Fa0/3/0) | LAN WiFi Publik Utara | 10.9.40.1/24 | 10.72.0.1/18 |
| R-PELABUHAN | Gi0/0 | L6 → R-UTARA | 10.9.0.22/30 | 10.72.241.54/30 |
| R-PELABUHAN | Gi0/1 | LAN Sensor dan SCADA Pelabuhan | 10.9.5.1/24 | 10.72.160.1/19 |
| R-PELABUHAN | Gi0/2 | LAN Kantor Pelabuhan | 10.9.50.1/24 | 10.72.240.1/25 |
| R-SELATAN | Gi0/0 | L3 → R-PUSAT | 10.9.0.10/30 | 10.72.241.42/30 |
| R-SELATAN | Gi0/1 | LAN PJU Pintar Selatan | 10.9.6.1/24 | 10.72.240.129/25 |
| R-SELATAN | Gi0/2 | LAN WiFi Publik Selatan | 10.9.60.1/24 | 10.72.64.1/19 |
| R-TIMUR | Gi0/0 | L4 → R-PUSAT | 10.9.0.14/30 | 10.72.241.46/30 |
| R-TIMUR | Gi0/1 | LAN Sensor Banjir Timur | 10.9.7.1/24 | 10.72.232.1/22 |
| R-TIMUR | Gi0/2 | LAN WiFi Publik Timur | 10.9.70.1/24 | 10.72.128.1/19 |
| R-BARAT | Gi0/0 | L5 → R-PUSAT | 10.9.0.18/30 | 10.72.241.50/30 |
| R-BARAT | Gi0/1 | LAN Puskesmas dan Sekolah Barat | 10.9.8.1/24 | 10.72.238.1/24 |
| R-BARAT | Gi0/2 | LAN WiFi Publik Barat | 10.9.80.1/24 | 10.72.192.1/19 |

IP statis server (usulan):

| Server | IP lama | IP baru | Gateway |
|---|---|---|---|
| SERVER DC (DNS, FTP, DHCP CCTV) | 10.9.2.2/24 | 10.72.239.2/24 | 10.72.239.1 |
| SERVER BALAI KOTA (Web) | – (kosong) | 10.72.241.2/27 | 10.72.241.1 |
| SERVER-INTERNET | – (kosong) | 8.8.8.8/24 | 8.8.8.1 |

## 1. Ganti IP interface (Anggota B)

Paste per router, mulai dari `configure terminal`.

### R-PUSAT
```
configure terminal
interface GigabitEthernet0/1
 ip address 10.72.241.33 255.255.255.252
interface GigabitEthernet0/2
 ip address 10.72.241.37 255.255.255.252
interface Vlan10
 ip address 10.72.241.41 255.255.255.252
interface Vlan20
 ip address 10.72.241.45 255.255.255.252
interface Vlan30
 ip address 10.72.241.49 255.255.255.252
interface Vlan40
 ip address 10.72.241.1 255.255.255.224
interface Vlan50
 ip address 10.72.224.1 255.255.248.0
end
```

### R-DC
```
configure terminal
interface GigabitEthernet0/0
 ip address 10.72.241.34 255.255.255.252
interface GigabitEthernet0/1
 ip address 10.72.239.1 255.255.255.0
interface GigabitEthernet0/2
 ip address 10.72.96.1 255.255.224.0
 no ip helper-address 10.9.2.2
 ip helper-address 10.72.239.2
end
```

### R-UTARA
```
configure terminal
interface GigabitEthernet0/0
 ip address 10.72.241.38 255.255.255.252
interface GigabitEthernet0/1
 ip address 10.72.241.53 255.255.255.252
interface GigabitEthernet0/2
 ip address 10.72.236.1 255.255.254.0
interface Vlan60
 ip address 10.72.0.1 255.255.192.0
end
```

### R-PELABUHAN
```
configure terminal
interface GigabitEthernet0/0
 ip address 10.72.241.54 255.255.255.252
interface GigabitEthernet0/1
 ip address 10.72.160.1 255.255.224.0
interface GigabitEthernet0/2
 ip address 10.72.240.1 255.255.255.128
end
```

### R-SELATAN
```
configure terminal
interface GigabitEthernet0/0
 ip address 10.72.241.42 255.255.255.252
interface GigabitEthernet0/1
 ip address 10.72.240.129 255.255.255.128
interface GigabitEthernet0/2
 ip address 10.72.64.1 255.255.224.0
end
```

### R-TIMUR
```
configure terminal
interface GigabitEthernet0/0
 ip address 10.72.241.46 255.255.255.252
interface GigabitEthernet0/1
 ip address 10.72.232.1 255.255.252.0
interface GigabitEthernet0/2
 ip address 10.72.128.1 255.255.224.0
end
```

### R-BARAT
```
configure terminal
interface GigabitEthernet0/0
 ip address 10.72.241.50 255.255.255.252
interface GigabitEthernet0/1
 ip address 10.72.238.1 255.255.255.0
interface GigabitEthernet0/2
 ip address 10.72.192.1 255.255.224.0
end
```

## 2. DHCP (Anggota B)

Pool lama (`10.9.x.0/24`) harus dihapus dulu supaya tidak membagikan alamat yang salah. Gaya exclude `.1`–`.10` dipertahankan.

### R-PUSAT
```
configure terminal
no ip dhcp excluded-address 10.9.1.1 10.9.1.10
no ip dhcp excluded-address 10.9.11.1 10.9.11.10
no ip dhcp pool POOL-BALAIKOTA
no ip dhcp pool POOL-PEGAWAI
ip dhcp excluded-address 10.72.224.1 10.72.224.10
ip dhcp pool POOL-PEGAWAI
 network 10.72.224.0 255.255.248.0
 default-router 10.72.224.1
 dns-server 10.72.239.2
end
```
LAN Server Balai Kota hanya berisi server dengan IP statis, jadi tidak perlu pool.

### R-UTARA
```
configure terminal
no ip dhcp excluded-address 10.9.4.1 10.9.4.10
no ip dhcp excluded-address 10.9.40.1 10.9.40.10
no ip dhcp pool POOL-UTARA
no ip dhcp pool POOL-WIFI-UTARA
ip dhcp excluded-address 10.72.236.1 10.72.236.10
ip dhcp excluded-address 10.72.0.1 10.72.0.10
ip dhcp pool POOL-LALIN-UTARA
 network 10.72.236.0 255.255.254.0
 default-router 10.72.236.1
 dns-server 10.72.239.2
ip dhcp pool POOL-WIFI-UTARA
 network 10.72.0.0 255.255.192.0
 default-router 10.72.0.1
 dns-server 10.72.239.2
end
```

### R-PELABUHAN
```
configure terminal
no ip dhcp excluded-address 10.9.5.1 10.9.5.10
no ip dhcp excluded-address 10.9.50.1 10.9.50.10
no ip dhcp pool POOL-PELABUHAN
no ip dhcp pool POOL-KANTOR-PELABUHAN
ip dhcp excluded-address 10.72.160.1 10.72.160.10
ip dhcp excluded-address 10.72.240.1 10.72.240.10
ip dhcp pool POOL-SCADA-PELABUHAN
 network 10.72.160.0 255.255.224.0
 default-router 10.72.160.1
 dns-server 10.72.239.2
ip dhcp pool POOL-KANTOR-PELABUHAN
 network 10.72.240.0 255.255.255.128
 default-router 10.72.240.1
 dns-server 10.72.239.2
end
```

### R-SELATAN
```
configure terminal
no ip dhcp excluded-address 10.9.6.1 10.9.6.10
no ip dhcp excluded-address 10.9.60.1 10.9.60.10
no ip dhcp pool POOL-SELATAN
no ip dhcp pool POOL-WIFI-SELATAN
ip dhcp excluded-address 10.72.240.129 10.72.240.138
ip dhcp excluded-address 10.72.64.1 10.72.64.10
ip dhcp pool POOL-PJU-SELATAN
 network 10.72.240.128 255.255.255.128
 default-router 10.72.240.129
 dns-server 10.72.239.2
ip dhcp pool POOL-WIFI-SELATAN
 network 10.72.64.0 255.255.224.0
 default-router 10.72.64.1
 dns-server 10.72.239.2
end
```

### R-TIMUR
```
configure terminal
no ip dhcp excluded-address 10.9.7.1 10.9.7.10
no ip dhcp excluded-address 10.9.70.1 10.9.70.10
no ip dhcp pool POOL-TIMUR
no ip dhcp pool POOL-WIFI-TIMUR
ip dhcp excluded-address 10.72.232.1 10.72.232.10
ip dhcp excluded-address 10.72.128.1 10.72.128.10
ip dhcp pool POOL-BANJIR-TIMUR
 network 10.72.232.0 255.255.252.0
 default-router 10.72.232.1
 dns-server 10.72.239.2
ip dhcp pool POOL-WIFI-TIMUR
 network 10.72.128.0 255.255.224.0
 default-router 10.72.128.1
 dns-server 10.72.239.2
end
```

### R-BARAT
```
configure terminal
no ip dhcp excluded-address 10.9.8.1 10.9.8.10
no ip dhcp excluded-address 10.9.80.1 10.9.80.10
no ip dhcp pool POOL-BARAT
no ip dhcp pool POOL-WIFI-BARAT
ip dhcp excluded-address 10.72.238.1 10.72.238.10
ip dhcp excluded-address 10.72.192.1 10.72.192.10
ip dhcp pool POOL-PUSKESMAS-BARAT
 network 10.72.238.0 255.255.255.0
 default-router 10.72.238.1
 dns-server 10.72.239.2
ip dhcp pool POOL-WIFI-BARAT
 network 10.72.192.0 255.255.224.0
 default-router 10.72.192.1
 dns-server 10.72.239.2
end
```

### DHCP CCTV Kota di SERVER DC (GUI: Services → DHCP)
- Pool lama `serverPool`: biarkan, tapi jangan dipakai untuk CCTV.
- Tambah pool baru:
  - Nama `POOL-CCTV`
  - Default Gateway `10.72.96.1`
  - DNS `10.72.239.2`
  - Start IP `10.72.96.11`
  - Subnet Mask `255.255.224.0`
  - Max users `100`
- Klik **Add**, lalu pastikan service **On**.
- R-DC Gi0/2 sudah diberi `ip helper-address 10.72.239.2` di langkah 1.

## 3. IP statis server (Anggota B)

Di setiap server buka Desktop → IP Configuration → Static, lalu isi sesuai tabel di bagian 0:
- SERVER DC: `10.72.239.2`, `255.255.255.0`, gateway `10.72.239.1`, DNS `10.72.239.2`
- SERVER BALAI KOTA: `10.72.241.2`, `255.255.255.224`, gateway `10.72.241.1`, DNS `10.72.239.2`
- SERVER-INTERNET: `8.8.8.8`, `255.255.255.0`, gateway `8.8.8.1`

## 4. Static Route (Anggota A — Soal 3)

### R-PUSAT
```
configure terminal
ip route 0.0.0.0 0.0.0.0 203.0.113.38
ip route 10.72.96.0 255.255.224.0 10.72.241.34
ip route 10.72.239.0 255.255.255.0 10.72.241.34
ip route 10.72.0.0 255.255.192.0 10.72.241.38
ip route 10.72.236.0 255.255.254.0 10.72.241.38
ip route 10.72.160.0 255.255.224.0 10.72.241.38
ip route 10.72.240.0 255.255.255.128 10.72.241.38
ip route 10.72.241.52 255.255.255.252 10.72.241.38
ip route 10.72.64.0 255.255.224.0 10.72.241.42
ip route 10.72.240.128 255.255.255.128 10.72.241.42
ip route 10.72.128.0 255.255.224.0 10.72.241.46
ip route 10.72.232.0 255.255.252.0 10.72.241.46
ip route 10.72.192.0 255.255.224.0 10.72.241.50
ip route 10.72.238.0 255.255.255.0 10.72.241.50
end
```

### R-UTARA
```
configure terminal
ip route 0.0.0.0 0.0.0.0 10.72.241.37
ip route 10.72.160.0 255.255.224.0 10.72.241.54
ip route 10.72.240.0 255.255.255.128 10.72.241.54
end
```

### Router cabang (default route ke atas)
```
! R-DC
configure terminal
ip route 0.0.0.0 0.0.0.0 10.72.241.33
end

! R-SELATAN
configure terminal
ip route 0.0.0.0 0.0.0.0 10.72.241.41
end

! R-TIMUR
configure terminal
ip route 0.0.0.0 0.0.0.0 10.72.241.45
end

! R-BARAT
configure terminal
ip route 0.0.0.0 0.0.0.0 10.72.241.49
end

! R-PELABUHAN
configure terminal
ip route 0.0.0.0 0.0.0.0 10.72.241.53
end
```

R-ISP: **tidak diberi `ip route` apa pun**. Kondisi di file sekarang sudah benar.

## 5. NAT Overload (Anggota A — Soal 5) di R-PUSAT
```
configure terminal
access-list 1 permit 10.72.0.0 0.0.255.255
interface GigabitEthernet0/0
 ip nat outside
interface GigabitEthernet0/1
 ip nat inside
interface GigabitEthernet0/2
 ip nat inside
interface Vlan10
 ip nat inside
interface Vlan20
 ip nat inside
interface Vlan30
 ip nat inside
interface Vlan40
 ip nat inside
interface Vlan50
 ip nat inside
exit
ip nat inside source list 1 interface GigabitEthernet0/0 overload
end
```

## 6. Verifikasi, lalu simpan

Di setiap router jalankan `write memory`.

1. `show ip interface brief` di setiap router: semua port yang dipakai harus up/up dengan IP 10.72.x.x.
2. Di setiap PC: Desktop → IP Configuration → DHCP (atau `ipconfig /renew`). Harus dapat IP 10.72.x.x, gateway, dan DNS `10.72.239.2`.
3. `show ip route` di R-PUSAT: 13 route `S` ditambah `S* 0.0.0.0/0 via 203.0.113.38`.
4. `show ip route` di R-ISP: hanya 203.0.113.36/30 dan 8.8.8.0/24.
5. Ping antar-wilayah, misalnya PC KANTOR → CCTV KOTA dan SEKOLAH → SERVER DC.
6. `ping 8.8.8.8` dari 1 host tiap wilayah, lalu `show ip nat translations` di R-PUSAT.
7. File → Save As **`K9_VLSM.pkt`**.

## 7. Temuan lain di file (untuk Anggota B / C)

- **Belum ada label teks LAN** (Soal 1: nama subnet, Network ID/prefix, jumlah host). Tambahkan dengan tool *Place Note*.
- **LAN WiFi (Utara, Selatan, Timur, Barat) baru berisi Access Point, belum ada perangkat perwakilan.** Tambahkan 1 laptop/smartphone wireless per AP.
- Hostname semua switch masih `Switch`. Display name sudah benar, tapi lebih rapi kalau `hostname` di CLI juga diganti, misalnya `hostname SW-DC`.
- R-PUSAT: deskripsi `Fa0/2/0` ("L5 Cable Port to R-BARAT") tidak sesuai karena kabel L5 ada di `Fa0/0/2`. Hanya kosmetik.
- **OSPF L7 (Anggota C):** ketiga port Gigabit di R-DC sudah terpakai. Untuk link L7 R-DC ↔ R-UTARA, R-DC perlu modul tambahan (misalnya HWIC-2T untuk serial, atau HWIC-4ESW + SVI seperti di R-PUSAT). Di R-UTARA masih ada `Fa0/3/1` (HWIC-4ESW) yang kosong. Subnet L7: `10.72.241.56/30`.
