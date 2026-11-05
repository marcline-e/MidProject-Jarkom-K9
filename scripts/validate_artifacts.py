"""Check saved K9 addressing and configurations; native evidence is in evidence/."""

import re
import sys
from collections import Counter
from ipaddress import IPv4Address, IPv4Interface, IPv4Network
from itertools import combinations
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

from pkt_core import Lab


ROOT = Path(__file__).resolve().parents[1]
NS = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
REL = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
HOST_LANS = {
    "HP-WIFI-UTARA": "WiFi Publik Utara",
    "HP-WIFI-SELATAN": "WiFi Publik Selatan",
    "CCTV KOTA": "CCTV Kota",
    "HP-WIFI-TIMUR": "WiFi Publik Timur",
    "SCADA PELABUHAN": "Sensor dan SCADA Pelabuhan",
    "HP-WIFI-BARAT": "WiFi Publik Barat",
    "PC - PEGAWAI": "Pegawai Balai Kota",
    "SENSOR BANJIR": "Sensor Banjir Timur",
    "SENSOR LANTAS UTARA": "Sensor Lalu Lintas Utara",
    "PUSKESMAS": "Puskesmas dan Sekolah Barat",
    "SERVER DC": "Server dan Storage DC",
    "PC KANTOR": "Kantor Pelabuhan",
    "PJU SELATAN": "PJU Pintar Selatan",
    "SERVER BALAI KOTA": "Server Balai Kota",
    "SEKOLAH": "Puskesmas dan Sekolah Barat",
}


def read_workbook(path: Path) -> dict[str, dict[str, str]]:
    # shortcut: use cached formula values; recalculate in Excel after changing formulas.
    with ZipFile(path) as archive:
        strings = [
            "".join(node.itertext())
            for node in ET.fromstring(archive.read("xl/sharedStrings.xml")).findall("s:si", NS)
        ]
        targets = {
            node.attrib["Id"]: node.attrib["Target"]
            for node in ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        }
        sheets = {}
        for sheet in ET.fromstring(archive.read("xl/workbook.xml")).findall("s:sheets/s:sheet", NS):
            target = targets[sheet.attrib[REL]]
            xml = archive.read(target.lstrip("/") if target.startswith("/") else "xl/" + target)
            cells = {}
            for cell in ET.fromstring(xml).findall(".//s:sheetData/s:row/s:c", NS):
                value = cell.findtext("s:v", namespaces=NS)
                assert cell.attrib.get("t") != "e", (sheet.attrib["name"], cell.attrib["r"], value)
                assert cell.find("s:f", NS) is None or value is not None, "Missing formula cache"
                if cell.attrib.get("t") == "inlineStr":
                    value = "".join(cell.find("s:is", NS).itertext())
                if value is not None:
                    cells[cell.attrib["r"]] = strings[int(value)] if cell.attrib.get("t") == "s" else value
            sheets[sheet.attrib["name"]] = cells
    return sheets


def validate_workbook(sheets: dict[str, dict[str, str]]) -> dict[str, IPv4Network]:
    requirements = sheets["Kebutuhan"]
    assert requirements["B2"] == "9" and requirements["B5"] == "10.72.0.0"
    hosts = {requirements[f"C{i}"]: int(requirements[f"D{i}"]) for i in range(8, 28)}
    assert len(hosts) == 20 and sum(hosts.values()) == 42092
    allocations = {}
    for name, parent in (("VLSM", "10.72.0.0/16"), ("CIDR", "10.72.0.0/14")):
        sheet = sheets[name]
        networks = {}
        for i in range(5, 25):
            subnet = sheet[f"C{i}"]
            network = IPv4Network(f'{sheet[f"H{i}"]}/{sheet[f"E{i}"]}')
            assert int(sheet[f"D{i}"]) == hosts[subnet], (name, subnet, "host count")
            assert network.prefixlen == 32 - (hosts[subnet] + 1).bit_length(), (name, subnet, "prefix")
            expected = {
                "F": network.netmask, "G": network.num_addresses,
                "I": network[1], "J": network[-2], "K": network.broadcast_address,
                "L": network[1], "M": int(network.network_address),
            }
            for column, value in expected.items():
                assert sheet[f"{column}{i}"] == str(value), (name, f"{column}{i}", value)
            assert network.subnet_of(IPv4Network(parent)), (name, subnet, "parent")
            if name == "CIDR":
                assert network.subnet_of(IPv4Network(sheet[f"N{i}"])), (subnet, "router supernet")
            networks[subnet] = network
        assert set(networks) == set(hosts)
        assert all(not a.overlaps(b) for a, b in combinations(networks.values(), 2)), name + " overlap"
        assert sum(n.num_addresses for n in networks.values()) == 61752
        allocations[name] = networks
    vlsm = sheets["VLSM"]
    assert [vlsm[f"D{i}"] for i in (26, 27, 28, 29, 31)] == ["42092", "61752", "16", "65536", "23444"]
    assert float(vlsm["D30"]) == 42092 / 65536 and vlsm["D32"] == "10.72.241.56"
    tree = sheets["Supernet CIDR"]
    supernets = {tree[f"A{i}"].strip(): IPv4Network(tree[f"I{i}"]) for i in range(5, 17)}
    for i in range(5, 17):
        name = tree[f"A{i}"].strip()
        network = supernets[name]
        children = [
            (supernets | allocations["CIDR"])[child.strip()]
            for child in tree[f"C{i}"].split(",")
        ]
        size = sum(child.num_addresses for child in children)
        assert size == int(tree[f"D{i}"]) and network.prefixlen == 32 - (size - 1).bit_length(), name
        assert all(child.subnet_of(network) for child in children), name
        assert all(not a.overlaps(b) for a, b in combinations(children, 2)), name
        for column, value in {"E": network.prefixlen, "F": network.num_addresses,
                              "G": network.network_address, "H": network.broadcast_address}.items():
            assert tree[f"{column}{i}"] == str(value), (name, column)
        if tree[f"B{i}"] != "-":
            assert network.subnet_of(supernets[tree[f"B{i}"]]), name
    assert all(sheets["Revisi"].get(f"{column}{i}") for i in range(5, 17) for column in "BCDEF")
    return allocations["VLSM"]


def config(engine: ET.Element, kind: str = "RUNNINGCONFIG") -> str:
    return "\n".join((line.text or "").rstrip() for line in engine.findall(f"{kind}/LINE"))


def sections(text: str, prefix: str) -> dict[str, list[str]]:
    result = {}
    current = None
    for line in text.splitlines():
        if line.startswith(prefix):
            current = line[len(prefix):]
            result[current] = []
        elif line.startswith(" ") and current is not None:
            result[current].append(line.strip())
        else:
            current = None
    return result


def interfaces(text: str) -> dict[str, IPv4Interface]:
    return {
        name: IPv4Interface("/".join(line.split()[2:4]))
        for name, lines in sections(text, "interface ").items()
        for line in lines if line.startswith("ip address ")
    }


def validate_topology(lab: Lab, sheets: dict[str, dict[str, str]], ospf: bool) -> None:
    engines = {device.findtext("ENGINE/NAME"): device.find("ENGINE") for device in lab.devs}
    assert len(engines) == 45, "Device inventory"
    assert Counter(e.findtext("TYPE") for e in engines.values()) == {
        "Router": 8, "Switch": 14, "AccessPoint": 4, "Pda": 4,
        "Pc": 9, "Server": 3, "Power Distribution Device": 3,
    }, "Device types"
    assert lab.base.find("SCRIPT_MODULE") is None, "Temporary scripting module remains"
    references = {e.findtext("SAVE_REF_ID"): name for name, e in engines.items()}
    cables = lab.base.findall("NETWORK/LINKS/LINK/CABLE")
    assert len(cables) == 37 + ospf, "Wired link count"
    backbone = set()
    occupied = set()
    for cable in cables:
        assert cable.findtext("FUNCTIONAL") == "true", "Disabled cable"
        ports = cable.findall("PORT")
        ends = ((references[cable.findtext("FROM")], ports[0].text),
                (references[cable.findtext("TO")], ports[1].text))
        for end in ends:
            assert end not in occupied, (end, "Port used twice")
            occupied.add(end)
        if all(name.startswith("R-") for name, _ in ends):
            backbone.add(frozenset(ends))
    expected = [
        ("R-PUSAT", "GigabitEthernet0/0", "R-ISP", "GigabitEthernet0/0"),
        ("R-PUSAT", "GigabitEthernet0/1", "R-DC", "GigabitEthernet0/0"),
        ("R-PUSAT", "GigabitEthernet0/2", "R-UTARA", "GigabitEthernet0/0"),
        ("R-PUSAT", "FastEthernet0/0/0", "R-SELATAN", "GigabitEthernet0/0"),
        ("R-PUSAT", "FastEthernet0/0/1", "R-TIMUR", "GigabitEthernet0/0"),
        ("R-PUSAT", "FastEthernet0/0/2", "R-BARAT", "GigabitEthernet0/0"),
        ("R-UTARA", "GigabitEthernet0/1", "R-PELABUHAN", "GigabitEthernet0/0"),
    ]
    if ospf:
        expected.append(("R-DC", "FastEthernet0/0/0", "R-UTARA", "FastEthernet0/3/1"))
    assert backbone == {frozenset(((a, ap), (b, bp))) for a, ap, b, bp in expected}, "L1-L7 wiring"
    addresses = {}
    for name, engine in engines.items():
        if engine.findtext("TYPE") not in ("Router", "Switch"):
            continue
        text = config(engine)
        assert text == config(engine, "STARTUPCONFIG"), (name, "Running/startup mismatch")
        assert "hostname " + name.replace(" ", "-") in text.splitlines(), (name, "Hostname")
        addresses[name] = interfaces(text)
        for port, lines in sections(text, "interface ").items():
            if port in addresses[name]:
                assert "shutdown" not in lines, (name, port, "Shutdown IP interface")
    assert "description " not in "\n".join(sections(config(engines["R-PUSAT"]), "interface ")["FastEthernet0/2/0"])
    sheet = sheets["IP Interface VLSM"]
    for i in range(5, 37):
        name = sheet[f"A{i}"]
        expected_ip = IPv4Interface(f'{sheet[f"D{i}"]}/{sheet[f"E{i}"]}')
        assert expected_ip.network.prefixlen == int(sheet[f"F{i}"]), (name, "Sheet prefix")
        if name == "Server 8.8.8.8":
            port = engines["SERVER-INTERNET"].find(".//PORT[TYPE='eCopperFastEthernet']")
            assert expected_ip == IPv4Interface(f'{port.findtext("IP")}/{port.findtext("SUBNET")}')
        elif " Tunnel" in name:
            router, port = name.split()
            assert addresses[router][port] == expected_ip, name
        else:
            assert expected_ip in addresses[name].values(), (name, str(expected_ip))
    labels = {node.findtext("TEXT") for node in lab.base.findall("PHYSICALWORKSPACE/NOTES/NOTE")}
    for i in range(5, 19):
        vlsm = sheets["VLSM"]
        label = f'{vlsm[f"C{i}"]}\n{vlsm[f"H{i}"]}/{vlsm[f"E{i}"]}\n{vlsm[f"D{i}"]} host'
        assert label in labels, ("LAN label", label)
    for region, ap in (("UTARA", "AP-UTARA"), ("SELATAN", "AP SELATAN"),
                       ("TIMUR", "AP TIMUR"), ("BARAT", "AP BARAT")):
        phone = engines["HP-WIFI-" + region]
        assert phone.findtext("WIRELESS_CLIENT/WIRELESS_COMMON/SSID") == "K9-WIFI-" + region
        assert engines[ap].findtext("WIRELESS_SERVER/WIRELESS_COMMON/SSID") == "K9-WIFI-" + region


def validate_services(lab: Lab, sheets: dict[str, dict[str, str]], subnets: dict[str, IPv4Network]) -> None:
    engines = {device.findtext("ENGINE/NAME"): device.find("ENGINE") for device in lab.devs}
    required = {sheets["VLSM"][f"C{i}"]: int(sheets["VLSM"][f"D{i}"]) for i in range(5, 19)}
    for name, lan in HOST_LANS.items():
        engine = engines[name]
        port_type = "eHostWirelessN" if name.startswith("HP-") else "eCopperFastEthernet"
        port = engine.find(f".//PORT[TYPE='{port_type}']")
        assert port is not None and port.findtext("POWER") == "true", (name, "Host port")
        assert engine.findtext("GATEWAY") == str(subnets[lan][1]), (name, "Gateway")
        assert engine.findtext("DNS_CLIENT/SERVER_IP") == "10.72.239.2", (name, "DNS client")
        assert port.findtext("PORT_DHCP_ENABLE") == str(not name.startswith("SERVER")).lower(), name
        if name.startswith("SERVER"):
            assert IPv4Interface(f'{port.findtext("IP")}/{port.findtext("SUBNET")}') == IPv4Interface(
                f"{subnets[lan][2]}/{subnets[lan].prefixlen}"
            ), (name, "Static address")
    internet = engines["SERVER-INTERNET"]
    assert internet.findtext("GATEWAY") == "8.8.8.1"
    assert internet.findtext(".//PORT[TYPE='eCopperFastEthernet']/PORT_DHCP_ENABLE") == "false"
    router_pools = set()
    for name, engine in engines.items():
        if engine.findtext("TYPE") != "Router":
            continue
        text = config(engine)
        excluded = set()
        for line in text.splitlines():
            if line.startswith("ip dhcp excluded-address "):
                values = line.split()[3:]
                excluded.update(IPv4Address(ip) for ip in range(int(IPv4Address(values[0])),
                                                               int(IPv4Address(values[-1])) + 1))
        for pool, lines in sections(text, "ip dhcp pool ").items():
            network_line = next(line for line in lines if line.startswith("network "))
            network = IPv4Network("/".join(network_line.split()[1:]))
            lan = next(lan for lan in required if subnets[lan] == network)
            assert network not in router_pools, (pool, "Duplicate DHCP network")
            router_pools.add(network)
            assert network in {ip.network for ip in interfaces(text).values()}, (name, pool, "Local LAN")
            assert f"default-router {network[1]}" in lines and "dns-server 10.72.239.2" in lines, pool
            assert network[1] in excluded, (pool, "Gateway not excluded")
            capacity = network.num_addresses - 2 - sum(network[0] < ip < network[-1] for ip in excluded)
            assert capacity >= required[lan], (pool, "DHCP capacity", capacity, required[lan])
    server_lans = {"CCTV Kota", "Server dan Storage DC", "Server Balai Kota"}
    assert router_pools == {subnets[lan] for lan in required.keys() - server_lans}, "Router DHCP coverage"
    dc = engines["SERVER DC"]
    dhcp = dc.find("DHCP_SERVERS/ASSOCIATED_PORTS/ASSOCIATED_PORT/DHCP_SERVER")
    assert dhcp.findtext("ENABLED") == "1", "DC DHCP disabled"
    pools = {pool.findtext("NAME"): pool for pool in dhcp.findall("POOLS/POOL")}
    for name, lan, start in (("POOL-CCTV", "CCTV Kota", "10.72.96.11"),
                             ("serverPool", "Server dan Storage DC", "10.72.239.3")):
        pool = pools[name]
        network = subnets[lan]
        first, last = IPv4Address(pool.findtext("START_IP")), IPv4Address(pool.findtext("END_IP"))
        size = int(pool.findtext("MAX_USERS"))
        assert size >= required[lan], (name, "DHCP capacity", size, required[lan])
        assert str(first) == start and last == first + size - 1, (name, "DHCP range")
        assert network[1] < first <= last < network[-1], (name, "Lease range crosses subnet")
        assert pool.findtext("MASK") == str(network.netmask) and pool.findtext("NETWORK") == str(network[0])
        assert pool.findtext("DEFAULT_ROUTER") == str(network[1]) and pool.findtext("DNS_SERVER") == "10.72.239.2"
    dc_interfaces = sections(config(engines["R-DC"]), "interface ")
    assert "ip helper-address 10.72.239.2" in dc_interfaces["GigabitEthernet0/2"], "CCTV DHCP relay"
    records = {record.findtext("NAME"): record.findtext("IPADDRESS")
               for record in dc.findall("DNS_SERVER/NAMESERVER-DATABASE/RESOURCE-RECORD")}
    assert dc.findtext("DNS_SERVER/ENABLED") == "1" and records == {
        "k9.smartcity.lab": "10.72.241.2", "www.k9.smartcity.lab": "10.72.241.2",
        "ftp.k9.smartcity.lab": "10.72.239.2", "mail.k9.smartcity.lab": "10.72.239.2",
    }, "DNS records"
    web = engines["SERVER BALAI KOTA"]
    assert web.findtext("HTTP_SERVER/ENABLED") == "1" and web.findtext("HTTPS_SERVER/HTTPSENABLED") == "1"
    page = web.find("FILE_MANAGER//FILE[NAME='index.html']/FILE_CONTENT/TEXT")
    assert page.text.strip() == (ROOT / "portal/index.html").read_text().strip(), "Embedded portal differs"
    assert dc.findtext("FTP_SERVER/ENABLED") == "1"
    account = dc.find("FTP_SERVER/USER_ACCOUNT_MNGR/ACCOUNT[USERNAME='cctv']")
    assert account.findtext("PASSWORD") == "K9-CCTV-Lab!" and "W" in account.findtext("PERMISSIONS"), "FTP upload user"
    assert all(engines[name].findtext("FTP_SERVER/ENABLED") == "0"
               for name in ("SERVER BALAI KOTA", "SERVER-INTERNET")), "Unnecessary FTP service"
    mail = dc.find("EMAIL_SERVER")
    assert mail.findtext("SMTP_ENABLED") == mail.findtext("POP3_ENABLED") == "1"
    assert mail.findtext("SMTP_DOMAIN") == "k9.smartcity.lab"
    users = {mail.findtext(f"USER{i}"): mail.findtext(f"PASSWORD{i}") for i in range(int(mail.findtext("NO_OF_USERS")))}
    for host, user in (("PC - PEGAWAI", "user-pusat"), ("PC KANTOR", "user-pelabuhan")):
        client = engines[host].find("EMAIL_CLIENT")
        assert client.findtext("USER") == user and client.findtext("PASSWORD") == users[user], host
        assert client.findtext("MAIL_ID") == user + "@k9.smartcity.lab", host
        assert client.findtext("POP3_SERVER") == client.findtext("SMTP_SERVER") == "mail.k9.smartcity.lab", host


def validate_routing(lab: Lab, subnets: dict[str, IPv4Network], ospf: bool) -> None:
    texts = {d.findtext("ENGINE/NAME"): config(d.find("ENGINE")) for d in lab.devs
             if d.findtext("ENGINE/TYPE") == "Router"}
    ports = {name: interfaces(text) for name, text in texts.items()}
    routes = {name: [(IPv4Network(f"{fields[2]}/{fields[3]}"), IPv4Address(fields[4]))
                     for line in text.splitlines() if line.startswith("ip route ")
                     for fields in [line.split()]] for name, text in texts.items()}
    assert not routes["R-ISP"] and "router ospf" not in texts["R-ISP"], "ISP must not route private networks"
    assert {ip.network for ip in ports["R-ISP"].values()} == {
        IPv4Network("203.0.113.36/30"), IPv4Network("8.8.8.0/24"),
    }, "ISP connected networks"
    pusat = texts["R-PUSAT"]
    assert "access-list 1 permit 10.72.0.0 0.0.255.255" in pusat.splitlines(), "NAT ACL"
    assert "ip nat inside source list 1 interface GigabitEthernet0/0 overload" in pusat.splitlines(), "NAT overload"
    nat_ports = sections(pusat, "interface ")
    assert "ip nat outside" in nat_ports["GigabitEthernet0/0"]
    for port in ("GigabitEthernet0/1", "GigabitEthernet0/2", "Vlan10", "Vlan20", "Vlan30", "Vlan40", "Vlan50"):
        assert "ip nat inside" in nat_ports[port], (port, "NAT inside")
    for name, source, peer, own, backup_source, backup_peer, backup_ip in (
        ("R-PUSAT", "GigabitEthernet0/2", "10.72.241.54", "10.72.241.37",
         "GigabitEthernet0/1", "10.72.241.54", "192.168.9.5/30"),
        ("R-PELABUHAN", "GigabitEthernet0/0", "10.72.241.37", "10.72.241.54",
         "GigabitEthernet0/0", "10.72.241.33", "192.168.9.6/30"),
    ):
        text = texts[name]
        blocks = sections(text, "interface ")
        assert "tunnel source " + source in blocks["Tunnel0"], (name, "GRE source")
        assert "tunnel destination " + peer in blocks["Tunnel0"], (name, "GRE destination")
        assert str(ports[name][source].ip) == own
        if ospf:
            assert ports[name]["Tunnel1"] == IPv4Interface(backup_ip), (name, "Backup GRE IP")
            assert "tunnel source " + backup_source in blocks["Tunnel1"], (name, "Backup GRE source")
            assert "tunnel destination " + backup_peer in blocks["Tunnel1"], (name, "Backup GRE peer")
            assert not re.search(r"(?m)^\s*crypto ", text), (name, "OSPF must use GRE without IPsec")
        else:
            assert "Tunnel1" not in blocks, (name, "Backup GRE belongs only in OSPF")
            assert {"encr aes", "authentication pre-share", "group 5"} <= set(sections(text, "crypto isakmp policy ")["10"])
            assert f"crypto isakmp key K9-GRE-IPsec-Lab! address {peer}" in text.splitlines(), (name, "IPsec PSK")
            assert "crypto ipsec transform-set K9-GRE esp-aes esp-sha-hmac" in text.splitlines()
            assert "mode transport" not in text, "Verified IPsec mode is tunnel"
            assert {"set peer " + peer, "set transform-set K9-GRE", "match address 110"} <= set(
                sections(text, "crypto map ")["K9-IPSEC 10 ipsec-isakmp"]
            ), (name, "Crypto map")
            assert f"access-list 110 permit gre host {own} host {peer}" in text.splitlines(), (name, "GRE crypto ACL")
            assert "crypto map K9-IPSEC" in blocks[source], (name, "Crypto binding")
    if ospf:
        assert ports["R-DC"]["Vlan1"] == IPv4Interface("10.72.241.58/30")
        assert ports["R-UTARA"]["Vlan1"] == IPv4Interface("10.72.241.57/30")
        for name, text in texts.items():
            if name == "R-ISP":
                continue
            assert routes[name] == ([(IPv4Network("0.0.0.0/0"), IPv4Address("203.0.113.38"))]
                                    if name == "R-PUSAT" else []), (name, "OSPF static route remains")
            processes = sections(text, "router ospf ")
            endpoint = name in ("R-PUSAT", "R-PELABUHAN")
            assert set(processes) == ({"1", "2"} if endpoint else {"1"}), (name, "OSPF processes")
            assert ("default-information originate" in processes["1"]) == (name == "R-PUSAT")
            if endpoint:
                assert "redistribute ospf 2 subnets" in processes["1"], (name, "LAN redistribution")
                assert not any(line.startswith("redistribute ") for line in processes["2"]), "Recursive GRE underlay import"
                assert "distance 100" in processes["2"], (name, "GRE route preference")
            networks = {}
            for process, lines in processes.items():
                networks[process] = []
                for line in lines:
                    if line.startswith("network "):
                        _, address, wildcard, area, number = line.split()
                        assert area == "area" and number == "0", (name, "OSPF area")
                        mask = IPv4Address(0xFFFFFFFF ^ int(IPv4Address(wildcard)))
                        networks[process].append(IPv4Network(f"{address}/{mask}"))
            for port, address in ports[name].items():
                if address.ip == IPv4Address("203.0.113.37"):
                    expected = set()
                else:
                    overlay = endpoint and (port.startswith("Tunnel") or address.network in subnets.values()
                                            and address.network.prefixlen < 30)
                    expected = {"2" if overlay else "1"}
                actual = {process for process, nets in networks.items() if any(address.ip in net for net in nets)}
                assert actual == expected, (name, port, "OSPF underlay/overlay separation", actual, expected)
                if address.network in subnets.values() and address.network.prefixlen < 30:
                    assert all("passive-interface " + port in processes[process] for process in actual), (name, port, "Passive LAN")
    else:
        assert all("router ospf" not in text for text in texts.values()), "OSPF in static file"
        upstreams = {"R-PUSAT": "203.0.113.38", "R-DC": "10.72.241.33", "R-UTARA": "10.72.241.37",
                     "R-PELABUHAN": "10.72.241.53", "R-SELATAN": "10.72.241.41",
                     "R-TIMUR": "10.72.241.45", "R-BARAT": "10.72.241.49"}
        for name, upstream in upstreams.items():
            assert [hop for net, hop in routes[name] if net.prefixlen == 0] == [IPv4Address(upstream)], (name, "Upstream default")
        assert "ip route 10.72.241.54 255.255.255.255 10.72.241.38" in pusat.splitlines()
        assert "ip route 10.72.241.37 255.255.255.255 10.72.241.53" in texts["R-PELABUHAN"].splitlines()
        for router, next_hop, lans in (
            ("R-PUSAT", "192.168.9.2", ("Sensor dan SCADA Pelabuhan", "Kantor Pelabuhan")),
            ("R-PELABUHAN", "192.168.9.1", ("Pegawai Balai Kota", "Server Balai Kota")),
        ):
            for lan in lans:
                assert [(net, hop) for net, hop in routes[router] if net == subnets[lan]] == [
                    (subnets[lan], IPv4Address(next_hop))
                ], (router, lan, "GRE LAN route")
        owners = {address.ip: name for name, values in ports.items() for address in values.values()}
        lans = {lan: next(name for name, values in ports.items()
                          if any(ip.network == subnets[lan] for ip in values.values())) for lan in set(HOST_LANS.values())}
        assert {subnets[lan] for lan, owner in lans.items() if owner != "R-PUSAT"} <= {
            net for net, _ in routes["R-PUSAT"]
        }, "PUSAT needs routes to every remote LAN"
        for lan in ("Sensor dan SCADA Pelabuhan", "Kantor Pelabuhan"):
            assert (subnets[lan], IPv4Address("10.72.241.54")) in routes["R-UTARA"], (lan, "UTARA downstream route")
        for source, target in ((a, b) for a in lans for b in lans):
            router, visited = lans[source], set()
            destination = subnets[target][2]
            while not any(destination in ip.network for ip in ports[router].values()):
                assert router not in visited, (source, target, "Routing loop", visited)
                visited.add(router)
                matches = sorted((net.prefixlen, hop) for net, hop in routes[router] if destination in net)
                assert matches, (source, target, router, "No route")
                hop = matches[-1][1]
                assert any(hop in ip.network for ip in ports[router].values()), (router, hop, "Unreachable next-hop")
                router = owners[hop]
            assert router == lans[target], (source, target, "Wrong destination router")


if __name__ == "__main__":
    if not __debug__:
        raise SystemExit("Run without -O: validation requires assertions.")
    workbook = read_workbook(ROOT / "K9_Subnetting.xlsx")
    subnets = validate_workbook(workbook)
    print("PASS workbook: 20 VLSM + 20 CIDR allocations, 12 supernets, 12 revision rows")
    paths = [Path(arg) for arg in sys.argv[1:]] or [ROOT / name for name in ("K9_VLSM.pkt", "K9_VLSM_OSPF.pkt")]
    for path in paths:
        lab = Lab(seed=path)
        validate_topology(lab, workbook, path.name.endswith("_OSPF.pkt"))
        validate_services(lab, workbook, subnets)
        validate_routing(lab, subnets, path.name.endswith("_OSPF.pkt"))
        print(f"PASS {path.name}: topology, 32 interface assignments, startup, DHCP, services, routing, NAT/GRE")
