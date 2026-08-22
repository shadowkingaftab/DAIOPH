# OS Layer Architecture

## Overview

The OS layer gives DAIOPH the ability to interact with the host operating system: launching applications, managing windows, accessing the filesystem, and automating tasks.

## Components

### Desktop (`os_layer/desktop/`)

#### Launcher (`launcher.py`)
- Discovers installed applications per platform
- Launches apps with arguments
- Platform support: Windows, macOS, Linux

#### Window Manager (`window_manager.py`)
- Enumerates open windows
- Focus/activate specific windows
- Query window geometry and titles
- Platform backends: Win32, Cocoa, X11/Wayland

#### Desktop Context (`desktop_context.py`)
- Aggregates current desktop state
- Provides context to intelligence (active app, recent activity)
- Respects privacy settings for what is exposed

### Filesystem (`os_layer/filesystem/`)

#### Filesystem Manager (`filesystem_manager.py`)
- Scoped file operations (read, write, list)
- Enforces permission boundaries
- Path validation and sanitization

#### Path Handler (`path_handler.py`)
- Cross-platform path normalization
- Safe path resolution (prevents traversal)
- User directory mapping (Documents, Downloads, etc.)

### Applications (`os_layer/applications/`)

#### Application Manager (`application_manager.py`)
- Application registry and metadata
- Running app tracking
- App capability queries

### Automation (`os_layer/automation/`)

#### Automation Controller (`automation_controller.py`)
- Task automation via declared workflows
- Keyboard/mouse automation (with explicit user consent)
- Scheduled task execution
- Macro recording and replay

### System (`os_layer/system/`)

#### System Manager (`system_manager.py`)
- OS information queries
- Environment variable access (scoped)
- Process management

#### System Monitor (`system_monitor.py`)
- System resource monitoring
- Process listing with resource usage
- Disk space monitoring

## Security Boundaries

All OS interactions are gated by the permission system:

| Capability | Permission Required |
|------------|---------------------|
| Read files | `fs.read` |
| Write files | `fs.write` |
| Launch apps | `apps.launch` |
| Control windows | `desktop.windows` |
| Automate input | `automation.input` |
| Monitor system | `system.monitor` |

## Design Principles

1. **Explicit consent**: No OS action without granted permission
2. **Scoped access**: Only permitted paths/apps are accessible
3. **Auditable**: All OS actions are logged
4. **Cross-platform**: Consistent API across Windows/macOS/Linux