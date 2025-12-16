# Project Standards & Structure

## Overview
This project follows the same organizational structure as the **FlexibleDietMenu** repository to maintain consistency across projects. This is a deliberate design choice to ensure familiarity and ease of navigation.

## Standard Structure Pattern

```
project-root/
├── README.md                    # Main project documentation
├── LICENSE                      # Project license
├── requirements.txt             # Python dependencies
├── setup.py                     # Package installation configuration
├── .gitignore                   # Git ignore rules
├── PROJECT_STANDARDS.md         # This file
│
├── docs/                        # All documentation
│   ├── setup/                   # Installation and setup guides
│   ├── features/                # Feature documentation
│   └── deployment/              # Deployment guides
│
└── protondrive_sync/            # Main application code
    ├── __init__.py
    ├── core/                    # Core functionality
    ├── utils/                   # Utility modules
    └── config/                  # Configuration files
```

## Key Principles

### 1. **Consistent Naming**
- Main application folder matches the project name (snake_case)
- Documentation organized in `docs/` with logical subdirectories
- Root-level files for project metadata and configuration

### 2. **Documentation Organization**
- **docs/setup/**: Installation, prerequisites, first-run guides
- **docs/features/**: Feature descriptions, usage examples
- **docs/deployment/**: Deployment instructions, systemd services

### 3. **Code Organization**
- All source code in the main application folder (`protondrive_sync/`)
- Modular structure with clear separation of concerns
- Configuration separate from core logic

## Maintenance Guidelines

### For All Future Changes:
1. ✅ **Keep the structure intact** - Don't move files between major directories
2. ✅ **Add new docs to appropriate docs/ subdirectories** - Not in the root
3. ✅ **Update imports** - If you rename/move modules, update all imports
4. ✅ **Follow the pattern** - New features should fit the existing structure
5. ✅ **Document changes** - Update relevant docs when adding features

### When Adding New Features:
- Add code to `protondrive_sync/` subdirectories
- Add documentation to `docs/features/`
- Update README.md with high-level overview
- Keep root directory clean

### When Updating Documentation:
- Use the appropriate `docs/` subdirectory
- Maintain consistent formatting with existing docs
- Cross-reference related documentation

## Rationale

**Why maintain this structure?**
- **Consistency**: Same pattern across multiple projects reduces cognitive load
- **Scalability**: Clear organization supports project growth
- **Professionalism**: Standard structure is familiar to contributors
- **Maintainability**: Easy to find and update specific components

## User Preference Note

This structure is maintained as a **user preference** for consistency across all projects. When working on this codebase, please respect and maintain this organizational pattern.

---

*Last Updated: December 2025*
*Structure Pattern: FlexibleDietMenu-compatible*
