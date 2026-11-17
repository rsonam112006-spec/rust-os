@echo off
setlocal enabledelayedexpansion

echo ============================================================
echo   Oracle VirtualBox Automated VM Setup for Rust Micro-OS
echo ============================================================

set "VM_NAME=RustMicroOS"
set "ISO_PATH=%~dp0..\micro-os.iso"
set "LOG_PATH=%~dp0..\traces\virtualbox_serial.log"

:: Check for VBoxManage
set "VBOX_BIN="
if exist "%VBOX_MSI_INSTALL_PATH%\VBoxManage.exe" set "VBOX_BIN=%VBOX_MSI_INSTALL_PATH%\VBoxManage.exe"
if exist "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe" set "VBOX_BIN=C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"
if exist "C:\Program Files (x86)\Oracle\VirtualBox\VBoxManage.exe" set "VBOX_BIN=C:\Program Files (x86)\Oracle\VirtualBox\VBoxManage.exe"

if "%VBOX_BIN%"=="" (
    where VBoxManage.exe >nul 2>&1
    if !errorlevel! equ 0 (
        set "VBOX_BIN=VBoxManage.exe"
    ) else (
        echo [ERROR] VBoxManage.exe not found!
        echo Please ensure Oracle VirtualBox is installed.
        pause
        exit /b 1
    )
)

echo [+] Using VBoxManage: "%VBOX_BIN%"

:: Ensure traces directory exists
if not exist "%~dp0..\traces" mkdir "%~dp0..\traces"
type nul > "%LOG_PATH%"

:: Power off and unregister if existing
"%VBOX_BIN%" list vms | findstr /C:"\"%VM_NAME%\"" >nul
if !errorlevel! equ 0 (
    echo [*] Removing previous instance of %VM_NAME%...
    "%VBOX_BIN%" controlvm "%VM_NAME%" poweroff >nul 2>&1
    "%VBOX_BIN%" unregistervm "%VM_NAME%" --delete >nul 2>&1
)

echo [*] Registering new VM %VM_NAME%...
"%VBOX_BIN%" createvm --name "%VM_NAME%" --ostype "Other_64" --register
"%VBOX_BIN%" modifyvm "%VM_NAME%" --memory 256 --cpus 1 --acpi on --ioapic on
"%VBOX_BIN%" modifyvm "%VM_NAME%" --uart1 0x3F8 4 --uartmode1 raw "%LOG_PATH%"
"%VBOX_BIN%" storagectl "%VM_NAME%" --name "IDE Controller" --add ide

if exist "%ISO_PATH%" (
    echo [*] Attaching "%ISO_PATH%"...
    "%VBOX_BIN%" storageattach "%VM_NAME%" --storagectl "IDE Controller" --port 0 --device 0 --type dvddrive --medium "%ISO_PATH%"
) else (
    echo [!] ISO not found at %ISO_PATH%. Run python scripts/build_bootable_iso.py first.
)

echo [*] Starting VirtualBox VM...
"%VBOX_BIN%" startvm "%VM_NAME%" --type gui

echo [+] Done!
pause
