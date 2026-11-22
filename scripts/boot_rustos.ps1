$ErrorActionPreference = "Continue"

$vbox = "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"
$vm = "RustOS"
$ws = "C:\Users\Lenovo\OneDrive\Desktop\os"

Write-Host "Powering off VM if running..."
try { & $vbox controlvm $vm poweroff } catch {}
Write-Host "Waiting 5 seconds for session unlock..."
Start-Sleep -Seconds 5

Write-Host "Adding floppy controller..."
& $vbox storagectl $vm --name "Floppy" --add floppy

Write-Host "Attaching micro-os.img to floppy controller..."
& $vbox storageattach $vm --storagectl "Floppy" --port 0 --device 0 --type fdd --medium "$ws\micro-os.img"

Write-Host "Attaching micro-os.iso to SATA DVD drive..."
& $vbox storageattach $vm --storagectl "SATA" --port 1 --device 0 --type dvddrive --medium "$ws\micro-os.iso"

Write-Host "Setting boot order to Floppy -> DVD..."
& $vbox modifyvm $vm --boot1 floppy --boot2 dvd --boot3 none

Write-Host "Starting VM in GUI mode..."
& $vbox startvm $vm --type gui

Write-Host "Done!"
