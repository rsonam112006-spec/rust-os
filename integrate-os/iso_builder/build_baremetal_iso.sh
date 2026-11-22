#!/bin/bash
set -e

PROJECT_DIR="/mnt/c/Users/Lenovo/OneDrive/Desktop/os"
ISO_OUTPUT_RUST="$PROJECT_DIR/rust-os.iso"
ISO_OUTPUT_LEGACY="$PROJECT_DIR/integrate-os.iso"
STAGING_DIR="/tmp/rust_os_baremetal_iso"
KERNEL_BIN="$PROJECT_DIR/integrate-os/kernel_arch/target/kernel.bin"

echo "=========================================================="
echo "      RUST OS — BARE-METAL HYBRID ISO BUILD PIPELINE      "
echo "=========================================================="

# 1. Clean and prepare staging
rm -rf "$STAGING_DIR"
mkdir -p "$STAGING_DIR/boot/grub"

# 2. Write grub.cfg
cat << 'EOF' > "$STAGING_DIR/boot/grub/grub.cfg"
set timeout=2
set default=0

insmod font
insmod all_video
insmod gfxterm
insmod serial

serial --unit=0 --speed=115200
terminal_input console serial
terminal_output gfxterm serial

set gfxmode=auto
set gfxpayload=keep

menuentry "Rust OS - 64-bit Bare-Metal Kernel" --class os {
    echo "Loading Rust OS Kernel..."
    multiboot /boot/kernel.bin
    boot
}
EOF

# 3. Copy kernel.bin
cp "$KERNEL_BIN" "$STAGING_DIR/boot/kernel.bin"

# 4. Generate Hybrid ISO for Rust OS
grub-mkrescue -o "$ISO_OUTPUT_RUST" "$STAGING_DIR"
cp -f "$ISO_OUTPUT_RUST" "$ISO_OUTPUT_LEGACY"

echo "[+] SUCCESS: Bare-Metal Rust OS ISO generated successfully!"
echo "[+] Primary Image: $ISO_OUTPUT_RUST"
echo "[+] Mirrored Image: $ISO_OUTPUT_LEGACY"
ls -lh "$ISO_OUTPUT_RUST" "$ISO_OUTPUT_LEGACY"
