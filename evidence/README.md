# Bukti pengujian native Packet Tracer

Log berasal dari Cisco Packet Tracer **9.0.1.0858**. Prefix `static-` merujuk pada konfigurasi
`K9_VLSM.pkt`; prefix `ospf-` merujuk pada `K9_VLSM_OSPF.pkt`.
Ringkasan hasil dan batas pengujian terdapat di [README utama](../README.md).

## Asal bukti dan cara membacanya

Pengujian runtime menggunakan kandidat perbaikan di Packet Tracer. Kandidat kemudian diberi label,
disimpan secara native, dan diperiksa kesamaan running/startup-config pada router serta switch.
Modul scripting sementara dihapus dari hasil save. Perbandingan XML canonical memastikan isi lain tetap sama.
Kedua file final dibuka ulang secara native tanpa modul tersebut untuk uji GRE, internet, dan traceroute;
file static juga diperiksa sampai ISAKMP `QM_IDLE`.

- Log command menyimpan output asli dan metadata penyelesaian. `completed.status = 0` berarti command selesai;
  kelulusan ping ditentukan oleh statistik reply, bukan angka status itu.
  Dua record mesh mempunyai `completed: null` tetapi output statistik lengkap; keduanya diperiksa dari output ping.
- File mesh/internet memuat percobaan awal serta retry. Daftar dapat bersarang karena pengujian per putaran.
  Keberhasilan dihitung per pasangan sumber/tujuan, sehingga retry tidak menambah jumlah arah yang lolos.
- `*-http.json` memetakan nama endpoint langsung ke body HTML. Isinya bukan objek status HTTP.
- `*-addresses.json` memuat IP, mask, gateway, DNS, DHCP, dan status interface saat runtime.
  Varian `*-labeled-addresses.json` diambil setelah label final ditambahkan.
- `*-final-gui-*.json` berisi pembacaan OCR screenshot. OCR kadang membaca angka `0` sebagai `@`;
  screenshot native menjadi rujukan visual. Output awal yang gagal tetap dipertahankan.
- Waktu IOS dan tanggal mailbox mengikuti waktu simulator.

[runtime-checks.txt](runtime-checks.txt) mencatat pemeriksaan pasangan ping unik, DNS, HTTP, DHCP,
dan upload pada log yang disalin. [artifact-sha256.txt](artifact-sha256.txt) mengidentifikasi dua `.pkt`
final, workbook, sumber portal, dan payload FTP. Dari root repository, periksa dengan:

```sh
sha256sum -c evidence/artifact-sha256.txt
```

[validator-tests.txt](validator-tests.txt) memuat hasil delapan test serta kontrol mutasi kode:
pembalikan pemeriksaan route ISP sengaja dibuat dalam memori dan berhasil dideteksi test regresi.
Tool `ruff` dan `markdownlint` tidak tersedia; link lokal, anchor heading, dan keseimbangan code fence diperiksa terpisah.

## Konektivitas dan layanan

| Pemeriksaan | Static | OSPF |
|---|---|---|
| Semua pasangan endpoint | [Mesh](static-mesh.json) | [Mesh](ospf-mesh.json) |
| Internet | [Ping](static-internet.json) | [Ping](ospf-internet.json) |
| IP runtime final berlabel | [Alamat](static-labeled-addresses.json) | [Alamat](ospf-labeled-addresses.json) |
| Renew DHCP | [Renew](static-dhcp-renew.json) | [Renew](ospf-dhcp-renew.json) |
| IP setelah renew | [Alamat](static-after-renew-addresses.json) | [Alamat](ospf-after-renew-addresses.json) |
| DNS `www` | [Lookup](static-dns-www.json) | [Lookup](ospf-dns-www.json) |
| DNS `ftp` | [Lookup](static-dns-ftp.json) | [Lookup](ospf-dns-ftp.json) |
| DNS `mail` | [Lookup](static-dns-mail.json) | [Lookup](ospf-dns-mail.json) |
| HTTP portal | [Body](static-http.json) | [Body](ospf-http.json) |
| FTP | [Login/upload](static-ftp.json) | [Login/upload](ospf-ftp.json) |
| Email | [Mailbox](static-email.json) | [Mailbox final](ospf-email-final.json) |
| NAT dan isolasi R-ISP | [Output](static-nat-isp.json) | [Output](ospf-nat-isp.json) |

Mesh mencakup 15 endpoint internal, sehingga terdapat `15 × 14 = 210` pasangan terarah.
Log static memuat 222 hasil ping dan OSPF 212 hasil ping; masing-masing memiliki 210 pasangan sukses 4/4.
Internet memiliki 15 sumber sukses per file. Uji DHCP menggunakan CCTV, Kantor Pelabuhan, dan WiFi Utara
sebagai perwakilan; kapasitas 6.000/125 lease diperiksa dari konfigurasi, bukan uji beban ribuan klien.

## Routing, GRE, dan failover

- Static: [route PUSAT](static-routes-pusat.json), [route UTARA](static-routes-utara.json),
  [route ISP](static-routes-isp.json), [traceroute GRE dua arah](static-gre-traces.json).
- IPsec: [counter sebelum](static-crypto-before.json), [traffic uji](static-crypto-traffic.json),
  [counter sesudah](static-crypto-after.json).
- OSPF normal: [proses dan neighbor](ospf-neighbors-pusat.json),
  [route PUSAT](ospf-routes-pusat.json), [route DC](ospf-routes-dc.json),
  [route PELABUHAN](ospf-routes-pelabuhan.json).
- L1 down: [shutdown](ospf-l1-evidence-shutdown.json), [interface/route](ospf-l1-evidence-routes.json),
  [trace dan ping CCTV](ospf-l1-evidence-trace.json), [GRE/internet](ospf-l1-evidence-pings.json),
  [restorasi](ospf-l1-evidence-restoration.json), [setelah pulih](ospf-l1-evidence-restored.json).
- L2 down: [route/neighbor](ospf-l2-down-routes.json), [traceroute](ospf-l2-down-traces.json),
  [ping](ospf-l2-down-pings.json), [pemulihan](ospf-l2-restored.json).
- [Route setelah kedua skenario dipulihkan](ospf-restored-routes.json).

Pengujian L1 dan L2 dilakukan terpisah. Screenshot utama:
[L1](../screenshots/ospf-l1-failover.png), [route L1](../screenshots/ospf-l1-routes.png),
[L2/Tunnel1](../screenshots/ospf-l2-trace-screen.png).
Penjelasan jalur serta batas single-link L3 sampai L6 ada di
[laporan Anggota C](../AnggotaC_GRE_OSPF_Layanan.md#35-uji-kegagalan-l1-dan-l2-secara-terpisah).

## Power-cycle dan pembukaan ulang file final

Log `static-recovery-*.json` mempertahankan diagnosis, percobaan startup-copy, reapply,
warm-up, serta pengulangan pemulihan. Urutan bukti utama:

1. [Running/startup sebelum reapply pada pengulangan](static-recovery-repeat-before.json).
2. [Startup-copy belum memulihkan crypto](static-recovery-copy-check.json).
3. [Perintah reapply lengkap](static-recovery-repeat-reapply.json).
4. [Retry ping](static-recovery-repeat-pings.json) dan [hasil stabil](static-recovery-stable.json).
5. [SA setelah reapply](static-recovery-repeat-after.json),
   [counter sebelum traffic](static-recovery-crypto-before.json),
   [counter sesudah traffic](static-recovery-crypto-after.json).

Urutan operasional pemulihan tersedia di
[laporan Anggota C](../AnggotaC_GRE_OSPF_Layanan.md#15-pemulihan-ipsec-setelah-power-cycle-packet-tracer).

Smoke test setelah modul scripting dihapus:

- Static: [log GUI](static-final-gui-smoke.json), [ISAKMP](static-final-gui-isakmp.json),
  [screenshot GRE](../screenshots/static-final-gui-gre.png),
  [internet](../screenshots/static-final-gui-internet.png),
  [trace](../screenshots/static-final-gui-trace.png).
- OSPF: [percobaan awal](ospf-final-gui-first.json), [log GUI stabil](ospf-final-gui-smoke.json),
  [screenshot GRE](../screenshots/ospf-final-gui-gre.png),
  [internet](../screenshots/ospf-final-gui-internet.png),
  [trace](../screenshots/ospf-final-gui-trace.png).
