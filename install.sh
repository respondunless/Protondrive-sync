#!/bin/bash

# ProtonDrive Sync - Super Easy Installer
# Makes installation a breeze for new Linux users! 🚀

set -e

# Colors for beautiful output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Emojis for fun!
CHECK="✓"
CROSS="✗"
ARROW="→"
STAR="★"
ROCKET="🚀"
PACKAGE="📦"
WRENCH="🔧"
COMPUTER="💻"

# Installation settings
INSTALL_DIR=""
INSTALL_TYPE=""
AUTO_START=false
APP_NAME="ProtonDrive Sync"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

#######################
# Helper Functions
#######################

print_header() {
    echo ""
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                                                            ║${NC}"
    echo -e "${CYAN}║${WHITE}           ProtonDrive Sync - Easy Installer ${ROCKET}            ${CYAN}║${NC}"
    echo -e "${CYAN}║                                                            ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_step() {
    echo -e "\n${BLUE}${ARROW} $1${NC}"
}

print_success() {
    echo -e "${GREEN}${CHECK} $1${NC}"
}

print_error() {
    echo -e "${RED}${CROSS} $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${CYAN}ℹ $1${NC}"
}

ask_yes_no() {
    local prompt="$1"
    local default="${2:-n}"
    local response
    
    if [[ "$default" == "y" ]]; then
        prompt="$prompt [Y/n]: "
    else
        prompt="$prompt [y/N]: "
    fi
    
    while true; do
        read -p "$(echo -e ${YELLOW}${prompt}${NC})" response < /dev/tty
        response=${response:-$default}
        case "$response" in
            [Yy]* ) return 0;;
            [Nn]* ) return 1;;
            * ) echo -e "${RED}Please answer yes or no.${NC}";;
        esac
    done
}

detect_distro() {
    print_step "Detecting your Linux distribution..."
    
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO=$ID
        DISTRO_PRETTY=$PRETTY_NAME
        
        # Special detection for CachyOS
        if [[ "$DISTRO" == "cachyos" ]]; then
            print_success "Detected: $DISTRO_PRETTY 🚀"
            print_info "CachyOS detected - using optimized settings for Arch-based systems!"
            CACHYOS_DETECTED=true
        else
            print_success "Detected: $DISTRO_PRETTY"
            CACHYOS_DETECTED=false
        fi
    else
        print_error "Cannot detect Linux distribution"
        exit 1
    fi
}

check_sudo() {
    if [[ "$INSTALL_TYPE" == "system" ]]; then
        print_step "Checking sudo permissions..."
        
        # Try to get sudo access
        if ! sudo -v &>/dev/null; then
            echo ""
            print_error "System-wide installation requires sudo privileges"
            echo ""
            echo -e "${YELLOW}╔════════════════════════════════════════════════════════════╗${NC}"
            echo -e "${YELLOW}║                  Permission Required                       ║${NC}"
            echo -e "${YELLOW}╚════════════════════════════════════════════════════════════╝${NC}"
            echo ""
            echo -e "${WHITE}To install system-wide, you need sudo access.${NC}"
            echo ""
            echo -e "${CYAN}Option 1 - Run with sudo:${NC}"
            echo -e "  ${WHITE}sudo bash install.sh${NC}"
            echo ""
            echo -e "${CYAN}Option 2 - User-only install (no sudo needed):${NC}"
            echo -e "  Run the installer again and choose option 2"
            echo -e "  This installs to ~/.local/share (only for your user)"
            echo ""
            exit 1
        fi
        
        # Keep sudo alive in background
        (while true; do sudo -n true; sleep 50; done 2>/dev/null) &
        SUDO_REFRESH_PID=$!
        
        print_success "Sudo privileges confirmed"
    fi
}

install_dependencies() {
    print_step "Installing dependencies ${PACKAGE}"
    
    case "$DISTRO" in
        arch|cachyos|manjaro|endeavouros|garuda)
            print_info "Installing packages for Arch-based system..."
            
            # CachyOS-specific optimizations
            if [[ "$CACHYOS_DETECTED" == true ]]; then
                print_info "🚀 Applying CachyOS optimizations..."
                
                # Check for AUR helper availability
                if command -v yay &>/dev/null; then
                    print_success "yay detected - you can use it for additional packages if needed"
                elif command -v paru &>/dev/null; then
                    print_success "paru detected - you can use it for additional packages if needed"
                else
                    print_info "Tip: Consider installing an AUR helper (yay or paru) for easier package management"
                fi
                
                # Use optimized pacman settings for CachyOS
                print_info "Using optimized pacman for faster installation..."
            fi
            
            if [[ "$INSTALL_TYPE" == "system" ]]; then
                sudo pacman -Sy --noconfirm --needed python python-pip python-pyqt5 rclone git || {
                    print_error "Failed to install system packages"
                    exit 1
                }
            else
                # For user install, check if packages are available
                if ! command -v python3 &>/dev/null; then
                    print_warning "Python3 not found. Installing system-wide (requires sudo)..."
                    sudo pacman -Sy --noconfirm --needed python python-pip || exit 1
                fi
                if ! command -v rclone &>/dev/null; then
                    print_warning "rclone not found. Installing system-wide (requires sudo)..."
                    sudo pacman -Sy --noconfirm --needed rclone || exit 1
                fi
            fi
            
            # CachyOS-specific post-install notes
            if [[ "$CACHYOS_DETECTED" == true ]]; then
                print_success "Packages installed with CachyOS optimizations!"
                print_info "CachyOS users: Your system's performance optimizations will benefit sync operations"
            fi
            ;;
            
        ubuntu|debian|linuxmint|pop|elementary)
            print_info "Installing packages for Debian-based system..."
            if [[ "$INSTALL_TYPE" == "system" ]]; then
                sudo apt-get update
                sudo apt-get install -y python3 python3-pip python3-pyqt5 rclone git || {
                    print_error "Failed to install system packages"
                    exit 1
                }
            else
                if ! command -v python3 &>/dev/null; then
                    print_warning "Python3 not found. Installing system-wide (requires sudo)..."
                    sudo apt-get update && sudo apt-get install -y python3 python3-pip || exit 1
                fi
                if ! command -v rclone &>/dev/null; then
                    print_warning "rclone not found. Installing system-wide (requires sudo)..."
                    sudo apt-get install -y rclone || exit 1
                fi
            fi
            ;;
            
        fedora|rhel|centos|rocky|almalinux)
            print_info "Installing packages for Fedora-based system..."
            if [[ "$INSTALL_TYPE" == "system" ]]; then
                sudo dnf install -y python3 python3-pip python3-qt5 rclone git || {
                    print_error "Failed to install system packages"
                    exit 1
                }
            else
                if ! command -v python3 &>/dev/null; then
                    print_warning "Python3 not found. Installing system-wide (requires sudo)..."
                    sudo dnf install -y python3 python3-pip || exit 1
                fi
                if ! command -v rclone &>/dev/null; then
                    print_warning "rclone not found. Installing system-wide (requires sudo)..."
                    sudo dnf install -y rclone || exit 1
                fi
            fi
            ;;
            
        opensuse*|sles)
            print_info "Installing packages for openSUSE-based system..."
            if [[ "$INSTALL_TYPE" == "system" ]]; then
                sudo zypper install -y python3 python3-pip python3-qt5 rclone git || {
                    print_error "Failed to install system packages"
                    exit 1
                }
            else
                if ! command -v python3 &>/dev/null; then
                    print_warning "Python3 not found. Installing system-wide (requires sudo)..."
                    sudo zypper install -y python3 python3-pip || exit 1
                fi
                if ! command -v rclone &>/dev/null; then
                    print_warning "rclone not found. Installing system-wide (requires sudo)..."
                    sudo zypper install -y rclone || exit 1
                fi
            fi
            ;;
            
        *)
            print_warning "Unknown distribution: $DISTRO"
            print_info "Attempting generic installation..."
            if ! command -v python3 &>/dev/null || ! command -v rclone &>/dev/null; then
                print_error "Please install python3, pip, PyQt5, and rclone manually"
                exit 1
            fi
            ;;
    esac
    
    print_success "System dependencies installed"
}

install_python_packages() {
    print_step "Installing Python packages..."
    
    local pip_cmd="pip3"
    local pip_args=""
    
    if [[ "$INSTALL_TYPE" == "user" ]]; then
        pip_args="--user"
    fi
    
    # Check if PyQt5 is already installed system-wide
    if python3 -c "import PyQt5" &>/dev/null; then
        print_success "PyQt5 already installed"
    else
        print_info "Installing PyQt5..."
        $pip_cmd install $pip_args PyQt5 || {
            print_warning "PyQt5 installation via pip failed, trying system package..."
            case "$DISTRO" in
                arch|cachyos|manjaro|endeavouros|garuda)
                    sudo pacman -S --noconfirm --needed python-pyqt5
                    ;;
                ubuntu|debian|linuxmint|pop|elementary)
                    sudo apt-get install -y python3-pyqt5
                    ;;
                fedora|rhel|centos|rocky|almalinux)
                    sudo dnf install -y python3-qt5
                    ;;
            esac
        }
    fi
    
    print_success "Python packages ready"
}

copy_files() {
    print_step "Installing application files..."
    
    # Determine if we need sudo for file operations
    local USE_SUDO=""
    if [[ "$INSTALL_TYPE" == "system" ]]; then
        USE_SUDO="sudo"
    fi
    
    # Create installation directory (idempotent)
    if [ ! -d "$INSTALL_DIR" ]; then
        print_info "Creating installation directory: $INSTALL_DIR"
        $USE_SUDO mkdir -p "$INSTALL_DIR" || {
            print_error "Failed to create installation directory"
            print_info "Make sure you have permission to create $INSTALL_DIR"
            exit 1
        }
    else
        print_info "Installation directory already exists (updating files)"
    fi
    
    # Copy source files (will overwrite if exists - making it idempotent)
    print_info "Copying application files..."
    $USE_SUDO cp -rf "$SCRIPT_DIR/protondrive_sync" "$INSTALL_DIR/" || {
        print_error "Failed to copy application files"
        exit 1
    }
    
    # Copy documentation files (optional, won't fail if missing)
    $USE_SUDO cp "$SCRIPT_DIR/README.md" "$INSTALL_DIR/" 2>/dev/null || true
    $USE_SUDO cp "$SCRIPT_DIR/docs/setup/QUICK_START.md" "$INSTALL_DIR/" 2>/dev/null || true
    $USE_SUDO cp "$SCRIPT_DIR/docs/setup/INSTALLATION_GUIDE.md" "$INSTALL_DIR/" 2>/dev/null || true
    $USE_SUDO cp "$SCRIPT_DIR/docs/setup/PROTONDRIVE_SETUP.md" "$INSTALL_DIR/" 2>/dev/null || true
    $USE_SUDO cp "$SCRIPT_DIR/LICENSE" "$INSTALL_DIR/" 2>/dev/null || true
    $USE_SUDO cp "$SCRIPT_DIR/uninstall.sh" "$INSTALL_DIR/" 2>/dev/null || true
    $USE_SUDO cp "$SCRIPT_DIR/requirements.txt" "$INSTALL_DIR/" 2>/dev/null || true
    
    # Create executable wrapper script
    print_info "Creating launcher script..."
    $USE_SUDO tee "$INSTALL_DIR/protondrive-sync" > /dev/null << 'EOF'
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
python3 -m protondrive_sync.main "$@"
EOF
    
    $USE_SUDO chmod +x "$INSTALL_DIR/protondrive-sync"
    $USE_SUDO chmod +x "$INSTALL_DIR/uninstall.sh" 2>/dev/null || true
    
    print_success "Application files installed to $INSTALL_DIR"
}

create_desktop_entry() {
    print_step "Creating desktop integration..."
    
    local desktop_dir
    local USE_SUDO=""
    
    if [[ "$INSTALL_TYPE" == "system" ]]; then
        desktop_dir="/usr/share/applications"
        USE_SUDO="sudo"
        $USE_SUDO mkdir -p "$desktop_dir"
    else
        desktop_dir="$HOME/.local/share/applications"
        mkdir -p "$desktop_dir"
    fi
    
    # Create desktop entry
    $USE_SUDO tee "$desktop_dir/protondrive-sync.desktop" > /dev/null << EOF
[Desktop Entry]
Name=ProtonDrive Sync
Comment=Sync your files with ProtonDrive
Exec=$INSTALL_DIR/protondrive-sync
Icon=folder-cloud
Terminal=false
Type=Application
Categories=Network;FileTransfer;Utility;
Keywords=proton;drive;sync;cloud;backup;
StartupNotify=true
EOF
    
    $USE_SUDO chmod +x "$desktop_dir/protondrive-sync.desktop"
    
    # Update desktop database
    if command -v update-desktop-database &>/dev/null; then
        if [[ -n "$USE_SUDO" ]]; then
            sudo update-desktop-database "$desktop_dir" 2>/dev/null || true
        else
            update-desktop-database "$desktop_dir" 2>/dev/null || true
        fi
    fi
    
    print_success "Desktop entry created - app will appear in your application menu!"
}

create_autostart_entry() {
    if $AUTO_START; then
        print_step "Setting up autostart..."
        
        local autostart_dir="$HOME/.config/autostart"
        mkdir -p "$autostart_dir"
        
        cat > "$autostart_dir/protondrive-sync.desktop" << EOF
[Desktop Entry]
Name=ProtonDrive Sync
Comment=Sync your files with ProtonDrive
Exec=$INSTALL_DIR/protondrive-sync
Icon=folder-cloud
Terminal=false
Type=Application
X-GNOME-Autostart-enabled=true
EOF
        
        print_success "Autostart enabled - app will launch on login"
    fi
}

create_bin_symlink() {
    if [[ "$INSTALL_TYPE" == "system" ]]; then
        print_step "Creating system commands..."
        sudo ln -sf "$INSTALL_DIR/protondrive-sync" /usr/local/bin/protondrive-sync
        sudo ln -sf "$INSTALL_DIR/uninstall.sh" /usr/local/bin/protondrive-sync-uninstall
        print_success "You can now run 'protondrive-sync' from anywhere!"
        print_success "To uninstall later, run: protondrive-sync-uninstall"
    else
        # For user install, add to ~/.local/bin
        local local_bin="$HOME/.local/bin"
        mkdir -p "$local_bin"
        ln -sf "$INSTALL_DIR/protondrive-sync" "$local_bin/protondrive-sync"
        ln -sf "$INSTALL_DIR/uninstall.sh" "$local_bin/protondrive-sync-uninstall"
        
        # Check if ~/.local/bin is in PATH
        if [[ ":$PATH:" != *":$local_bin:"* ]]; then
            print_warning "~/.local/bin is not in your PATH"
            print_info "Add this to your ~/.bashrc or ~/.zshrc:"
            echo -e "${WHITE}export PATH=\"\$HOME/.local/bin:\$PATH\"${NC}"
        else
            print_success "You can now run 'protondrive-sync' from anywhere!"
            print_success "To uninstall later, run: protondrive-sync-uninstall"
        fi
    fi
}

setup_config_directory() {
    print_step "Setting up configuration directory..."
    
    local config_dir="$HOME/.config/protondrive-sync"
    mkdir -p "$config_dir"
    
    print_success "Configuration directory created at $config_dir"
}

#######################
# Main Installation
#######################

main() {
    clear
    print_header
    
    echo -e "${WHITE}Welcome to the ProtonDrive Sync installer!${NC}"
    echo -e "${CYAN}This script will guide you through a super easy installation.${NC}"
    echo ""
    
    # Detect distribution
    detect_distro
    
    # Ask installation type
    echo ""
    echo -e "${WHITE}Where would you like to install the application?${NC}"
    echo -e "  ${GREEN}1)${NC} System-wide (requires sudo, available for all users)"
    echo -e "  ${GREEN}2)${NC} User-only (no sudo required, only for you)"
    echo ""
    
    while true; do
        read -p "$(echo -e ${YELLOW}Choose [1-2]: ${NC})" choice < /dev/tty
        case $choice in
            1)
                INSTALL_TYPE="system"
                INSTALL_DIR="/opt/protondrive-sync"
                break
                ;;
            2)
                INSTALL_TYPE="user"
                INSTALL_DIR="$HOME/.local/share/protondrive-sync"
                break
                ;;
            *)
                print_error "Invalid choice. Please enter 1 or 2."
                ;;
        esac
    done
    
    print_success "Installation type: $INSTALL_TYPE"
    
    # Check sudo if needed
    check_sudo
    
    # Ask about autostart
    echo ""
    if ask_yes_no "Would you like the app to start automatically when you log in?" "n"; then
        AUTO_START=true
    fi
    
    # Confirm installation
    echo ""
    echo -e "${WHITE}Ready to install with these settings:${NC}"
    echo -e "  ${CYAN}${ARROW}${NC} Installation type: $INSTALL_TYPE"
    echo -e "  ${CYAN}${ARROW}${NC} Installation directory: $INSTALL_DIR"
    echo -e "  ${CYAN}${ARROW}${NC} Autostart: $(if $AUTO_START; then echo 'Yes'; else echo 'No'; fi)"
    echo ""
    
    if ! ask_yes_no "Continue with installation?" "y"; then
        print_warning "Installation cancelled"
        exit 0
    fi
    
    # Start installation
    echo ""
    print_step "${ROCKET} Starting installation..."
    
    install_dependencies
    install_python_packages
    copy_files
    create_desktop_entry
    create_autostart_entry
    create_bin_symlink
    setup_config_directory
    
    # Installation complete
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                                                            ║${NC}"
    echo -e "${GREEN}║${WHITE}              Installation Complete! ${STAR}${STAR}${STAR}                  ${GREEN}║${NC}"
    echo -e "${GREEN}║                                                            ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    print_success "ProtonDrive Sync is now installed!"
    echo ""
    echo -e "${WHITE}How to get started:${NC}"
    echo -e "  ${CYAN}1.${NC} Open your application menu and search for '${WHITE}ProtonDrive Sync${NC}'"
    echo -e "  ${CYAN}2.${NC} Or run from terminal: ${WHITE}protondrive-sync${NC}"
    echo -e "  ${CYAN}3.${NC} Follow the setup wizard to configure rclone and start syncing!"
    echo ""
    
    # CachyOS-specific tips
    if [[ "$CACHYOS_DETECTED" == true ]]; then
        echo -e "${MAGENTA}╔════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${MAGENTA}║          CachyOS-Specific Tips & Optimizations 🚀          ║${NC}"
        echo -e "${MAGENTA}╚════════════════════════════════════════════════════════════╝${NC}"
        echo ""
        echo -e "${CYAN}✓${NC} ProtonDrive Sync is optimized for your CachyOS system"
        echo -e "${CYAN}✓${NC} Performance-optimized pacman settings detected"
        echo -e "${CYAN}✓${NC} Sync operations will benefit from CachyOS optimizations"
        echo ""
        echo -e "${WHITE}Recommended for CachyOS users:${NC}"
        echo -e "  ${CYAN}•${NC} Use an AUR helper (yay/paru) for easier package management"
        echo -e "  ${CYAN}•${NC} Enable bandwidth limiting if on metered connection"
        echo -e "  ${CYAN}•${NC} Consider selective sync for faster initial setup"
        echo ""
    fi
    
    echo -e "${CYAN}📖 Documentation:${NC}"
    if [ -f "$INSTALL_DIR/QUICK_START.md" ]; then
        echo -e "  ${WHITE}Quick Start:${NC} $INSTALL_DIR/QUICK_START.md"
    fi
    if [ -f "$INSTALL_DIR/INSTALLATION_GUIDE.md" ]; then
        echo -e "  ${WHITE}Installation Guide:${NC} $INSTALL_DIR/INSTALLATION_GUIDE.md"
    fi
    if [ -f "$INSTALL_DIR/PROTONDRIVE_SETUP.md" ]; then
        echo -e "  ${WHITE}ProtonDrive Setup:${NC} $INSTALL_DIR/PROTONDRIVE_SETUP.md"
    fi
    echo ""
    
    # Check if rclone is configured
    if ! rclone listremotes 2>/dev/null | grep -q "protondrive"; then
        print_warning "rclone doesn't seem to be configured yet"
        echo -e "${CYAN}You'll need to set up rclone with your ProtonDrive account.${NC}"
        echo -e "${CYAN}The app will guide you through this on first run!${NC}"
        echo ""
        
        if ask_yes_no "Would you like to configure rclone now?" "y"; then
            echo ""
            print_info "Starting rclone configuration..."
            echo -e "${YELLOW}When prompted:${NC}"
            echo -e "  1. Choose 'n' for new remote"
            echo -e "  2. Name it '${WHITE}protondrive${NC}'"
            echo -e "  3. Select 'Proton Drive' from the list"
            echo -e "  4. Follow the authentication steps"
            echo ""
            read -p "Press Enter to continue..." < /dev/tty
            rclone config
        fi
    fi
    
    echo ""
    if ask_yes_no "Would you like to launch ProtonDrive Sync now?" "y"; then
        print_info "Launching ProtonDrive Sync..."
        "$INSTALL_DIR/protondrive-sync" &
        sleep 2
        print_success "Application launched! Check your application window."
    fi
    
    echo ""
    print_info "To uninstall later, run: ${WHITE}bash $INSTALL_DIR/uninstall.sh${NC}"
    echo ""
    echo -e "${CYAN}Thank you for using ProtonDrive Sync! ${ROCKET}${NC}"
    echo ""
    
    # Cleanup sudo refresh process
    if [[ -n "${SUDO_REFRESH_PID:-}" ]]; then
        kill "$SUDO_REFRESH_PID" 2>/dev/null || true
    fi
}

# Run main installation
main
