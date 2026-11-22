#!/bin/bash
set -e

PROJECT_DIR="/mnt/c/Users/Lenovo/OneDrive/Desktop/os"
KERNEL_DIR="$PROJECT_DIR/integrate-os/kernel_arch"
BUILD_DIR="$KERNEL_DIR/target"
OUTPUT_BIN="$BUILD_DIR/kernel.bin"

echo "=== Building Integrate OS Bare-Metal 64-bit Kernel ==="
mkdir -p "$BUILD_DIR"

# 1. Assemble boot.s
as --64 "$KERNEL_DIR/src/boot.s" -o "$BUILD_DIR/boot.o"

# 2. Link boot.o and libintegrate_os_kernel.a
ld -n -T "$KERNEL_DIR/src/linker.ld" -o "$OUTPUT_BIN" "$BUILD_DIR/boot.o" "$KERNEL_DIR/target/x86_64-unknown-none/release/libintegrate_os_kernel.a"

# 3. Check Multiboot compliance
grub-file --is-x86-multiboot "$OUTPUT_BIN"
echo "[+] SUCCESS: kernel.bin is verified Multiboot compliant!"
ls -lh "$OUTPUT_BIN"
