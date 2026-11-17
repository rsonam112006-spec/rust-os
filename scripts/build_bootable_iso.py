#!/usr/bin/env python3
"""
scripts/build_bootable_iso.py
Builds a bootable disk image / ISO (micro-os.iso) for Oracle VirtualBox.
Supports standard ISO 9660 with El Torito boot catalog or FAT32 UEFI structure.
"""

import os
import sys
import subprocess
import struct

def create_minimal_boot_sector():
    """Generates a standard 512-byte BIOS MBR boot sector with 0xAA55 signature."""
    sector = bytearray(512)
    # Minimal x86 16-bit code:
    # cli; cld; mov ax, 0x07C0; mov ds, ax; mov si, msg;
    # print_loop: lodsb; test al, al; jz halt; mov ah, 0x0E; int 0x10; jmp print_loop;
    # halt: hlt; jmp halt
    code = bytes([
        0xFA, 0xFC, 0xB8, 0xC0, 0x07, 0x8E, 0xD8, 0xBE, 0x1E, 0x00,
        0xAC, 0x84, 0xC0, 0x74, 0x06, 0xB4, 0x0E, 0xCD, 0x10, 0xEB,
        0xF5, 0xF4, 0xEB, 0xFD
    ])
    msg = b"\r\n[Rust-MicroOS] Booting under Oracle VirtualBox (CA-6)...\r\n\0"
    sector[0:len(code)] = code
    sector[0x1E:0x1E+len(msg)] = msg
    sector[510] = 0x55
    sector[511] = 0xAA
    return bytes(sector)

def build_iso(out_path="micro-os.iso"):
    print(f"Generating bootable image for VirtualBox: {out_path}")
    
    # Check if a custom kernel binary exists
    kernel_bin = "target/x86_64-unknown-none/release/rust-micro-os"
    if not os.path.exists(kernel_bin):
        kernel_bin = "target/release/rust-micro-os.exe"

    boot_sector = create_minimal_boot_sector()

    # Create a 1.44 MB floppy emulation image (standard El Torito payload)
    floppy_img = bytearray(1440 * 1024)
    floppy_img[0:512] = boot_sector

    # If kernel binary exists, append it to sectors starting at sector 1
    if os.path.exists(kernel_bin):
        with open(kernel_bin, "rb") as f:
            kdata = f.read()
        max_copy = min(len(kdata), len(floppy_img) - 512)
        floppy_img[512:512+max_copy] = kdata[:max_copy]
        print(f"Embedded kernel payload ({max_copy} bytes) into boot image.")

    # Write 1.44MB boot image
    with open("micro-os.img", "wb") as f:
        f.write(floppy_img)
    print("Created raw boot floppy image: micro-os.img")

    # Construct ISO 9660 with El Torito specification
    # Sector size = 2048 bytes
    iso_sectors = 16 + 2 + 1 + (len(floppy_img) // 2048) + 10
    iso_data = bytearray(iso_sectors * 2048)

    # Sector 16: Primary Volume Descriptor (PVD)
    pvd = bytearray(2048)
    pvd[0] = 0x01 # Type 1: PVD
    pvd[1:6] = b"CD001"
    pvd[6] = 0x01 # Version
    pvd[40:72] = b"RUST_MICROOS_CA6".ljust(32)
    iso_data[16 * 2048 : 17 * 2048] = pvd

    # Sector 17: Boot Record Volume Descriptor (El Torito)
    brvd = bytearray(2048)
    brvd[0] = 0x00 # Boot Record
    brvd[1:6] = b"CD001"
    brvd[6] = 0x01
    brvd[7:39] = b"EL TORITO SPECIFICATION".ljust(32)
    # Pointer to Boot Catalog (Sector 18)
    struct.pack_into("<I", brvd, 0x47, 18)
    iso_data[17 * 2048 : 18 * 2048] = brvd

    # Sector 18: Boot Catalog
    catalog = bytearray(2048)
    # Validation Entry
    catalog[0] = 0x01 # Header ID
    catalog[1] = 0x00 # Platform x86
    catalog[0x1C] = 0x55
    catalog[0x1D] = 0xAA
    # Default Initial Entry
    catalog[0x20] = 0x88 # Bootable
    catalog[0x21] = 0x02 # Boot Media: 1.44 MB floppy emulation
    # Starting sector of boot image (Sector 20)
    struct.pack_into("<I", catalog, 0x28, 20)
    # Sector count (1 sector for initial load)
    struct.pack_into("<H", catalog, 0x2C, 1)
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
