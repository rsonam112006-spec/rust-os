//! Lightweight HTTP 1.1 Protocol Engine
//!
//! Provides request construction, response parsing, and built-in micro-web service
//! simulation for the OS web browser and `curl` command.

pub struct HttpRequest<'a> {
    pub method: &'static str,
    pub path: &'a str,
    pub host: &'a str,
    pub user_agent: &'static str,
}

impl<'a> HttpRequest<'a> {
    pub fn new_get(host: &'a str, path: &'a str) -> Self {
        Self {
            method: "GET",
            path,
            host,
            user_agent: "RustMicroOS-Browser/2.0",
        }
    }

    pub fn serialize(&self, out: &mut [u8]) -> Result<usize, &'static str> {
        let mut pos = 0;

        let append = |buf: &mut [u8], pos: &mut usize, s: &str| -> Result<(), &'static str> {
            let bytes = s.as_bytes();
            if *pos + bytes.len() > buf.len() {
                return Err("Buffer too small for HTTP request");
            }
            buf[*pos..*pos + bytes.len()].copy_from_slice(bytes);
            *pos += bytes.len();
            Ok(())
        };

        append(out, &mut pos, self.method)?;
        append(out, &mut pos, " ")?;
        append(out, &mut pos, self.path)?;
        append(out, &mut pos, " HTTP/1.1\r\nHost: ")?;
        append(out, &mut pos, self.host)?;
        append(out, &mut pos, "\r\nUser-Agent: ")?;
        append(out, &mut pos, self.user_agent)?;
        append(out, &mut pos, "\r\nConnection: close\r\n\r\n")?;

        Ok(pos)
    }
}

pub struct HttpResponse<'a> {
    pub status_code: u16,
    pub status_text: &'a str,
    pub content_type: &'a str,
    pub body: &'a str,
}

impl<'a> HttpResponse<'a> {
    pub fn parse(raw: &'a str) -> Result<Self, &'static str> {
        if !raw.starts_with("HTTP/1.1 ") && !raw.starts_with("HTTP/1.0 ") {
            return Err("Invalid HTTP response header");
        }

        let first_line_end = raw.find("\r\n").ok_or("No status line end")?;
        let status_line = &raw[9..first_line_end];
        let mut parts = status_line.splitn(2, ' ');
        let code_str = parts.next().ok_or("Missing status code")?;
        let status_text = parts.next().unwrap_or("OK");

        let status_code: u16 = code_str.parse().map_err(|_| "Invalid status code number")?;

        let body_start = if let Some(idx) = raw.find("\r\n\r\n") {
            idx + 4
        } else {
            raw.len()
        };

        let body = &raw[body_start..];

        Ok(Self {
            status_code,
            status_text,
            content_type: "text/html",
            body,
        })
    }
}

/// Built-in micro web server responses for local loopback testing
pub fn handle_local_http(path: &str) -> &'static str {
    match path {
        "/" | "/index.html" | "/welcome" => {
            "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nConnection: close\r\n\r\n\
            <!DOCTYPE html>\n\
            <html>\n\
            <head><title>Welcome to Rust Micro-OS</title></head>\n\
            <body style='font-family: sans-serif; background: #121214; color: #EEE; padding: 20px;'>\n\
            <h1 style='color: #0A84FF;'>Welcome to Rust Micro-OS v2.0!</h1>\n\
            <p>You are viewing this web page served from inside the <b>Rust Microkernel Network Stack</b>.</p>\n\
            <ul>\n\
            <li>Full TCP/IP & ICMP protocol integration</li>\n\
            <li>macOS & Windows 11 Fluent Desktop Compositor</li>\n\
            <li>Preemptive Round Robin & Priority Aging Scheduler</li>\n\
            <li>Zero C dependencies & 100% Rust memory safety</li>\n\
            </ul>\n\
            <p>Status: <span style='color: #30D158;'>Online & Connected</span> (10 Gbps Ethernet)</p>\n\
            </body>\n\
            </html>"
        }
        "/system" => {
            "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nConnection: close\r\n\r\n\
            OS: Rust Micro-OS 2.0\n\
            Kernel: Microkernel x86_64\n\
            NIC: virtio-net0 (MAC: 52:54:00:12:34:56)\n\
            IP: 192.168.1.142 / 24\n\
            Gateway: 192.168.1.1\n\
            Heap Allocator: Coalescing Free-List (64 KiB)\n\
            Scheduler: Preemptive Round Robin (Q=3)\n"
        }
        _ => {
            "HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\nConnection: close\r\n\r\n\
            404 Not Found: The requested resource was not located on this micro-kernel."
        }
    }
}
