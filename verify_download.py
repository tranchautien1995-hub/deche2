import hashlib
import io
import plistlib
import struct
import sys
import zipfile
from pathlib import Path


def main():
    archive_path, output = map(Path, sys.argv[1:])
    with zipfile.ZipFile(archive_path) as artifact:
        assert artifact.testzip() is None
        files = [name for name in artifact.namelist() if name.endswith(".ipa")]
        (name,) = files
        assert "/" not in name and "\\" not in name
        data = artifact.read(name)
        digest = hashlib.sha256(data).hexdigest()
        assert digest == artifact.read("SHA256.txt").decode().split()[0]
        build = artifact.read("BuildInfo.txt").decode()

    with zipfile.ZipFile(io.BytesIO(data)) as ipa:
        assert ipa.testzip() is None
        bundle = "Payload/AoE2HDMobile.app/"
        info = plistlib.loads(ipa.read(bundle + "Info.plist"))
        assert info["MinimumOSVersion"] == "15.1"
        assert info["CFBundleShortVersionString"] == "1.0.4"
        assert info["CFBundleVersion"] == "5"
        assert info["CFBundleIdentifier"] == "io.github.tranchautien1995.aoe2hdmobile"
        assert info["UIFileSharingEnabled"] is True
        assert info["LSSupportsOpeningDocumentsInPlace"] is True
        assert info["CFBundlePackageType"] == "APPL"
        assert all(Path(item).suffix not in {".apk", ".drs", ".slp"} for item in ipa.namelist())
        packs = [item for item in ipa.infolist() if item.filename.startswith(bundle) and item.filename.endswith(".pck")]
        assert len(packs) == 1 and packs[0].file_size > 0
        executable = ipa.getinfo(bundle + info["CFBundleExecutable"])
        assert (executable.external_attr >> 16) & 0o111
        with ipa.open(executable) as binary:
            magic, cpu_type, _, file_type = struct.unpack("<4I", binary.read(16))
        assert (magic, cpu_type, file_type) == (0xFEEDFACF, 0x0100000C, 2)
        print(f"Bundle: {info.get('CFBundleDisplayName', info['CFBundleName'])}")
        print(f"Minimum iOS: {info['MinimumOSVersion']}")

    destination = output / name
    with destination.open("wb") as payload:
        payload.write(data)
    print(f"IPA: {len(data)} bytes")
    print(f"SHA-256: {digest}")
    print(build)


if __name__ == "__main__":
    main()
