# Mid Project Jarkom — Smart City Surabaya (Kelompok 9, K = 9)

Skema: **VLSM**, blok dasar `10.72.0.0/16`. Domain internal `k9.smartcity.lab`.

## Isi
- `K9_VLSM.pkt` — file utama: static routing, NAT, DHCP, tunnel GRE + IPsec, layanan aplikasi (DNS, Web, FTP, Email).
- `K9_VLSM_OSPF.pkt` — soal 7: link cadangan L7 (R-DC ↔ R-UTARA, `10.72.241.56/30`) + OSPF + uji failover.
- `K9_Subnetting.xlsx` — tabel VLSM/CIDR, supernet, dan tabel revisi UTS.
- `AnggotaA_Routing_NAT.md` — tabel subnetting, static routing, NAT (Anggota A).
- `AnggotaC_GRE_OSPF_Layanan.md` — GRE + IPsec, OSPF + L7, layanan aplikasi + bukti uji (Anggota C).
- `K9_PT_Config.md` — panduan konfigurasi per perangkat (pemetaan port, DHCP, routing).
- `screenshots/` — bukti pengujian.

## Pengalamatan tambahan
| Kebutuhan | Alamat |
|---|---|
| Link R-PUSAT–R-ISP | `203.0.113.36/30` (PUSAT `.37`, ISP `.38`) |
| Server internet | `8.8.8.8/24`, gateway `8.8.8.1` |
| Tunnel GRE | `192.168.9.0/30` (PUSAT `.1`, PELABUHAN `.2`) |
| Link cadangan L7 (OSPF) | `10.72.241.56/30` (UTARA `.57`, DC `.58`) |

## Verifikasi ringkas
- Semua LAN saling ping; semua host `ping 8.8.8.8` via NAT overload (`203.0.113.37`).
- Traceroute Balai Kota ↔ Pelabuhan melewati tunnel (`192.168.9.x`); IPsec SA `QM_IDLE/ACTIVE`, counter encrypt bertambah.
- OSPF: 5 neighbor di R-PUSAT, default tersebar via `default-information originate`; link L1 diputus → trafik pulih via L2 + L7 otomatis.
