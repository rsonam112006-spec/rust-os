//! Built-in Micro-OS Desktop Applications
//!
//! Provides the visual client content for all system applications:
//! - Browser: Network Navigator & Ping Diagnostic Center
//! - Terminal: PowerTerminal interactive micro-shell
//! - TaskManager: Activity Monitor with real-time CPU graph
//! - FileExplorer: MicroFinder file system browser
//! - Settings: About Micro-OS and system specs

pub mod browser;
pub mod file_explorer;
pub mod settings;
pub mod snap_store;
pub mod task_manager;
pub mod terminal;
pub mod wifi;

pub use browser::BrowserApp;
pub use file_explorer::FileExplorerApp;
pub use settings::SettingsApp;
pub use snap_store::SnapStoreApp;
pub use task_manager::TaskManagerApp;
pub use terminal::TerminalApp;
pub use wifi::WifiApp;

use crate::gui::framebuffer::Framebuffer;
use crate::gui::window::AppType;
use crate::net::NetworkStack;
use crate::task::TaskManager;

pub struct ApplicationHub {
    pub browser: BrowserApp,
    pub terminal: TerminalApp,
    pub task_manager: TaskManagerApp,
    pub file_explorer: FileExplorerApp,
    pub settings: SettingsApp,
    pub wifi: WifiApp,
    pub snap_store: SnapStoreApp,
}

impl ApplicationHub {
    pub const fn new() -> Self {
        Self {
            browser: BrowserApp::new(),
            terminal: TerminalApp::new(),
            task_manager: TaskManagerApp::new(),
            file_explorer: FileExplorerApp::new(),
            settings: SettingsApp::new(),
            wifi: WifiApp::new(),
            snap_store: SnapStoreApp::new(),
        }
    }

    pub fn render_app(
        &self,
        app_type: AppType,
        fb: &mut Framebuffer,
        x: i32,
        y: i32,
        w: u32,
        h: u32,
        net: &NetworkStack,
        tm: &TaskManager,
    ) {
        match app_type {
            AppType::Browser => self.browser.render(fb, x, y, w, h, net),
            AppType::Terminal => self.terminal.render(fb, x, y, w, h),
            AppType::TaskManager => self.task_manager.render(fb, x, y, w, h, tm),
            AppType::Explorer => self.file_explorer.render(fb, x, y, w, h),
            AppType::Settings => self.settings.render(fb, x, y, w, h),
            AppType::Wifi => self.wifi.render(fb, x, y, w, h, net),
            AppType::SnapStore => self.snap_store.render(fb, x, y, w, h),
        }
    }
}
