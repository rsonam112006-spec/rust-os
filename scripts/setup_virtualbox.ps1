<#
.SYNOPSIS
    Automated Oracle VirtualBox VM Provisioning & Launch Script for Rust Micro-OS (CA-6)

.DESCRIPTION
    Creates, configures, and launches a dedicated VirtualBox VM named "RustMicroOS".
    Configures 256 MB RAM, 1 vCPU, IDE storage controller, and redirects UART COM1
    (port 0x3F8) directly to a host trace log file for automated Python parsing.
#>

[CmdletBinding()]
param (
    [string]$VmName = "RustMicroOS",
    [string]$IsoPath = "$PSScriptRoot\..\micro-os.iso",
    [string]$SerialLogPath = "$PSScriptRoot\..\traces\virtualbox_serial.log"
)

$ErrorActionPreference = "Stop"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Oracle VirtualBox Automated VM Setup for Rust Micro-OS     " -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# 1. Locate VBoxManage executable
$vboxPaths = @(
    "VBoxManage.exe",
    "$env:VBOX_MSI_INSTALL_PATH\VBoxManage.exe",
    "$env:ProgramFiles\Oracle\VirtualBox\VBoxManage.exe",
    "$env:ProgramFiles(x86)\Oracle\VirtualBox\VBoxManage.exe",
    "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"
)

$vboxManage = $null
foreach ($path in $vboxPaths) {
    if ($path -and (Test-Path $path)) {
        $vboxManage = $path
        break
    }
}

if (-not $vboxManage) {
    $cmd = Get-Command VBoxManage -ErrorAction SilentlyContinue
    if ($cmd) {
        $vboxManage = $cmd.Source
    }
}

if (-not $vboxManage) {
    Write-Host "[ERROR] Could not find VBoxManage.exe." -ForegroundColor Red
    Write-Host "Please ensure Oracle VirtualBox is installed and added to PATH or installed in 'C:\Program Files\Oracle\VirtualBox\'." -ForegroundColor Yellow
    exit 1
}

Write-Host "[+] Found VBoxManage at: $vboxManage" -ForegroundColor Green

# 2. Check if VM already exists; power off and unregister if needed
Write-Host "[*] Checking if VM '$VmName' already exists..."
$existingVms = & $vboxManage list vms
if ($existingVms -match """$VmName""") {
    Write-Host "[!] VM '$VmName' exists. Cleaning up previous instance..." -ForegroundColor Yellow
    try {
        & $vboxManage controlvm $VmName poweroff 2>$null
        Start-Sleep -Seconds 1
    } catch {}
    & $vboxManage unregistervm $VmName --delete
    Write-Host "[+] Old VM removed." -ForegroundColor Green
}

# 3. Create fresh VM
Write-Host "[*] Creating VM '$VmName'..."
& $vboxManage createvm --name $VmName --ostype "Other_64" --register

# 4. Configure Memory, CPU, and System Flags
Write-Host "[*] Configuring 256 MB RAM, 1 CPU, ACPI and IOAPIC..."
& $vboxManage modifyvm $VmName --memory 256 --cpus 1 --acpi on --ioapic on --boot1 dvd --boot2 disk --boot3 none --boot4 none

# 5. Configure COM1 Serial Port output to file
$resolvedLogDir = Split-Path -Parent (Resolve-Path -Path (Split-Path -Parent $SerialLogPath) -ErrorAction SilentlyContinue)
if (-not $resolvedLogDir) {
    $resolvedLogDir = "$PSScriptRoot\..\traces"
    New-Item -ItemType Directory -Force -Path $resolvedLogDir | Out-Null
}
$fullLogPath = [System.IO.Path]::GetFullPath($SerialLogPath)

# Ensure empty log file exists
if (Test-Path $fullLogPath) {
    Remove-Item -Force $fullLogPath
}
New-Item -ItemType File -Force -Path $fullLogPath | Out-Null

Write-Host "[*] Configuring COM1 (0x3F8) redirection to: $fullLogPath"
& $vboxManage modifyvm $VmName --uart1 0x3F8 4 --uartmode1 raw "$fullLogPath"

# 6. Configure Storage Controller
Write-Host "[*] Adding IDE Storage Controller..."
& $vboxManage storagectl $VmName --name "IDE Controller" --add ide

# 7. Attach Media if available
if (Test-Path $IsoPath) {
    $fullIsoPath = [System.IO.Path]::GetFullPath($IsoPath)
    Write-Host "[*] Attaching bootable ISO: $fullIsoPath" -ForegroundColor Green
    & $vboxManage storageattach $VmName --storagectl "IDE Controller" --port 0 --device 0 --type dvddrive --medium "$fullIsoPath"
} else {
    Write-Host "[!] Bootable media not yet present at $IsoPath. You can build it using 'python scripts/build_bootable_iso.py'." -ForegroundColor Yellow
}

# 8. Start the VM
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Starting VirtualBox VM: $VmName                            " -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
& $vboxManage startvm $VmName --type gui

Write-Host "[+] VirtualBox VM started successfully." -ForegroundColor Green
Write-Host "[+] Monitor console on the VirtualBox window." -ForegroundColor Green
Write-Host "[+] Serial logs are being captured to: $fullLogPath" -ForegroundColor Green
