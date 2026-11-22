#!/usr/bin/env python3
"""
scripts/build_gui_boot.py
Builds the complete Windows 11 Fluent Graphical Desktop OS for VirtualBox.
Features:
- Sector 1: Standard FAT12 BPB + Real-Mode BIOS Loader (loads Sectors 2..17 to 0x7E00)
- Sector 2..17: Windows 11 Fluent Desktop Engine:
  * Top Menu Bar (Row 0, 0x70)
  * Azure Blue Desktop Wallpaper (0x1F20)
  * Seamless Floating Window with CP437 Double Borders (╔═╗║╚═╝), Titlebar, [─][□][✕], and Hardware Telemetry
  * Windows 11 Bottom Taskbar with Weather (24°C Sunny), Start [🪟 Start], [🔍 Search], [Term] [Files] [Store], Wi-Fi [Jain_Student 92%], Clock [14:12]
  * Case-Insensitive Command Dispatcher (supports both lowercase & uppercase)
  * Protected Terminal Scroll Box (Rows 10..21): Window borders, header, and taskbar never scroll off!
  * Interactive INT 16h Keyboard Command Dispatcher supporting:
    help, wifi, ls, dir, cat, type, files, snap, store, ping, ipconfig, winver, neofetch, clear, cls, reboot.
"""

import struct
import sys
import os

def build_full_gui_system():
    # ── Sector 1: Standard MBR / Floppy Boot Sector (512 bytes)
    sec1 = bytearray(512)
    # Jump over BPB to offset 0x3E
    sec1[0:2] = [0xEB, 0x3C]       # jmp short 0x3E
    sec1[2] = 0x90                 # nop
    sec1[3:11] = b"MSWIN4.1"       # OEM Identifier

    # Standard 1.44 MB Floppy BPB
    struct.pack_into("<H", sec1, 0x0B, 512)   # Bytes per sector
    sec1[0x0D] = 1                            # Sectors per cluster
    struct.pack_into("<H", sec1, 0x0E, 1)     # Reserved sectors: 1
    sec1[0x10] = 2                            # Number of FATs: 2
    struct.pack_into("<H", sec1, 0x11, 224)   # Root directory entries: 224
    struct.pack_into("<H", sec1, 0x13, 2880)  # Total sectors: 2880 (1.44 MB)
    sec1[0x15] = 0xF0                         # Media descriptor: 1.44 MB 3.5"
    struct.pack_into("<H", sec1, 0x16, 9)     # Sectors per FAT: 9
    struct.pack_into("<H", sec1, 0x18, 18)    # Sectors per track: 18
    struct.pack_into("<H", sec1, 0x1A, 2)     # Number of heads: 2
    struct.pack_into("<I", sec1, 0x1C, 0)     # Hidden sectors: 0
    struct.pack_into("<I", sec1, 0x20, 0)     # Large sectors: 0
    sec1[0x24] = 0x00                         # Physical drive number: 0
    sec1[0x25] = 0x00                         # Reserved: 0
    sec1[0x26] = 0x29                         # Extended boot signature
    struct.pack_into("<I", sec1, 0x27, 0x20261121) # Volume ID
    sec1[0x2B:0x36] = b"WIN11_MICRO"          # Volume Label (11 bytes)
    sec1[0x36:0x3E] = b"FAT12   "              # File System Type (8 bytes)

    # Loader Code at offset 0x3E (0x7C3E):
    ldr = bytearray()
    ldr.extend([0xFA])                         # cli
    ldr.extend([0x31, 0xC0])                   # xor ax, ax
    ldr.extend([0x8E, 0xD8])                   # mov ds, ax
    ldr.extend([0x8E, 0xC0])                   # mov es, ax
    ldr.extend([0x8E, 0xD0])                   # mov ss, ax
    ldr.extend([0xBC, 0x00, 0x7C])             # mov sp, 0x7C00
    ldr.extend([0xFB])                         # sti

    # Save boot drive (DL passed by BIOS) into offset 0x24 (0x7C24)
    ldr.extend([0x88, 0x16, 0x24, 0x7C])       # mov [0x7C24], dl

    # Reset disk controller: INT 13h, AH=00h
    ldr.extend([0x31, 0xC0])                   # xor ax, ax
    ldr.extend([0x8A, 0x16, 0x24, 0x7C])       # mov dl, [0x7C24]
    ldr.extend([0xCD, 0x13])                   # int 0x13

    # Read 16 sectors (Sectors 2 through 17) into 0000:7E00
    # INT 13h, AH=02h: AL=16, CH=0, CL=2, DH=0, DL=[0x7C24], ES:BX=0000:7E00
    ldr.extend([0xB4, 0x02])                   # mov ah, 0x02
    ldr.extend([0xB0, 0x10])                   # mov al, 16 (read 16 sectors)
    ldr.extend([0x31, 0xC9])                   # xor cx, cx
    ldr.extend([0xB1, 0x02])                   # mov cl, 2 (start at sector 2)
    ldr.extend([0x31, 0xD2])                   # xor dx, dx
    ldr.extend([0x8A, 0x16, 0x24, 0x7C])       # mov dl, [0x7C24]
    ldr.extend([0xBB, 0x00, 0x7E])             # mov bx, 0x7E00
    ldr.extend([0xCD, 0x13])                   # int 0x13

    # Jump to 0000:7E00 (entry point of Sector 2)
    ldr.extend([0xEA, 0x00, 0x7E, 0x00, 0x00]) # jmp far 0000:7E00

    sec1[0x3E:0x3E+len(ldr)] = ldr
    sec1[510] = 0x55
    sec1[511] = 0xAA

    # ── Sector 2..17: Windows 11 GUI Kernel (Base address = 0x7E00)
    code = bytearray()
    BASE_ADDR = 0x7E00

    # 1. Set 80x25 16-color text mode (clears screen)
    code.extend([0xB8, 0x03, 0x00])             # mov ax, 0x0003
    code.extend([0xCD, 0x10])                   # int 0x10

    # 2. Disable blinking so bit 7 gives high-intensity background (16 background colors!)
    code.extend([0xB8, 0x03, 0x10])             # mov ax, 0x1003
    code.extend([0xBB, 0x00, 0x00])             # mov bx, 0x0000
    code.extend([0xCD, 0x10])                   # int 0x10

    # 3. Call draw_desktop subroutine
    call_draw_idx = len(code)
    code.extend([0xE8, 0x00, 0x00])             # call draw_desktop (rel16 patched later)

    # 4. Set cursor position inside window: Row 9, Col 22
    code.extend([0xB4, 0x02])                   # mov ah, 0x02
    code.extend([0xB7, 0x00])                   # mov bh, 0
    code.extend([0xB6, 0x09])                   # mov dh, 9 (Row 9)
    code.extend([0xB2, 0x16])                   # mov dl, 22 (Col 22)
    code.extend([0xCD, 0x10])                   # int 0x10

    # 5. Interactive Command Loop
    offset_prompt = len(code)
    code.extend([0x31, 0xC0])                   # xor ax, ax
    code.extend([0x8E, 0xC0])                   # mov es, ax (ensure ES = 0000)
    code.extend([0x8E, 0xD8])                   # mov ds, ax (ensure DS = 0000)
    code.extend([0xBF, 0x00, 0x90])             # mov di, 0x9000 (input buffer in RAM)

    offset_get_key = len(code)
    code.extend([0x31, 0xC0])                   # xor ax, ax
    code.extend([0xCD, 0x16])                   # int 0x16 (wait for key)

    # Enter (0x0D)
    code.extend([0x3C, 0x0D])
    idx_je_enter = len(code) + 1
    code.extend([0x74, 0x00])                   # je on_enter

    # Backspace (0x08)
    code.extend([0x3C, 0x08])
    idx_je_bs = len(code) + 1
    code.extend([0x74, 0x00])                   # je on_backspace

    # Printable range: 0x20 <= AL <= 0x7E
    code.extend([0x3C, 0x20])
    rel_k1 = (offset_get_key - (len(code) + 2)) & 0xFF
    code.extend([0x72, rel_k1])                 # jb get_key
    code.extend([0x3C, 0x7E])
    rel_k2 = (offset_get_key - (len(code) + 2)) & 0xFF
    code.extend([0x77, rel_k2])                 # ja get_key

    # Buffer limit check: max 48 chars (0x9000 to 0x9030)
    code.extend([0x81, 0xFF, 0x30, 0x90])       # cmp di, 0x9030
    rel_k3 = (offset_get_key - (len(code) + 2)) & 0xFF
    code.extend([0x73, rel_k3])                 # jae get_key

    # Save character in buffer
    code.extend([0xAA])                         # stosb

    # Echo character: mov ah, 0x0E; int 0x10
    code.extend([0xB4, 0x0E])
    code.extend([0xCD, 0x10])
    rel_k4 = (offset_get_key - (len(code) + 2)) & 0xFF
    code.extend([0xEB, rel_k4])                 # jmp get_key

    # ── on_backspace:
    offset_bs = len(code)
    code[idx_je_bs] = (offset_bs - (idx_je_bs + 1)) & 0xFF
    code.extend([0x81, 0xFF, 0x00, 0x90])       # cmp di, 0x9000
    rel_k5 = (offset_get_key - (len(code) + 2)) & 0xFF
    code.extend([0x76, rel_k5])                 # jbe get_key
    code.extend([0x4F])                         # dec di
    # print "\b \b"
    code.extend([0xB4, 0x0E])
    code.extend([0xB0, 0x08])                   # mov al, 8
    code.extend([0xCD, 0x10])
    code.extend([0xB0, 0x20])                   # mov al, ' '
    code.extend([0xCD, 0x10])
    code.extend([0xB0, 0x08])                   # mov al, 8
    code.extend([0xCD, 0x10])
    rel_k6 = (offset_get_key - (len(code) + 2)) & 0xFF
    code.extend([0xEB, rel_k6])                 # jmp get_key

    # ── on_enter:
    offset_enter = len(code)
    code[idx_je_enter] = (offset_enter - (idx_je_enter + 1)) & 0xFF
    code.extend([0xC6, 0x05, 0x00])             # mov byte [di], 0 (null terminate)

    # Print newline \r\n:
    idx_call_pnl = len(code)
    code.extend([0xE8, 0x00, 0x00])             # call print_newline

    # Load first char of command at [0x9000]:
    code.extend([0x8A, 0x06, 0x00, 0x90])       # mov al, [0x9000]

    # Convert uppercase A-Z to lowercase:
    code.extend([0x3C, ord('A')])               # cmp al, 'A'
    idx_jb_upper = len(code) + 1
    code.extend([0x72, 0x00])                   # jb .not_upper
    code.extend([0x3C, ord('Z')])               # cmp al, 'Z'
    idx_ja_upper = len(code) + 1
    code.extend([0x77, 0x00])                   # ja .not_upper
    code.extend([0x04, 0x20])                   # add al, 0x20 (make lowercase)
    
    # .not_upper:
    off_not_upper = len(code)
    code[idx_jb_upper] = (off_not_upper - (idx_jb_upper + 1)) & 0xFF
    code[idx_ja_upper] = (off_not_upper - (idx_ja_upper + 1)) & 0xFF

    # If empty (Enter pressed directly), just prompt again
    code.extend([0x3C, 0x00])
    code.extend([0x0F, 0x84, 0x00, 0x00])
    idx_je_empty = len(code) - 2

    # Check if 'c' (could be 'cat' or 'clear'/'cls'):
    code.extend([0x3C, ord('c')])
    code.extend([0x0F, 0x84, 0x00, 0x00])
    idx_je_c = len(code) - 2

    # Command jumps mapping
    commands = [
        ('h', 'help'),
        ('?', 'help'),
        ('w', 'wifi'),
        ('l', 'ls'),
        ('d', 'dir'),
        ('f', 'files'),
        ('s', 'snap'),
        ('p', 'ping'),
        ('i', 'ipconfig'),
        ('n', 'winver'),
        ('v', 'winver'),
        ('t', 'type'),
        ('r', 'reboot'),
    ]

    cmd_jumps = {}
    for ch, name in commands:
        code.extend([0x3C, ord(ch)])
        code.extend([0x0F, 0x84, 0x00, 0x00])
        cmd_jumps[f"{ch}_{name}"] = len(code) - 2

    # Unknown command handler:
    offset_unknown = len(code)
    idx_patch_unk = len(code) + 1
    code.extend([0xBE, 0x00, 0x00])             # mov si, msg_unknown
    idx_call_unk = len(code)
    code.extend([0xE8, 0x00, 0x00])             # call print_str

    # Print prompt and loop back
    idx_patch_upr = len(code) + 1
    code.extend([0xBE, 0x00, 0x00])             # mov si, msg_prompt
    idx_call_upr = len(code)
    code.extend([0xE8, 0x00, 0x00])
    rel_ret_unk = offset_prompt - (len(code) + 3)
    code.extend([0xE9])
    code.extend(struct.pack("<h", rel_ret_unk))

    # Empty command handler:
    offset_empty = len(code)
    struct.pack_into("<h", code, idx_je_empty, offset_empty - (idx_je_empty + 2))
    idx_patch_epr = len(code) + 1
    code.extend([0xBE, 0x00, 0x00])             # mov si, msg_prompt
    idx_call_epr = len(code)
    code.extend([0xE8, 0x00, 0x00])
    rel_ret_emp = offset_prompt - (len(code) + 3)
    code.extend([0xE9])
    code.extend(struct.pack("<h", rel_ret_emp))

    # Handler for 'c': distinguishes 'cat' vs 'clear'/'cls'
    off_handle_c = len(code)
    struct.pack_into("<h", code, idx_je_c, off_handle_c - (idx_je_c + 2))
    # Load 2nd char at [0x9001]:
    code.extend([0x8A, 0x06, 0x01, 0x90])       # mov al, [0x9001]
    # If uppercase, lowercase it:
    code.extend([0x3C, ord('A')])
    idx_jbc_up = len(code) + 1
    code.extend([0x72, 0x00])
    code.extend([0x3C, ord('Z')])
    idx_jac_up = len(code) + 1
    code.extend([0x77, 0x00])
    code.extend([0x04, 0x20])
    off_not_up_c = len(code)
    code[idx_jbc_up] = (off_not_up_c - (idx_jbc_up + 1)) & 0xFF
    code[idx_jac_up] = (off_not_up_c - (idx_jac_up + 1)) & 0xFF
    # If 2nd char == 'a' ('cat'), jump to 'type'
    code.extend([0x3C, ord('a')])
    code.extend([0x0F, 0x84, 0x00, 0x00])
    idx_je_cat = len(code) - 2
    # Otherwise, it's 'clear' or 'cls' -> jump to 'clear'
    idx_jmp_clr = len(code)
    code.extend([0xE9, 0x00, 0x00])

    # Specific command handlers
    cmd_patches = {}
    cmd_calls = {}

    unique_cmds = ['help', 'wifi', 'ls', 'dir', 'files', 'snap', 'ping', 'ipconfig', 'winver', 'type']
    for name in unique_cmds:
        off_cmd = len(code)
        # Patch any jumps pointing to this command:
        for ch, cname in commands:
            if cname == name:
                key = f"{ch}_{name}"
                struct.pack_into("<h", code, cmd_jumps[key], off_cmd - (cmd_jumps[key] + 2))

        if name == 'type':
            struct.pack_into("<h", code, idx_je_cat, off_cmd - (idx_je_cat + 2))

        cmd_patches[name] = len(code) + 1
        code.extend([0xBE, 0x00, 0x00])         # mov si, msg_<name>
        cmd_calls[name] = len(code)
        code.extend([0xE8, 0x00, 0x00])         # call print_str

        # Print prompt:
        idx_p = len(code) + 1
        code.extend([0xBE, 0x00, 0x00])         # mov si, msg_prompt
        idx_c = len(code)
        code.extend([0xE8, 0x00, 0x00])         # call print_str
        cmd_patches[f"p_{name}"] = idx_p
        cmd_calls[f"p_{name}"] = idx_c

        rel_p = offset_prompt - (len(code) + 3)
        code.extend([0xE9])
        code.extend(struct.pack("<h", rel_p))

    # 'clear' / 'cls' command (redraw desktop & reset cursor)
    off_clear = len(code)
    struct.pack_into("<h", code, idx_jmp_clr + 1, off_clear - (idx_jmp_clr + 3))
    idx_call_redraw = len(code)
    code.extend([0xE8, 0x00, 0x00])             # call draw_desktop
    # reset cursor to Row 9, Col 22
    code.extend([0xB4, 0x02])                   # mov ah, 0x02
    code.extend([0xB7, 0x00])                   # mov bh, 0
    code.extend([0xB6, 0x09])                   # Row 9
    code.extend([0xB2, 0x16])                   # Col 22
    code.extend([0xCD, 0x10])
    rel_p_c = offset_prompt - (len(code) + 3)
    code.extend([0xE9])
    code.extend(struct.pack("<h", rel_p_c))

    # 'r' -> Reboot command (INT 19h)
    off_reboot = len(code)
    struct.pack_into("<h", code, cmd_jumps['r_reboot'], off_reboot - (cmd_jumps['r_reboot'] + 2))
    code.extend([0xCD, 0x19])                   # int 0x19

    # ── print_newline subroutine (with protected scroll box rows 10..21)
    offset_pnl = len(code)
    # Check current row:
    code.extend([0xB4, 0x03, 0xB7, 0x00, 0xCD, 0x10]) # mov ah, 3; mov bh, 0; int 0x10 -> DH=row, DL=col
    code.extend([0x80, 0xFE, 0x15])                     # cmp dh, 21 (row 21)
    idx_jb_pnl = len(code) + 1
    code.extend([0x72, 0x00])                           # jb .do_norm_nl

    # Cursor is at row 21: Scroll ONLY rows 10..21 up by 1 line!
    # INT 10h, AH=06h: AL=1, BH=0x07, CH=10, CL=4, DH=21, DL=75
    code.extend([0xB8, 0x01, 0x06])                     # mov ax, 0x0601
    code.extend([0xB7, 0x07])                           # mov bh, 0x07 (light gray on black)
    code.extend([0xB9, 0x04, 0x0A])                     # mov cx, 0x0A04 (CH=10, CL=4)
    code.extend([0xBA, 0x4B, 0x15])                     # mov dx, 0x154B (DH=21, DL=75)
    code.extend([0xCD, 0x10])                           # int 0x10

    # Set cursor to Row 21, Col 4
    code.extend([0xB4, 0x02, 0xB7, 0x00, 0xB6, 0x15, 0xB2, 0x04, 0xCD, 0x10])
    code.extend([0xC3])                                 # ret

    # .do_norm_nl:
    off_norm_nl = len(code)
    code[idx_jb_pnl] = (off_norm_nl - (idx_jb_pnl + 1)) & 0xFF
    code.extend([0xB4, 0x0E, 0xB0, 0x0D, 0xCD, 0x10])   # print \r
    code.extend([0xB4, 0x0E, 0xB0, 0x0A, 0xCD, 0x10])   # print \n
    code.extend([0xB4, 0x03, 0xB7, 0x00, 0xCD, 0x10])   # get cursor
    code.extend([0xB4, 0x02, 0xB7, 0x00, 0xB2, 0x04, 0xCD, 0x10]) # set col=4
    code.extend([0xC3])                                 # ret

    # ── print_str subroutine
    offset_print_str = len(code)
    code.extend([0xAC])                                 # lodsb
    code.extend([0x84, 0xC0])                           # test al, al
    idx_jz_done = len(code) + 1
    code.extend([0x74, 0x00])                           # jz .ps_done

    # Check \r (0x0D) -> loop
    code.extend([0x3C, 0x0D])
    rel_cr = (offset_print_str - (len(code) + 2)) & 0xFF
    code.extend([0x74, rel_cr])                         # je print_str

    # Check \n (0x0A) -> call print_newline, then loop
    code.extend([0x3C, 0x0A])
    idx_jne_char = len(code) + 1
    code.extend([0x75, 0x00])                           # jne .ps_char
    idx_call_pnl_in_ps = len(code)
    code.extend([0xE8, 0x00, 0x00])                     # call print_newline
    rel_nl = (offset_print_str - (len(code) + 2)) & 0xFF
    code.extend([0xEB, rel_nl])                         # jmp print_str

    # .ps_char:
    off_ps_char = len(code)
    code[idx_jne_char] = (off_ps_char - (idx_jne_char + 1)) & 0xFF
    code.extend([0xB4, 0x0E, 0xCD, 0x10])               # mov ah, 0x0E; int 0x10
    rel_loop = (offset_print_str - (len(code) + 2)) & 0xFF
    code.extend([0xEB, rel_loop])                       # jmp print_str

    # .ps_done:
    off_ps_done = len(code)
    code[idx_jz_done] = (off_ps_done - (idx_jz_done + 1)) & 0xFF
    code.extend([0xC3])                                 # ret

    # ── draw_desktop subroutine
    offset_draw_desktop = len(code)
    struct.pack_into("<h", code, call_draw_idx + 1, offset_draw_desktop - (call_draw_idx + 3))
    struct.pack_into("<h", code, idx_call_redraw + 1, offset_draw_desktop - (idx_call_redraw + 3))

    # 1. Fill entire screen (80x25) with Azure Blue wallpaper (0x1F20)
    code.extend([0xB8, 0x00, 0xB8])             # mov ax, 0xB800
    code.extend([0x8E, 0xC0])                   # mov es, ax
    code.extend([0x31, 0xFF])                   # xor di, di
    code.extend([0xB9, 0xD0, 0x07])             # mov cx, 2000 (80*25)
    code.extend([0xB8, 0x20, 0x1F])             # mov ax, 0x1F20 (' ' on Blue)
    code.extend([0xF3, 0xAB])                   # rep stosw

    # Helper to invoke write_plane
    wp_calls = []
    def emit_plane_write(str_patch_key, di_offset, attr_byte):
        nonlocal code
        idx_s = len(code) + 1
        code.extend([0xBE, 0x00, 0x00])         # mov si, str_<key>
        code.extend([0xBF])
        code.extend(struct.pack("<H", di_offset)) # mov di, di_offset
        code.extend([0xB5, attr_byte])          # mov ch, attr_byte
        idx_c = len(code)
        code.extend([0xE8, 0x00, 0x00])         # call write_plane
        wp_calls.append(idx_c)
        return idx_s

    # Top Menu Bar: Row 0 (DI = 0), Attribute = 0x70 (Black on Light Gray)
    idx_top = emit_plane_write("top", 0, 0x70)

    # Window Titlebar: Row 2, Col 3 (DI = (2*80 + 3)*2 = 326), Attribute = 0x1E (Yellow on Blue)
    idx_win_top = emit_plane_write("win_top", 326, 0x1E)

    # Row 3: Subtitle / OS version: DI = (3*80 + 3)*2 = 486, Attribute = 0x0F (White on Black)
    idx_win_r3 = emit_plane_write("win_r3", 486, 0x0F)

    # Row 4: Hardware specs: DI = (4*80 + 3)*2 = 646, Attribute = 0x07 (Light Gray on Black)
    idx_win_r4 = emit_plane_write("win_r4", 646, 0x07)

    # Row 5: Wi-Fi status: DI = (5*80 + 3)*2 = 806, Attribute = 0x0A (Light Green on Black)
    idx_win_r5 = emit_plane_write("win_r5", 806, 0x0A)

    # Row 6: Divider: DI = (6*80 + 3)*2 = 966, Attribute = 0x08 (Dark Gray on Black)
    idx_win_r6 = emit_plane_write("win_r6", 966, 0x08)

    # Row 7: Command hints: DI = (7*80 + 3)*2 = 1126, Attribute = 0x0B (Light Cyan on Black)
    idx_win_r7 = emit_plane_write("win_r7", 1126, 0x0B)

    # Row 8: Divider: DI = (8*80 + 3)*2 = 1286, Attribute = 0x08 (Dark Gray on Black)
    idx_win_r8 = emit_plane_write("win_r8", 1286, 0x08)

    # Row 9: Prompt row: DI = (9*80 + 3)*2 = 1446, Attribute = 0x0F (White on Black)
    idx_win_r9 = emit_plane_write("win_r9", 1446, 0x0F)

    # Rows 10 to 21: Clear window interior with black lines (DI = (r*80 + 3)*2)
    win_row_patches = []
    for r in range(10, 22):
        s_idx = emit_plane_write("win_empty", (r*80 + 3)*2, 0x07)
        win_row_patches.append(s_idx)

    # Window Bottom Border: Row 22, Col 3 (DI = (22*80 + 3)*2 = 3526), Attribute = 0x1E
    idx_win_bot = emit_plane_write("win_bot", 3526, 0x1E)

    # Window Drop Shadow on right side (Col 77, Rows 3 to 22)
    for r in range(3, 23):
        # DI = (r*80 + 77)*2, write ' ' with black attribute 0x00
        code.extend([0xBF])
        code.extend(struct.pack("<H", (r*80 + 77)*2))
        code.extend([0xB8, 0x20, 0x08])         # mov ax, 0x0820 (dark gray space shadow)
        code.extend([0xAB])                     # stosw

    # Taskbar: Row 24 (DI = (24*80 + 0)*2 = 3840), Attribute = 0x70 (Black on Light Gray)
    idx_taskbar = emit_plane_write("taskbar", 3840, 0x70)

    # Restore ES = 0000 for RAM string & buffer operations
    code.extend([0x31, 0xC0])                   # xor ax, ax
    code.extend([0x8E, 0xC0])                   # mov es, ax
    code.extend([0xC3])                         # ret from draw_desktop

    # ── write_plane subroutine
    offset_write_plane = len(code)
    code.extend([0xAC])                         # lodsb
    code.extend([0x84, 0xC0])                   # test al, al
    code.extend([0x74, 0x05])                   # jz .wp_done
    code.extend([0x8A, 0xE5])                   # mov ah, ch (attribute)
    code.extend([0xAB])                         # stosw
    rel_wp = (offset_write_plane - (len(code) + 2)) & 0xFF
    code.extend([0xEB, rel_wp])
    code.extend([0xC3])                         # ret

    # Patch call_pnl calls:
    struct.pack_into("<h", code, idx_call_pnl + 1, offset_pnl - (idx_call_pnl + 3))
    struct.pack_into("<h", code, idx_call_pnl_in_ps + 1, offset_pnl - (idx_call_pnl_in_ps + 3))

    # Patch write_plane calls:
    for c in wp_calls:
        struct.pack_into("<h", code, c + 1, offset_write_plane - (c + 3))

    # Patch print_str calls:
    all_ps_calls = [idx_call_unk, idx_call_upr, idx_call_epr]
    for k in cmd_calls:
        all_ps_calls.append(cmd_calls[k])
    for c in all_ps_calls:
        struct.pack_into("<h", code, c + 1, offset_print_str - (c + 3))

    # ── Strings Table (stored directly after code in Sector 2..17)
    str_map = {}
    def add_str(key, s_bytes):
        str_map[key] = BASE_ADDR + len(code)
        code.extend(s_bytes)

    # Exact 74-character width elements (Cols 3 to 76 inclusive):
    # Left border: 1 byte, Content: 72 bytes, Right border: 1 byte = 74 bytes total!
    c_top_border = bytes([0xC9]) + (bytes([0xCD]) * 2) + b"[ Win11 Terminal: macha@micro-os ]" + (bytes([0xCD]) * 25) + b"[-][+][X]" + (bytes([0xCD]) * 2) + bytes([0xBB, 0])
    c_bot_border = bytes([0xC8]) + (bytes([0xCD]) * 72) + bytes([0xBC, 0])
    c_empty_row  = bytes([0xBA]) + (b" " * 72) + bytes([0xBA, 0])
    c_div_row    = bytes([0xBA]) + b"  " + (b"-" * 68) + b"  " + bytes([0xBA, 0])
    c_r3         = bytes([0xBA]) + b"  " + b"Windows 11 Fluent OS [Version 10.0.22631.3296]".ljust(69) + b" " + bytes([0xBA, 0])
    c_r4         = bytes([0xBA]) + b"  " + b"Hardware: Intel(R) Wi-Fi 6 AX203  *  virtio-net (192.168.1.142)".ljust(69) + b" " + bytes([0xBA, 0])
    c_r5         = bytes([0xBA]) + b"  " + b"Wi-Fi AP:  'Jain_Student' (5 GHz, Ch 44, Signal 92%) - Connected OK".ljust(69) + b" " + bytes([0xBA, 0])
    c_r7         = bytes([0xBA]) + b"  " + b"Commands: help, ls, dir, wifi, snap, files, ping, winver, clear".ljust(69) + b" " + bytes([0xBA, 0])
    c_r9         = bytes([0xBA]) + b"  " + b"C:\\Users\\macha> ".ljust(69) + b" " + bytes([0xBA, 0])

    # Top Menu Bar (exact 80 chars)
    s_top = b" Win11 Fluent OS   File   Edit   View   Terminal   Wi-Fi   Settings   Help     \0"
    # Taskbar (exact 80 chars)
    s_taskbar = b" [24C Sunny]  [Start] [Search] [Term] [Files] [Store]  [WiFi: Jain_Student 92%] 14:12 \0"

    add_str("top",       s_top)
    add_str("win_top",   c_top_border)
    add_str("win_r3",    c_r3)
    add_str("win_r4",    c_r4)
    add_str("win_r5",    c_r5)
    add_str("win_r6",    c_div_row)
    add_str("win_r7",    c_r7)
    add_str("win_r8",    c_div_row)
    add_str("win_r9",    c_r9)
    add_str("win_empty", c_empty_row)
    add_str("win_bot",   c_bot_border)
    add_str("taskbar",   s_taskbar)

    # Command Response Strings:
    add_str("msg_prompt", b"  C:\\Users\\macha> \0")
    add_str("msg_unknown", b"  Unknown command. Type 'help' for full list of commands.\r\n\0")
    add_str("msg_help", (
        b"  Commands available in Windows 11 Fluent OS:\r\n"
        b"    wifi     - Display active Wi-Fi & scan nearby networks\r\n"
        b"    ls / dir - List files and directories in C:\\Users\\macha\r\n"
        b"    cat/type - Display file contents (e.g. cat welcome.txt)\r\n"
        b"    files    - File Explorer overview\r\n"
        b"    snap     - App Store package manager (core22, doom, calc)\r\n"
        b"    ping     - Network diagnostics (ping 8.8.8.8)\r\n"
        b"    ipconfig - Network adapter IP and MAC addresses\r\n"
        b"    winver   - OS build and system specifications\r\n"
        b"    clear    - Redraw graphical desktop & clear terminal\r\n"
        b"    reboot   - Restart operating system\r\n\0"
    ))
    add_str("msg_wifi", (
        b"  [Wi-Fi Status] Adapter: Intel(R) Wi-Fi 6 AX203 (MAC: 90:10:57:c0:0b:7a)\r\n"
        b"  Connected to: 'Jain_Student' (Signal: 92%, 5 GHz, Channel: 44, Open)\r\n"
        b"  IPv4 Address: 192.168.1.142   Subnet: 255.255.255.0   Gateway: 192.168.1.1\r\n"
        b"  Available Wi-Fi Networks nearby:\r\n"
        b"    * Jain_Student   [92%]  5 GHz   Ch 44  [CONNECTED]\r\n"
        b"      Jain_Faculty   [88%]  5 GHz   Ch 48  WPA2-Enterprise\r\n"
        b"      eduroam        [76%]  5 GHz   Ch 36  WPA2-Enterprise\r\n"
        b"      Jain_Guest     [68%]  2.4 GHz Ch 6   Open\r\n"
        b"      Direct-Roku-22 [45%]  2.4 GHz Ch 11  WPA2-Personal\r\n\0"
    ))
    add_str("msg_ls", (
        b"  Directory of C:\\Users\\macha:\r\n"
        b"    21-11-2026  14:12  <DIR>          Desktop\r\n"
        b"    21-11-2026  14:12  <DIR>          Documents\r\n"
        b"    21-11-2026  14:12  <DIR>          Downloads\r\n"
        b"    21-11-2026  14:12            184  welcome.txt\r\n"
        b"    21-11-2026  14:12            240  notes.md\r\n"
        b"    21-11-2026  14:12            310  todo.list\r\n"
        b"    3 File(s) 734 bytes  |  3 Dir(s) 3,820,442,624 bytes free\r\n\0"
    ))
    add_str("msg_dir", (
        b"  Volume in drive C is WINDOWS11\r\n"
        b"  Volume Serial Number is 2026-1121\r\n"
        b"  Directory of C:\\Users\\macha\r\n"
        b"    21-11-2026  14:12  <DIR>          .\r\n"
        b"    21-11-2026  14:12  <DIR>          ..\r\n"
        b"    21-11-2026  14:12  <DIR>          Desktop\r\n"
        b"    21-11-2026  14:12  <DIR>          Documents\r\n"
        b"    21-11-2026  14:12            184  welcome.txt\r\n"
        b"    21-11-2026  14:12            240  notes.md\r\n"
        b"    21-11-2026  14:12            310  todo.list\r\n\0"
    ))
    add_str("msg_files", (
        b"  [File Explorer] Location: C:\\Users\\macha\\\r\n"
        b"  [DIR] Desktop    [DIR] Documents    [DIR] Downloads\r\n"
        b"  * welcome.txt (184 B)  - Windows 11 Fluent OS Guide\r\n"
        b"  * notes.md    (240 B)  - Wi-Fi 6 AX203 Configuration\r\n"
        b"  * todo.list   (310 B)  - System tasks and benchmarks\r\n\0"
    ))
    add_str("msg_snap", (
        b"  [Microsoft / Snap App Store - Channel: stable/22H2]\r\n"
        b"  Installed:\r\n"
        b"    * core22          [v2.0.4]   System runtime base\r\n"
        b"    * virtio-net      [v1.8.2]   Virtual Network Adapter\r\n"
        b"    * wlan-ax203      [v22.10]   Intel Wi-Fi 6 Driver\r\n"
        b"  Available for install:\r\n"
        b"    * doom            [1993]     Classic DOOM game engine\r\n"
        b"    * snake           [v1.2]     Retro Terminal Snake\r\n"
        b"    * calc            [v3.0]     Fluent Scientific Calculator\r\n\0"
    ))
    add_str("msg_ping", (
        b"  Pinging 8.8.8.8 with 32 bytes of data:\r\n"
        b"  Reply from 8.8.8.8: bytes=32 time=11.4ms TTL=118\r\n"
        b"  Reply from 8.8.8.8: bytes=32 time=10.8ms TTL=118\r\n"
        b"  Reply from 8.8.8.8: bytes=32 time=11.2ms TTL=118\r\n"
        b"  Ping statistics: 3 sent, 3 received, 0% packet loss (avg 11.1ms)\r\n\0"
    ))
    add_str("msg_ipconfig", (
        b"  Windows IP Configuration:\r\n"
        b"  Wireless LAN adapter Wi-Fi:\r\n"
        b"    Connection-specific DNS Suffix  . : jain.lan\r\n"
        b"    Description . . . . . . . . . . . : Intel(R) Wi-Fi 6 AX203\r\n"
        b"    Physical Address. . . . . . . . . : 90-10-57-C0-0B-7A\r\n"
        b"    IPv4 Address. . . . . . . . . . . : 192.168.1.142\r\n"
        b"    Subnet Mask . . . . . . . . . . . : 255.255.255.0\r\n"
        b"    Default Gateway . . . . . . . . . : 192.168.1.1\r\n\0"
    ))
    add_str("msg_winver", (
        b"  Microsoft Windows 11 Fluent OS [Version 10.0.22631.3296]\r\n"
        b"  (c) Microsoft Corporation. All rights reserved.\r\n"
        b"  Hardware: Intel(R) Core(TM) i5/i7 Processor  *  4096 MB RAM\r\n"
        b"  Display: VBoxSVGA 80x25 High-Intensity 16-Color Fluent Frame\r\n"
        b"  Wi-Fi Adapter: Intel(R) Wi-Fi 6 AX203 (Active AP: Jain_Student 92%)\r\n\0"
    ))
    add_str("msg_type", (
        b"  === C:\\Users\\macha\\welcome.txt ===\r\n"
        b"  Welcome to Windows 11 Fluent Micro-OS!\r\n"
        b"  Connected to: 'Jain_Student' (Intel Wi-Fi 6 AX203, Signal: 92%)\r\n"
        b"  Type 'help' to see all available commands.\r\n\0"
    ))

    # Patch String Addresses:
    def patch_str_ptr(code_idx, key):
        struct.pack_into("<H", code, code_idx, str_map[key])

    patch_str_ptr(idx_patch_unk, "msg_unknown")
    patch_str_ptr(idx_patch_upr, "msg_prompt")
    patch_str_ptr(idx_patch_epr, "msg_prompt")

    patch_str_ptr(idx_top,       "top")
    patch_str_ptr(idx_win_top,   "win_top")
    patch_str_ptr(idx_win_r3,    "win_r3")
    patch_str_ptr(idx_win_r4,    "win_r4")
    patch_str_ptr(idx_win_r5,    "win_r5")
    patch_str_ptr(idx_win_r6,    "win_r6")
    patch_str_ptr(idx_win_r7,    "win_r7")
    patch_str_ptr(idx_win_r8,    "win_r8")
    patch_str_ptr(idx_win_r9,    "win_r9")
    patch_str_ptr(idx_win_bot,   "win_bot")
    patch_str_ptr(idx_taskbar,   "taskbar")

    for s_idx in win_row_patches:
        patch_str_ptr(s_idx, "win_empty")

    for name in unique_cmds:
        patch_str_ptr(cmd_patches[name], f"msg_{name}")
        patch_str_ptr(cmd_patches[f"p_{name}"], "msg_prompt")

    # Pad Sector 2..17 to 16 sectors = 8192 bytes
    target_len = 16 * 512
    if len(code) > target_len:
        raise ValueError(f"Code size ({len(code)}) exceeds 16 sectors ({target_len})")
    code.extend(b"\x00" * (target_len - len(code)))

    full_image = bytearray(sec1) + bytes(code)
    print(f"[+] Assembled Full Windows 11 GUI Boot Image: {len(full_image)} bytes (17 sectors = 8704 bytes)")
    return bytes(full_image)

if __name__ == "__main__":
    img = build_full_gui_system()
    with open("micro-os-kernel.bin", "wb") as f:
        f.write(img)
    print("[+] Wrote micro-os-kernel.bin successfully!")
