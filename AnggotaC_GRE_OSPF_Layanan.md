# Anggota C — Tunnel GRE + IPsec, OSPF + L7, dan Layanan Aplikasi (Kelompok 9, skema VLSM)

File yang dikerjakan:
- `K9_VLSM.pkt` — file utama (static + NAT + DHCP + GRE + IPsec + layanan aplikasi).
- `K9_VLSM_OSPF.pkt` — file terpisah (soal 7): link cadangan L7 + OSPF.

Alamat pendukung: tunnel GRE `192.168.9.0/30` (R-PUSAT `.1`, R-PELABUHAN `.2`), link L7 `10.72.241.56/30` (R-UTARA `.57`, R-DC `.58`), domain internal `k9.smartcity.lab`.

## 1. Tunnel GRE + Bonus IPsec (Soal 6)

### Konfigurasi

R-PUSAT:
```
interface Tunnel0
 ip address 192.168.9.1 255.255.255.252
 tunnel source GigabitEthernet0/2
 tunnel destination 10.72.241.54
!
! Trafik Balai Kota -> Pelabuhan dipaksa lewat tunnel
ip route 10.72.160.0 255.255.224.0 192.168.9.2
ip route 10.72.240.0 255.255.255.128 192.168.9.2
```

R-PELABUHAN:
```
interface Tunnel0
 ip address 192.168.9.2 255.255.255.252
 tunnel source GigabitEthernet0/0
 tunnel destination 10.72.241.37
!
ip route 10.72.224.0 255.255.248.0 192.168.9.1
ip route 10.72.241.0 255.255.255.224 192.168.9.1
```

Bonus IPsec (kedua router, `K9-IPSEC` crypto map di interface menuju peer):
```
crypto isakmp policy 10
 encr aes
 authentication pre-share
crypto isakmp key K9-GRE-IPSEC address <IP-peer>
crypto ipsec transform-set K9-SET esp-aes esp-sha-hmac
crypto map K9-IPSEC 10 ipsec-isakmp
 set peer <IP-peer>
 set transform-set K9-SET
 match address <ACL-GRE>
```
Tunnel dienkripsi dengan **IPsec transport mode over GRE** (match address membatasi protokol 47 GRE antar endpoint), bukan `tunnel mode ipsec ipv4`.

### Bukti uji

Traceroute dari PC - PEGAWAI (LAN Pegawai Balai Kota) ke PC KANTOR (LAN Kantor Pelabuhan):
```
  1   10.72.224.1      (gateway, R-PUSAT)
  2   192.168.9.2      (tunnel GRE -> R-PELABUHAN)
  3   10.72.240.11     (tujuan)
```
Arah balik dari PC KANTOR: hop 2 = `192.168.9.1`. Lalu lintas antar-wilayah benar-benar melewati tunnel, bukan jalur fisik L2→L6.

Status IPsec setelah ping antar-wilayah (`show crypto isakmp sa` / `show crypto ipsec sa`):
```
dst             src             state          conn-id slot status
10.72.241.54    10.72.241.37    QM_IDLE           1060    0 ACTIVE
...
#pkts encaps: 15, #pkts encrypt: 15, #pkts digest: 0
#pkts decaps: 11, #pkts decrypt: 11, #pkts verify: 0
transform: esp-aes esp-sha-hmac , in use settings ={Tunnel, }
Status: ACTIVE
```
Counter `encrypt`/`decrypt` bertambah pada setiap ping → paket GRE benar terenkripsi.

### Penjelasan teknis

**Mengapa router memilih jalur tunnel?** Router memilih rute dengan *longest prefix match*, bukan berdasarkan jalur fisik terpendek. Jalur fisik ke Pelabuhan hanya dikenal sebagai route ringkas (di file static: `10.72.160.0/19 via 10.72.241.38`), sedangkan route menuju Pelabuhan lewat tunnel ditulis dengan next-hop `192.168.9.2` untuk prefix yang sama. Karena keduanya prefix sama, yang menentukan adalah *administrative distance*: static route (AD 1) mengalahkan rute hasil protokol dinamis, sehingga trafik Balai Kota ↔ Pelabuhan selalu masuk Tunnel0. Di file OSPF pun prinsipnya sama: static route via tunnel tetap dipertahankan dan mengalahkan rute OSPF (AD 110) untuk dua subnet Pelabuhan tersebut.

**Mengapa GRE saja tidak mengenkripsi?** GRE hanya **enkapsulasi**: paket IP asli dibungkus dengan header GRE dan header IP baru agar bisa dilewatkan melintasi jaringan transit. Isinya tetap plaintext dan dapat dibaca siapa pun yang menyadap link; GRE juga tidak punya mekanisme integritas (tidak ada HMAC) maupun autentikasi peer, sehingga paket palsu bisa disuntik ke tunnel. Enkripsi baru muncul ketika GRE dipadukan dengan IPsec: transform-set `esp-aes esp-sha-hmac` memberi kerahasiaan (AES) sekaligus integritas/autentikasi (SHA-HMAC) pada seluruh isi tunnel.

## 2. Layanan Aplikasi Smart City (Soal 8)

Semua layanan memakai domain `k9.smartcity.lab`, DNS di SERVER DC (`10.72.239.2`).

| Layanan | Lokasi | Konfigurasi | Bukti |
|---|---|---|---|
| DNS | SERVER DC | A record: `k9.smartcity.lab`, `www.k9…` → `10.72.241.2`; `ftp.k9…`, `mail.k9…` → `10.72.239.2` | `nslookup` dari semua wilayah menjawab IP benar |
| Web | SERVER BALAI KOTA (`10.72.241.2`) | HTTP+HTTPS On, `index.html` "Portal Smart City Surabaya – Kelompok 9" | Browser di 7 LAN memuat halaman (1492 byte) via `http://www.k9.smartcity.lab` |
| FTP | SERVER DC | User `cctv` (RWDNL), service On | Dari PC-CCTV-KOTA: `ftp ftp.k9.smartcity.lab` → login → `put rekaman-cctv-k9.txt` → *Transfer complete - 272 bytes* |
| Email | SERVER DC | Domain `k9.smartcity.lab`, SMTP+POP3 On, akun `user-pusat` & `user-pelabuhan` | Kirim-terima dua arah (screenshot) |

Email kirim-terima dua arah (SMTP resolving `mail.k9.smartcity.lab` → `10.72.239.2`, "Receive Mail Success"):
- Pusat → Pelabuhan: subjek "Laporan CCTV Kelompok 9" masuk di PC KANTOR — `screenshots/pt-email-kantor-read.png`.
- Pelabuhan → Pusat: subjek "Balasan Kantor Pelabuhan" masuk di PC - PEGAWAI — `screenshots/pt-email-pegawai-recv.png`.

## 3. OSPF + Link Cadangan L7 (Soal 7, file `K9_VLSM_OSPF.pkt`)

### Perubahan topologi
- Modul `HWIC-4ESW` dipasang di R-DC (ketiga GigabitEthernet sudah terpakai), kabel crossover **L7**: `R-DC Fa0/0/0 ↔ R-UTARA Fa0/3/1`, subnet `10.72.241.56/30` — R-UTARA `.57` (interface Vlan1), R-DC `.58` (interface Vlan1).

### Konfigurasi (pola yang sama di 7 router internal)
```
no ip route <semua static antar-router>          ! R-PUSAT kecuali default + 2 route tunnel
router ospf 1
 router-id <1..7>.1.1.1
 network 10.72.0.0 0.0.255.255 area 0
 passive-interface <interface LAN pengguna>
```
- R-PUSAT: `default-information originate` (default route ke ISP tetap static, hanya di R-PUSAT); passive: Vlan40, Vlan50.
- Passive-interface dipasang di semua interface menghadap LAN pengguna (R-DC Gi0/1-2, R-UTARA Gi0/2+Vlan60, R-PELABUHAN/SELATAN/TIMUR/BARAT Gi0/1-2).
- R-ISP tidak ikut OSPF dan tidak menerima rute privat (network statement hanya `10.72.0.0`).

### Bukti uji
- Adjacency R-PUSAT: 5 neighbor (DC, UTARA, SELATAN, TIMUR, BARAT) state 2WAY/FULL.
- `show ip route ospf` di R-DC: seluruh LAN tercatat sebagai `O`, default `O*E2 0.0.0.0/0 [110/1] via 10.72.241.33` — default tersebar otomatis dari R-PUSAT.
- Trafik Balai Kota → Pelabuhan tetap lewat tunnel (tracert hop 2 = `192.168.9.2`) karena static route via tunnel mengalahkan OSPF.

**Failover**: L1 (R-PUSAT Gi0/1) dimatikan, lalu dari PC - PEGAWAI:
```
ping 10.72.96.11
  Reply from 10.72.96.11 ... (3/4 reply, 1 timeout saat konvergensi)

tracert 10.72.96.11
  1   10.72.224.1     (R-PUSAT)
  2   10.72.241.38    (R-UTARA via L2)
  3   10.72.241.58    (R-DC via L7)
  4   10.72.96.11     (PC CCTV Kota)
```
Konektivitas pulih otomatis melalui L2 + L7 tanpa konfigurasi tambahan; setelah L1 dinyalakan ulang ping kembali 4/4.

## 4. Catatan Uji 2 (individu)

Skenario yang perlu dikuasai untuk demo perbaikan 10 menit:
1. **OSPF network statement salah** → cek `show ip ospf interface`, `show ip ospf neighbor`; perbaiki wildcard mask/network.
2. **DNS record menunjuk IP salah** → `nslookup` dari client, perbaiki A record di SERVER DC.
3. **Tunnel down (destination/source mismatch)** → `show interface Tunnel0` (up/down), cek route ke tujuan tunnel dan parameter `tunnel source/destination`.
