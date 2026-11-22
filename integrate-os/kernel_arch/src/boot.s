/*
 * Rust OS — 32-bit to 64-bit Multiboot Bootloader Entry
 * Handoff: BIOS/UEFI -> GRUB 2 -> _start (32-bit) -> Long Mode (64-bit) -> kernel_main (Rust)
 */

.global _start
.global gdt64_ptr
.extern kernel_main

# --- Multiboot 1 Header ---
.section .multiboot_header, "a"
.align 4
.set MB_MAGIC,    0x1BADB002
.set MB_FLAGS,    0x00000003    # Align modules on 4KB + provide memory map
.set MB_CHECKSUM, -(MB_MAGIC + MB_FLAGS)

.long MB_MAGIC
.long MB_FLAGS
.long MB_CHECKSUM

# --- 32-bit Protected Mode Entry Point ---
.section .boot, "ax"
.code32
_start:
    cli

    # 1. Initialize temporary boot stack
    mov $boot_stack_top, %esp

    # 2. Preserve Multiboot arguments (EAX = Magic, EBX = Multiboot Info Address)
    mov %eax, %edi
    mov %ebx, %esi

    # 3. Verify Multiboot Magic (0x2BADB002)
    cmp $0x2BADB002, %eax
    jne error_no_multiboot

    # 4. Check for CPUID instruction support
    pushfl
    pop %eax
    mov %eax, %ecx
    xor $(1 << 21), %eax
    push %eax
    popfl
    pushfl
    pop %eax
    push %ecx
    popfl
    cmp %eax, %ecx
    je error_no_cpuid

    # 5. Check for x86_64 Long Mode support
    mov $0x80000000, %eax
    cpuid
    cmp $0x80000001, %eax
    jb error_no_long_mode

    mov $0x80000001, %eax
    cpuid
    test $(1 << 29), %edx
    jz error_no_long_mode

    # 6. Setup 4-Level Identity Paging (maps 0 - 1 GiB via 2 MiB huge pages)
    # Point PML4[0] -> PDPT
    mov $pdpt_table, %eax
    or $0x03, %eax          # Present + Writable
    mov %eax, pml4_table

    # Point PDPT[0] -> PD
    mov $pd_table, %eax
    or $0x03, %eax          # Present + Writable
    mov %eax, pdpt_table

    # Map 512 entries in Page Directory (512 * 2 MiB = 1 GiB)
    mov $0, %ecx
map_pd_loop:
    mov $0x200000, %eax     # 2 MiB
    mul %ecx
    or $0x83, %eax          # Present + Writable + HugePage (2MB)
    mov %eax, pd_table(, %ecx, 8)
    inc %ecx
    cmp $512, %ecx
    jne map_pd_loop

    # 7. Enable Physical Address Extension (PAE) in CR4
    mov %cr4, %eax
    or $(1 << 5), %eax
    mov %eax, %cr4

    # 8. Load PML4 Base Address into CR3
    mov $pml4_table, %eax
    mov %eax, %cr3

    # 9. Enable Long Mode in EFER MSR (0xC0000080, bit 8)
    mov $0xC0000080, %ecx
    rdmsr
    or $(1 << 8), %eax
    wrmsr

    # 10. Enable Paging & Protected Mode in CR0
    mov %cr0, %eax
    or $(1 << 31) | (1 << 0), %eax
    mov %eax, %cr0

    # 11. Load temporary 64-bit GDT
    lgdt (gdt64_ptr)

    # 12. Far jump into 64-bit Long Mode code segment (0x08)
    ljmp $0x08, $long_mode_entry

# --- Early Boot Error Handlers ---
error_no_multiboot:
    movl $0x4f524f45, 0xb8000  # "ER"
    movl $0x4f314f52, 0xb8004  # "R1" (Multiboot error)
    hlt
    jmp error_no_multiboot

error_no_cpuid:
    movl $0x4f524f45, 0xb8000  # "ER"
    movl $0x4f324f52, 0xb8004  # "R2" (No CPUID)
    hlt
    jmp error_no_cpuid

error_no_long_mode:
    movl $0x4f524f45, 0xb8000  # "ER"
    movl $0x4f334f52, 0xb8004  # "R3" (No Long Mode)
    hlt
    jmp error_no_long_mode

# --- 64-bit Long Mode Execution ---
.code64
long_mode_entry:
    # Reload data segment registers with 64-bit data selector (0x10)
    mov $0x10, %ax
    mov %ax, %ds
    mov %ax, %es
    mov %ax, %fs
    mov %ax, %gs
    mov %ax, %ss

    # Initialize 64-bit kernel execution stack
    mov $kernel_stack_top, %rsp

    # Clear RFLAGS
    push $0
    popfq

    # Call Rust kernel entry point: kernel_main(magic: u32, info: u64)
    # SysV ABI: RDI = 1st arg, RSI = 2nd arg
    call kernel_main

    # If kernel_main returns, halt CPU permanently
    cli
halt_loop:
    hlt
    jmp halt_loop

# --- 64-bit GDT Definition ---
.section .rodata
.align 8
gdt64:
    .quad 0                                              # Null descriptor
    .quad (1 << 43) | (1 << 44) | (1 << 47) | (1 << 53)  # 0x08: 64-bit Kernel Code (Ring 0, Executable, 64-bit)
    .quad (1 << 41) | (1 << 44) | (1 << 47)              # 0x10: 64-bit Kernel Data (Ring 0, Writable)
gdt64_ptr:
    .word . - gdt64 - 1
    .long gdt64

# --- Page Tables & Stacks ---
.section .bss
.align 4096
pml4_table:
    .skip 4096
pdpt_table:
    .skip 4096
pd_table:
    .skip 4096

.align 16
boot_stack_bottom:
    .skip 16384     # 16 KiB 32-bit boot stack
boot_stack_top:

.align 16
kernel_stack_bottom:
    .skip 65536     # 64 KiB 64-bit kernel stack
kernel_stack_top:
