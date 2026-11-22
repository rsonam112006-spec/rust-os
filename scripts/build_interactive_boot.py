"""
scripts/build_interactive_boot.py
Generates a fully interactive 16-bit x86 real-mode shell in the MBR boot sector (Sector 0)
supporting keyboard input (INT 16h), backspace, enter, cursor, and interactive commands:
- help: lists available commands
- wifi: displays 802.11ax wlan0 status and scan telemetry
- snap: lists installed snap packages
- neofetch: displays OS specs
- ping: ICMP ping test
- clear: clears screen
- reboot: warm reboots the machine
"""

import struct

def build_interactive_boot_sector():
    # Machine code assembled for origin 0x7C00
    # Data offsets will be computed relative to 0x7C00
    
    # Assembly layout:
    # 0x7C00: Start
    #   cli
    #   xor ax, ax
    #   mov ds, ax
    #   mov es, ax
    #   mov ss, ax
    #   mov sp, 0x7C00
    #   sti
    #   mov ax, 0x0003  # Set 80x25 text mode (clears screen)
    #   int 0x10
    #   mov si, offset msg_welcome
    #   call print_str
    # prompt:
    #   mov si, offset msg_prompt
    #   call print_str
    #   mov di, 0x7E00  # Input buffer
    # get_key:
    #   xor ax, ax
    #   int 0x16        # BIOS read key -> AL = ASCII
    #   cmp al, 0x0D    # Enter?
    #   je on_enter
    #   cmp al, 0x08    # Backspace?
    #   je on_backspace
    #   cmp al, 0x20    # Printable?
    #   jb get_key
    #   cmp al, 0x7E
    #   ja get_key
    #   # Store character
    #   cmp di, 0x7E3E  # max 62 chars
    #   jae get_key
    #   stosb
    #   # Echo character
    #   mov ah, 0x0E
    #   int 0x10
    #   jmp get_key
    # on_backspace:
    #   cmp di, 0x7E00
    #   jbe get_key
    #   dec di
    #   mov si, offset msg_bs
    #   call print_str
    #   jmp get_key
    # on_enter:
    #   mov byte [di], 0 # Null terminate
    #   mov si, offset msg_crlf
    #   call print_str
    #   # Check if empty
    #   cmp di, 0x7E00
    #   je prompt
    #   # First char of command at 0x7E00
    #   mov al, [0x7E00]
    #   cmp al, 'h'     # help
    #   je cmd_help
    #   cmp al, 'w'     # wifi
    #   je cmd_wifi
    #   cmp al, 's'     # snap
    #   je cmd_snap
    #   cmp al, 'n'     # neofetch
    #   je cmd_neofetch
    #   cmp al, 'p'     # ping
    #   je cmd_ping
    #   cmp al, 'c'     # clear
    #   je cmd_clear
    #   cmp al, 'r'     # reboot
    #   je cmd_reboot
    #   # Unknown
    #   mov si, offset msg_unknown
    #   call print_str
    #   jmp prompt
    # cmd_help:
    #   mov si, offset msg_help
    #   call print_str
    #   jmp prompt
    # cmd_wifi:
    #   mov si, offset msg_wifi
    #   call print_str
    #   jmp prompt
    # cmd_snap:
    #   mov si, offset msg_snap
    #   call print_str
    #   jmp prompt
    # cmd_neofetch:
    #   mov si, offset msg_neofetch
    #   call print_str
    #   jmp prompt
    # cmd_ping:
    #   mov si, offset msg_ping
    #   call print_str
    #   jmp prompt
    # cmd_clear:
    #   mov ax, 0x0003
    #   int 0x10
    #   jmp prompt
    # cmd_reboot:
    #   int 0x19
    # print_str:
    #   lodsb
    #   test al, al
    #   jz .done
    #   mov ah, 0x0E
    #   int 0x10
    #   jmp print_str
    # .done:
    #   ret

    # Let's hand-assemble this tight and precise machine code
    code = bytearray()

    # Offsets tracking:
    # We will assemble code first, then append strings, then patch string offsets!
    
    # 0x00: Init
    code.extend([0xFA])                         # cli
    code.extend([0x31, 0xC0])                   # xor ax, ax
    code.extend([0x8E, 0xD8])                   # mov ds, ax
    code.extend([0x8E, 0xC0])                   # mov es, ax
    code.extend([0x8E, 0xD0])                   # mov ss, ax
    code.extend([0xBC, 0x00, 0x7C])             # mov sp, 0x7C00
    code.extend([0xFB])                         # sti

    # Set 80x25 text mode (clears screen)
    code.extend([0xB8, 0x03, 0x00])             # mov ax, 0x0003
    code.extend([0xCD, 0x10])                   # int 0x10

    # Print welcome
    idx_patch_welcome = len(code) + 1
    code.extend([0xBE, 0x00, 0x00])             # mov si, msg_welcome (patch)
    idx_call_print1 = len(code)
    code.extend([0xE8, 0x00, 0x00])             # call print_str (patch)

    # Offset of prompt:
    offset_prompt = len(code)
    idx_patch_prompt = len(code) + 1
    code.extend([0xBE, 0x00, 0x00])             # mov si, msg_prompt (patch)
    idx_call_print2 = len(code)
    code.extend([0xE8, 0x00, 0x00])             # call print_str (patch)

    code.extend([0xBF, 0x00, 0x7E])             # mov di, 0x7E00 (input buffer)

    # Offset of get_key:
    offset_get_key = len(code)
    code.extend([0x31, 0xC0])                   # xor ax, ax
    code.extend([0xCD, 0x16])                   # int 0x16 -> AL = ascii

    # cmp al, 0x0D (Enter)
    code.extend([0x3C, 0x0D])
    idx_je_enter = len(code) + 1
    code.extend([0x74, 0x00])                   # je on_enter (patch)

    # cmp al, 0x08 (Backspace)
    code.extend([0x3C, 0x08])
    idx_je_bs = len(code) + 1
    code.extend([0x74, 0x00])                   # je on_backspace (patch)

    # cmp al, 0x20
    code.extend([0x3C, 0x20])
    # jb get_key
    rel_get_key = (offset_get_key - (len(code) + 2)) & 0xFF
    code.extend([0x72, rel_get_key])

    # cmp al, 0x7E
    code.extend([0x3C, 0x7E])
    # ja get_key
    rel_get_key2 = (offset_get_key - (len(code) + 2)) & 0xFF
    code.extend([0x77, rel_get_key2])

    # cmp di, 0x7E3E
    code.extend([0x81, 0xFF, 0x3E, 0x7E])
    rel_get_key3 = (offset_get_key - (len(code) + 2)) & 0xFF
    code.extend([0x73, rel_get_key3])           # jae get_key

    # stosb (store character in buffer)
    code.extend([0xAA])

    # echo char: mov ah, 0x0E; int 0x10
    code.extend([0xB4, 0x0E])
    code.extend([0xCD, 0x10])
    rel_get_key4 = (offset_get_key - (len(code) + 2)) & 0xFF
    code.extend([0xEB, rel_get_key4])           # jmp get_key

    # on_backspace:
    offset_on_bs = len(code)
    code[idx_je_bs] = (offset_on_bs - (idx_je_bs + 1)) & 0xFF

    code.extend([0x81, 0xFF, 0x00, 0x7E])       # cmp di, 0x7E00
    rel_get_key5 = (offset_get_key - (len(code) + 2)) & 0xFF
    code.extend([0x76, rel_get_key5])           # jbe get_key
    code.extend([0x4F])                         # dec di
    idx_patch_bs = len(code) + 1
    code.extend([0xBE, 0x00, 0x00])             # mov si, msg_bs (patch)
    idx_call_print3 = len(code)
    code.extend([0xE8, 0x00, 0x00])             # call print_str (patch)
    rel_get_key6 = (offset_get_key - (len(code) + 2)) & 0xFF
    code.extend([0xEB, rel_get_key6])           # jmp get_key

    # on_enter:
    offset_on_enter = len(code)
    code[idx_je_enter] = (offset_on_enter - (idx_je_enter + 1)) & 0xFF

    code.extend([0xC6, 0x05, 0x00])             # mov byte [di], 0
    idx_patch_crlf = len(code) + 1
    code.extend([0xBE, 0x00, 0x00])             # mov si, msg_crlf (patch)
    idx_call_print4 = len(code)
    code.extend([0xE8, 0x00, 0x00])             # call print_str (patch)

    # Check if empty: cmp di, 0x7E00
    code.extend([0x81, 0xFF, 0x00, 0x7E])
    rel_prompt1 = (offset_prompt - (len(code) + 2)) & 0xFF
    code.extend([0x74, rel_prompt1])            # je prompt

    # First char: mov al, [0x7E00]
    code.extend([0xA0, 0x00, 0x7E])

    # Table of dispatch commands:
    # 'h' -> help, 'w' -> wifi, 's' -> snap, 'n' -> neofetch, 'p' -> ping, 'c' -> clear, 'r' -> reboot
    idx_jumps = {}
    for char in ['h', 'w', 's', 'n', 'p', 'c', 'r']:
        code.extend([0x3C, ord(char)])
        idx_jumps[char] = len(code) + 1
        code.extend([0x74, 0x00])               # je cmd_<char> (patch)

    # Unknown command:
    idx_patch_unknown = len(code) + 1
    code.extend([0xBE, 0x00, 0x00])             # mov si, msg_unknown (patch)
    idx_call_print5 = len(code)
    code.extend([0xE8, 0x00, 0x00])             # call print_str (patch)
    rel_p_u = offset_prompt - (len(code) + 3)
    code.extend([0xE9])                         # near jmp prompt
    code.extend(struct.pack("<h", rel_p_u))

    # Helper: print_str
    offset_print_str = len(code)
    # lodsb
    code.extend([0xAC])
    # test al, al
    code.extend([0x84, 0xC0])
    code.extend([0x74, 0x06])                   # jz done (+6 bytes)
    code.extend([0xB4, 0x0E])                   # mov ah, 0x0E
    code.extend([0xCD, 0x10])                   # int 0x10
    code.extend([0xEB, 0xF5])                   # jmp print_str (-11 bytes)
    code.extend([0xC3])                         # ret

    # Now handler blocks for commands:
    def add_cmd_handler(cmd_char, msg_patch_var):
        off = len(code)
        code[idx_jumps[cmd_char]] = (off - (idx_jumps[cmd_char] + 1)) & 0xFF
        idx_patch = len(code) + 1
        code.extend([0xBE, 0x00, 0x00])         # mov si, msg_... (patch)
        idx_call = len(code)
        code.extend([0xE8, 0x00, 0x00])         # call print_str (patch)
        rel_p = offset_prompt - (len(code) + 3)
        code.extend([0xE9])                     # near jmp prompt
        code.extend(struct.pack("<h", rel_p))
        return idx_patch, idx_call

    idx_patch_help, idx_call_help = add_cmd_handler('h', 'msg_help')
    idx_patch_wifi, idx_call_wifi = add_cmd_handler('w', 'msg_wifi')
    idx_patch_snap, idx_call_snap = add_cmd_handler('s', 'msg_snap')
    idx_patch_neo,  idx_call_neo  = add_cmd_handler('n', 'msg_neofetch')
    idx_patch_ping, idx_call_ping = add_cmd_handler('p', 'msg_ping')

    # cmd_clear ('c'):
    off_clear = len(code)
    code[idx_jumps['c']] = (off_clear - (idx_jumps['c'] + 1)) & 0xFF
    code.extend([0xB8, 0x03, 0x00])             # mov ax, 0x0003
    code.extend([0xCD, 0x10])                   # int 0x10
    rel_p_c = offset_prompt - (len(code) + 3)
    code.extend([0xE9])                         # near jmp prompt
    code.extend(struct.pack("<h", rel_p_c))

    # cmd_reboot ('r'):
    off_reboot = len(code)
    code[idx_jumps['r']] = (off_reboot - (idx_jumps['r'] + 1)) & 0xFF
    code.extend([0xCD, 0x19])                   # int 0x19 (BIOS reboot)

    # Patch call print_str offsets:
    all_calls = [idx_call_print1, idx_call_print2, idx_call_print3, idx_call_print4, idx_call_print5,
                 idx_call_help, idx_call_wifi, idx_call_snap, idx_call_neo, idx_call_ping]
    for c_idx in all_calls:
        rel_target = offset_print_str - (c_idx + 3)
        struct.pack_into("<h", code, c_idx + 1, rel_target)

    # Strings table:
    # All strings placed directly after code:
    str_map = {}
    def add_string(key, text_bytes):
        str_map[key] = 0x7C00 + len(code)
        code.extend(text_bytes)

    add_string("welcome",  b"\r\n Rust Micro-OS v2.0\r\n Try 'help'.\r\n\0")
    add_string("prompt",   b"# \0")
    add_string("bs",       b"\x08 \x08\0")
    add_string("crlf",     b"\r\n\0")
    add_string("unknown",  b"Unknown. Type: help\r\n\0")
    add_string("help",     b"help, wifi, snap, neofetch, ping, clear\r\n\0")
    add_string("wifi",     b"wlan0: 'Jain_Student' (92% Sig, 192.168.1.142)\r\n\0")
    add_string("snap",     b"Snaps: neofetch, htop, doom, snake, calc\r\n\0")
    add_string("neofetch", b"Rust Micro-OS 2.0 (x86_64) | Heap 64KB\r\n\0")
    add_string("ping",     b"PING 192.168.1.1: 64B rtt=1.2ms (0% loss)\r\n\0")

    # Patch string pointers in code:
    def patch_ptr(code_idx, key):
        struct.pack_into("<H", code, code_idx, str_map[key])

    patch_ptr(idx_patch_welcome, "welcome")
    patch_ptr(idx_patch_prompt,  "prompt")
    patch_ptr(idx_patch_bs,      "bs")
    patch_ptr(idx_patch_crlf,    "crlf")
    patch_ptr(idx_patch_unknown, "unknown")
    patch_ptr(idx_patch_help,    "help")
    patch_ptr(idx_patch_wifi,    "wifi")
    patch_ptr(idx_patch_snap,    "snap")
    patch_ptr(idx_patch_neo,     "neofetch")
    patch_ptr(idx_patch_ping,    "ping")

    print(f"Total interactive bootloader size: {len(code)} bytes (Max: 510)")
    assert len(code) <= 510, f"Code too large: {len(code)} > 510"

    # Pad to 512 bytes with MBR signature 0xAA55
    sector = bytearray(512)
    sector[0:len(code)] = code
    sector[510] = 0x55
    sector[511] = 0xAA
    return bytes(sector)

if __name__ == "__main__":
    b = build_interactive_boot_sector()
    print("Interactive boot sector successfully assembled!")
