import copy
import sys
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import validate_artifacts as check


class ArtifactValidatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.sheets = check.read_workbook(check.ROOT / "K9_Subnetting.xlsx")
        cls.subnets = check.validate_workbook(cls.sheets)
        cls.static = check.Lab(seed=check.ROOT / "K9_VLSM.pkt")
        cls.ospf = check.Lab(seed=check.ROOT / "K9_VLSM_OSPF.pkt")

    def test_final_artifacts(self) -> None:
        for lab, ospf in ((self.static, False), (self.ospf, True)):
            with self.subTest(ospf=ospf):
                check.validate_topology(lab, self.sheets, ospf)
                check.validate_services(lab, self.sheets, self.subnets)
                check.validate_routing(lab, self.subnets, ospf)

    def test_rejects_host_range_beyond_broadcast(self) -> None:
        sheets = copy.deepcopy(self.sheets)
        sheets["VLSM"]["J18"] = "10.72.241.32"
        with self.assertRaisesRegex(AssertionError, "J18"):
            check.validate_workbook(sheets)

    def test_rejects_insufficient_cctv_leases(self) -> None:
        lab = copy.deepcopy(self.static)
        pool = lab.base.find(".//DHCP_SERVERS//POOL[NAME='POOL-CCTV']")
        pool.find("MAX_USERS").text = "512"
        with self.assertRaisesRegex(AssertionError, "DHCP capacity"):
            check.validate_services(lab, self.sheets, self.subnets)

    def test_rejects_kantor_exclusions_leaving_only_116_leases(self) -> None:
        lab = copy.deepcopy(self.static)
        line = next(line for line in lab.base.findall(".//RUNNINGCONFIG/LINE")
                    if line.text == "ip dhcp excluded-address 10.72.240.1")
        line.text += " 10.72.240.10"
        with self.assertRaisesRegex(AssertionError, "DHCP capacity"):
            check.validate_services(lab, self.sheets, self.subnets)

    def test_rejects_underlay_advertised_inside_gre(self) -> None:
        lab = copy.deepcopy(self.ospf)
        line = next(line for line in lab.base.findall(".//RUNNINGCONFIG/LINE")
                    if (line.text or "").strip() == "network 192.168.9.0 0.0.0.7 area 0")
        line.text = " network 10.72.241.32 0.0.0.31 area 0"
        with self.assertRaisesRegex(AssertionError, "underlay/overlay separation"):
            check.validate_routing(lab, self.subnets, True)

    def test_rejects_private_return_route_on_isp(self) -> None:
        lab = copy.deepcopy(self.static)
        engine = next(d.find("ENGINE") for d in lab.devs if d.findtext("ENGINE/NAME") == "R-ISP")
        ET.SubElement(engine.find("RUNNINGCONFIG"), "LINE").text = "ip route 10.72.0.0 255.255.0.0 203.0.113.37"
        with self.assertRaisesRegex(AssertionError, "ISP must not route private"):
            check.validate_routing(lab, self.subnets, False)

    def test_rejects_unsaved_router_config(self) -> None:
        lab = copy.deepcopy(self.static)
        ET.SubElement(lab.base.find(".//STARTUPCONFIG"), "LINE").text = "hostname stale"
        with self.assertRaisesRegex(AssertionError, "Running/startup mismatch"):
            check.validate_topology(lab, self.sheets, False)

    def test_rejects_temporary_scripting_module(self) -> None:
        lab = copy.deepcopy(self.static)
        ET.SubElement(lab.base, "SCRIPT_MODULE")
        with self.assertRaisesRegex(AssertionError, "Temporary scripting module"):
            check.validate_topology(lab, self.sheets, False)


if __name__ == "__main__":
    unittest.main()
