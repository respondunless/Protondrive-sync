#!/bin/bash

# ProtonDrive Sync - Uninstaller
# Clean removal with options to keep your data

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

# Emojis
CHECK="✓"
CROSS="✗"
ARROW="→"
TRASH="🗑"

KEEP_CONFIG=false
KEEP_DATA=false

#######################
# Helper Functions
#######################

print_header() {
    echo ""
    echo -e "${RED}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║                                                            ║${NC}"
    echo -e "${RED}║${WHITE}           ProtonDrive Sync - Uninstaller ${TRASH}                ${RED}║${NC}"
    echo -e "${RED}║                                                            ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
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
        read -p "$(echo -e ${YELLOW}${prompt}${NC})" response
        response=${response:-$default}
        case "$response" in
            [Yy]* ) return 0;;
            [Nn]* ) return 1;;
            * ) echo -e "${RED}Please answer yes or no.${NC}";;
        esac
    done
}

detect_installation() {
    print_info "Detecting installation..."
    
    # Check system installation
    if [ -d "/opt/protondrive-sync" ]; then
        INSTALL_DIR="/opt/protondrive-sync"
        INSTALL_TYPE="system"
        print_success "Found system installation at $INSTALL_DIR"
        return 0
    fi
    
    # Check user installation
    if [ -d "$HOME/.local/share/protondrive-sync" ]; then
        INSTALL_DIR="$HOME/.local/share/protondrive-sync"
        INSTALL_TYPE="user"
        print_success "Found user installation at $INSTALL_DIR"
        return 0
    fi
    
    print_error "No installation found"
    print_info "Searched locations:"
    echo "  - /opt/protondrive-sync"
    echo "  - $HOME/.local/share/protondrive-sync"
    exit 1
}

remove_application_files() {
    print_info "Removing application files..."
    
    if [ -d "$INSTALL_DIR" ]; then
        if [[ "$INSTALL_TYPE" == "system" ]]; then
            sudo rm -rf "$INSTALL_DIR"
        else
            rm -rf "$INSTALL_DIR"
        fi
        print_success "Application files removed"
    fi
}

remove_desktop_entry() {
    print_info "Removing desktop integration..."
    
    local removed=false
    
    # Remove system desktop entry
    if [ -f "/usr/share/applications/protondrive-sync.desktop" ]; then
        sudo rm -f "/usr/share/applications/protondrive-sync.desktop"
        removed=true
    fi
    
    # Remove user desktop entry
    if [ -f "$HOME/.local/share/applications/protondrive-sync.desktop" ]; then
        rm -f "$HOME/.local/share/applications/protondrive-sync.desktop"
        removed=true
    fi
    
    # Remove autostart entry
    if [ -f "$HOME/.config/autostart/protondrive-sync.desktop" ]; then
        rm -f "$HOME/.config/autostart/protondrive-sync.desktop"
        print_success "Autostart entry removed"
    fi
    
    if $removed; then
        # Update desktop database
        if command -v update-desktop-database &>/dev/null; then
            update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true
            sudo update-desktop-database "/usr/share/applications" 2>/dev/null || true
        fi
        print_success "Desktop entries removed"
    fi
}

remove_bin_symlink() {
    print_info "Removing command symlinks..."
    
    local removed=false
    
    # Remove system symlinks
    if [ -L "/usr/local/bin/protondrive-sync" ]; then
        sudo rm -f "/usr/local/bin/protondrive-sync"
        removed=true
    fi
    
    if [ -L "/usr/local/bin/protondrive-sync-uninstall" ]; then
        sudo rm -f "/usr/local/bin/protondrive-sync-uninstall"
        removed=true
    fi
    
    # Remove user symlinks
    if [ -L "$HOME/.local/bin/protondrive-sync" ]; then
        rm -f "$HOME/.local/bin/protondrive-sync"
        removed=true
    fi
    
    if [ -L "$HOME/.local/bin/protondrive-sync-uninstall" ]; then
        rm -f "$HOME/.local/bin/protondrive-sync-uninstall"
        removed=true
    fi
    
    if $removed; then
        print_success "Command symlinks removed"
    fi
}

remove_config() {
    if ! $KEEP_CONFIG; then
        print_info "Removing configuration..."
        
        if [ -d "$HOME/.config/protondrive-sync" ]; then
            rm -rf "$HOME/.config/protondrive-sync"
            print_success "Configuration removed"
        fi
    else
        print_info "Keeping configuration files (as requested)"
    fi
}

kill_running_instances() {
    print_info "Stopping running instances..."
    
    if pgrep -f "protondrive-sync" > /dev/null; then
        pkill -f "protondrive-sync" 2>/dev/null || true
        sleep 1
        print_success "Stopped running instances"
    else
        print_info "No running instances found"
    fi
}

#######################
# Main Uninstall
#######################

main() {
    clear
    print_header
    
    echo -e "${WHITE}This will remove ProtonDrive Sync from your system.${NC}"
    echo ""
    
    # Detect installation
    detect_installation
    
    echo ""
    echo -e "${WHITE}What would you like to do with your data?${NC}"
    echo ""
    
    # Ask about configuration
    if [ -d "$HOME/.config/protondrive-sync" ]; then
        if ask_yes_no "Keep your configuration files?" "y"; then
            KEEP_CONFIG=true
        fi
    fi
    
    echo ""
    echo -e "${WHITE}Uninstall Summary:${NC}"
    echo -e "  ${CYAN}${ARROW}${NC} Installation type: $INSTALL_TYPE"
    echo -e "  ${CYAN}${ARROW}${NC} Installation directory: $INSTALL_DIR"
    echo -e "  ${CYAN}${ARROW}${NC} Keep configuration: $(if $KEEP_CONFIG; then echo 'Yes'; else echo 'No'; fi)"
    echo ""
    
    print_warning "This will remove the application from your system!"
    if ! ask_yes_no "Are you sure you want to continue?" "n"; then
        print_info "Uninstall cancelled"
        exit 0
    fi
    
    # Start uninstall
    echo ""
    print_info "${TRASH} Starting uninstall..."
    echo ""
    
    kill_running_instances
    remove_desktop_entry
    remove_bin_symlink
    remove_application_files
    remove_config
    
    # Uninstall complete
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                                                            ║${NC}"
    echo -e "${GREEN}║${WHITE}              Uninstall Complete!                          ${GREEN}║${NC}"
    echo -e "${GREEN}║                                                            ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    print_success "ProtonDrive Sync has been removed from your system"
    
    if $KEEP_CONFIG; then
        echo ""
        print_info "Your configuration is preserved at:"
        echo -e "  ${WHITE}$HOME/.config/protondrive-sync${NC}"
        print_info "Delete it manually if you want to remove all traces"
    fi
    
    echo ""
    echo -e "${CYAN}Thank you for trying ProtonDrive Sync!${NC}"
    echo -e "${CYAN}We hope to see you again. ${NC}"
    echo ""
    
    # Optional: Ask for feedback
    echo -e "${WHITE}Before you go...${NC}"
    if ask_yes_no "Would you like to share why you're uninstalling? (opens GitHub issues)" "n"; then
        if command -v xdg-open &>/dev/null; then
            xdg-open "https://github.com/respondunless/Protondrive-sync/issues/new" &
        else
            print_info "Please visit: https://github.com/respondunless/Protondrive-sync/issues/new"
        fi
    fi
    
    echo ""
}

# Run main uninstall
main
