/*
 * Integrate OS — Linker Script for 64-bit Bare-Metal Kernel
 * Target Architecture: x86_64
 * Entry Point: _start (32-bit Multiboot handoff)
 */

ENTRY(_start)

SECTIONS {
    /* GRUB loads kernels at 1 MiB physical address */
    . = 1M;

    /* Boot section: Multiboot header must be in first 8 KiB */
    .boot : ALIGN(4K) {
        KEEP(*(.multiboot_header))
        *(.boot)
    }

    /* 64-bit executable code */
    .text : ALIGN(4K) {
        *(.text .text.*)
    }

    /* Read-only data */
    .rodata : ALIGN(4K) {
        *(.rodata .rodata.*)
    }

    /* Initialized data */
    .data : ALIGN(4K) {
        *(.data .data.*)
    }

    /* Uninitialized data and stacks */
    .bss : ALIGN(4K) {
        *(COMMON)
        *(.bss .bss.*)
    }

    /* Discard unnecessary debugging and metadata sections */
    /DISCARD/ : {
        *(.eh_frame)
        *(.comment)
    }
}
