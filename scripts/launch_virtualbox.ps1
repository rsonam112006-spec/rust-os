# scripts/launch_virtualbox.ps1
# Automates the creation and launch of Rust Micro-OS in Oracle VirtualBox

$ErrorActionPreference = "Stop"

$workspace = "C:\Users\Lenovo\OneDrive\Desktop\os"
$isoPath = "$workspace\micro-os.iso"
$serialLog = "$workspace\traces\virtualbox_serial.log"
$vmName = "RustMicroOS"

# 1. Locate VBoxManage
$vboxPaths = @(
    "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe",
    "C:\Program Files (x86)\Oracle\VirtualBox\VBoxManage.exe",
    (Get-Command VBoxManage.exe -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source)
)

$vbox = $null
foreach ($path in $vboxPaths) {
    if ($path -and (Test-Path $path)) {
        $vbox = $path
        break
    }
}

if (-not $vbox) {
    Write-Host "[!] Oracle VirtualBox (VBoxManage.exe) was not found." -ForegroundColor Yellow
    Write-Host "[*] Attempting installation via winget..." -ForegroundColor Cyan
    winget install --id Oracle.VirtualBox -e --accept-source-agreements --accept-package-agreements
    Start-Sleep -Seconds 5
    if (Test-Path "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe") {
        $vbox = "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"
    } else {
        Write-Host "[-] Please finish VirtualBox installation and re-run this script." -ForegroundColor Red
        exit 1
    }
}

Write-Host "[+] Found VirtualBox at: $vbox" -ForegroundColor Green

# 2. Check if VM already exists; unregister if needed for a clean state
$existing = & $vbox list vms
if ($existing -match "`"$vmName`"") {
    Write-Host "[*] VM '$vmName' already exists. Powering off if running..." -ForegroundColor Yellow
    try { & $vbox controlvm $vmName poweroff } catch {}
    Start-Sleep -Seconds 1
} else {
    Write-Host "[*] Creating new VirtualBox VM '$vmName'..." -ForegroundColor Cyan
    & $vbox createvm --name $vmName --ostype "Other_64" --register
}

# 3. Configure Hardware Specifications
Write-Host "[*] Configuring VM Hardware (512 MB RAM, 2 vCPUs, VMSVGA 32MB, AC97 audio, virtio network)..." -ForegroundColor Cyan
& $vbox modifyvm $vmName --memory 512 `
                         --cpus 2 `
                         --vram 32 `
                         --graphicscontroller vmsvga `
                         --boot1 dvd `
                         --boot2 none `
                         --boot3 none `
                         --boot4 none `
                         --mouse usbtablet `
                         --keyboard ps2 `
                         --nic1 nat `
                         --nictype1 82540EM

# 4. Attach Storage Controller & micro-os.iso
Write-Host "[*] Attaching Storage Controller and ISO ($isoPath)..." -ForegroundColor Cyan
$storageList = & $vbox showvminfo $vmName --machinereadable
if ($storageList -notmatch "storagecontrollername0") {
    & $vbox storagectl $vmName --name "IDE Controller" --add ide
}

& $vbox storageattach $vmName --name "IDE Controller" `
                             --port 0 `
                             --device 0 `
                             --type dvddrive `
                             --medium $isoPath

# 5. Configure Serial Port COM1 to pipe output to serial log
Write-Host "[*] Configuring COM1 Serial Port -> $serialLog..." -ForegroundColor Cyan
if (-not (Test-Path "$workspace\traces")) {
    New-Item -ItemType Directory -Path "$workspace\traces" -Force | Out-Null
}
& $vbox modifyvm $vmName --uart1 0x3F8 4 `
                         --uartmode1 file $serialLog

# 6. Launch VM in Interactive GUI Mode
Write-Host "[+] Launching $vmName in Oracle VirtualBox GUI..." -ForegroundColor Green
& $vbox startvm $vmName --type gui

Write-Host "==========================================================" -ForegroundColor Green
Write-Host "   Rust Micro-OS is now running inside Oracle VirtualBox!   " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
