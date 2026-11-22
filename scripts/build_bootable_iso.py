#!/usr/bin/env python3
"""
scripts/build_bootable_iso.py
Builds a bootable disk image / ISO (micro-os.iso and micro-os.img) for Oracle VirtualBox.
Supports standard ISO 9660 with El Torito boot catalog and 1.44MB Floppy emulation.
Boots directly into the Windows 11 Fluent Graphical Desktop Kernel.
"""

import os
import sys
import struct

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from build_gui_boot import build_full_gui_system
except ImportError:
    from scripts.build_gui_boot import build_full_gui_system

def build_iso(out_path="micro-os.iso"):
    print(f"[*] Generating Windows 11 Fluent Graphical OS Image for VirtualBox: {out_path}")

    gui_img = build_full_gui_system()

    # Create 1.44 MB floppy emulation image (standard El Torito payload)
    floppy_img = bytearray(1440 * 1024)
    floppy_img[0:len(gui_img)] = gui_img

    # Write 1.44MB boot floppy image
    with open("micro-os.img", "wb") as f:
        f.write(floppy_img)
    print(f"[+] Created raw boot floppy image: micro-os.img ({len(gui_img)} kernel bytes embedded)")

    # Construct ISO 9660 with El Torito specification
    # Sector size = 2048 bytes
    iso_sectors = 16 + 2 + 1 + (len(floppy_img) // 2048) + 10
    iso_data = bytearray(iso_sectors * 2048)

    # Sector 16: Primary Volume Descriptor (PVD)
    pvd = bytearray(2048)
    pvd[0] = 0x01 # Type 1: PVD
    pvd[1:6] = b"CD001"
    pvd[6] = 0x01 # Version
    pvd[40:72] = b"WIN11_MICROOS   ".ljust(32, b" ")
    # Volume Space Size (Little + Big Endian, 8 bytes total at offset 80)
    struct.pack_into("<I", pvd, 80, iso_sectors)
    struct.pack_into(">I", pvd, 84, iso_sectors)
    # Logical Block Size (2048 bytes at offset 128)
    struct.pack_into("<H", pvd, 128, 2048)
    struct.pack_into(">H", pvd, 130, 2048)
    iso_data[16 * 2048 : 17 * 2048] = pvd

    # Sector 17: Boot Record Volume Descriptor (El Torito)
    brvd = bytearray(2048)
    brvd[0] = 0x00 # Boot Record
    brvd[1:6] = b"CD001"
    brvd[6] = 0x01
    brvd[7:39] = b"EL TORITO SPECIFICATION".ljust(32, b"\x00")
    # Pointer to Boot Catalog (Sector 18)
    struct.pack_into("<I", brvd, 0x47, 18)
    iso_data[17 * 2048 : 18 * 2048] = brvd

    # Sector 18: Boot Catalog
    catalog = bytearray(2048)
    # Validation Entry (Bytes 0x00 to 0x1F)
    catalog[0] = 0x01 # Header ID
    catalog[1] = 0x00 # Platform x86
    catalog[0x1E] = 0x55 # Key byte 1
    catalog[0x1F] = 0xAA # Key byte 2
    # Checksum: sum of all 16 words must be 0
    s_val = sum(struct.unpack_from('<16H', catalog[0:32]))
    c_val = (-s_val) & 0xFFFF
    struct.pack_into('<H', catalog, 0x1C, c_val)

    # Default Initial Entry (Bytes 0x20 to 0x3F)
    catalog[0x20] = 0x88 # Bootable
    catalog[0x21] = 0x02 # 1.44 MB floppy emulation
    struct.pack_into("<H", catalog, 0x26, 1)  # Sector count at 0x26
    struct.pack_into("<I", catalog, 0x28, 20) # Load RBA at 0x28 (Sector 20)
    iso_data[18 * 2048 : 19 * 2048] = catalog

    # Sector 19: Volume Descriptor Set Terminator
    vds = bytearray(2048)
    vds[0] = 0xFF
    vds[1:6] = b"CD001"
    vds[6] = 0x01
    iso_data[19 * 2048 : 20 * 2048] = vds

    # Sector 20+: Floppy image payload
    iso_data[20 * 2048 : 20 * 2048 + len(floppy_img)] = floppy_img

    with open(out_path, "wb") as f:
        f.write(iso_data)

    print(f"[+] Bootable ISO successfully generated: {out_path} ({len(iso_data)} bytes)")
    print(f"[+] This ISO can now be attached and booted in Oracle VirtualBox.")

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "micro-os.iso"
    build_iso(out)
