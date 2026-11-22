#!/bin/bash
# Integrate OS — Automated ISO Generation Pipeline
# Builds a bootable hybrid ISO (integrate-os.iso) with GRUB 2 bootloader,
# Linux 64-bit kernel, research engine, and network utilities.

set -e

PROJECT_DIR="/mnt/c/Users/Lenovo/OneDrive/Desktop/os"
ISO_OUTPUT="$PROJECT_DIR/integrate-os.iso"
STAGING_DIR="/tmp/integrate_os_iso_staging"

echo "=========================================================="
echo "      INTEGRATE OS — BOOTABLE ISO BUILD PIPELINE          "
echo "=========================================================="

# Step 1: Clean and prepare staging workspace
echo "[*] Step 1: Preparing ISO staging directory hierarchy..."
rm -rf "$STAGING_DIR"
mkdir -p "$STAGING_DIR/boot/grub"
mkdir -p "$STAGING_DIR/integrate-os/bin"
mkdir -p "$STAGING_DIR/integrate-os/scripts"

# Step 2: Deploy GRUB 2 Configuration
echo "[*] Step 2: Integrating GRUB 2 bootloader configuration..."
cp "$PROJECT_DIR/integrate-os/iso_builder/boot/grub/grub.cfg" "$STAGING_DIR/boot/grub/grub.cfg"

# Step 3: Embed Linux Kernel and Initrd
echo "[*] Step 3: Embedding 64-bit Linux Kernel (vmlinuz) and Initial RAM Disk (initrd)..."
cp -L /boot/vmlinuz "$STAGING_DIR/boot/vmlinuz"
cp -L /boot/initrd.img "$STAGING_DIR/boot/initrd.img"

# Step 4: Embed Compiled Research Engine & System Scripts
echo "[*] Step 4: Staging Integrate OS Rust Research Suite and management tools..."
cp "$PROJECT_DIR/integrate-os/research/target/release/integrate_os_research" "$STAGING_DIR/integrate-os/bin/integrate-os"
chmod +x "$STAGING_DIR/integrate-os/bin/integrate-os"

cp "$PROJECT_DIR/integrate-os/iso_builder/detect_hardware.sh" "$STAGING_DIR/integrate-os/scripts/"
cp "$PROJECT_DIR/integrate-os/iso_builder/network_setup.sh" "$STAGING_DIR/integrate-os/scripts/"
cp "$PROJECT_DIR/integrate-os/iso_builder/snap_store_gui.py" "$STAGING_DIR/integrate-os/scripts/"
chmod +x "$STAGING_DIR"/integrate-os/scripts/*

# Step 5: Generate Bootable Hybrid ISO via grub-mkrescue / xorriso
echo "[*] Step 5: Generating Hybrid El-Torito ISO via grub-mkrescue & xorriso..."
grub-mkrescue -o "$ISO_OUTPUT" "$STAGING_DIR"

echo -e "\n[+] SUCCESS: Integrate OS Bootable ISO generated successfully!"
echo "[+] Output File Location : $ISO_OUTPUT"
ls -lh "$ISO_OUTPUT"

echo "=========================================================="
