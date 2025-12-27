# -*- coding: utf-8 -*-
"""
Backup Script for EEBot Progressive Refactoring.

This script creates a backup of critical files before each phase of refactoring.
It creates timestamped backup directories and maintains a backup manifest.

Usage:
    python scripts/backup_before_refactor.py [--phase PHASE] [--restore BACKUP_DIR]

Examples:
    # Create backup before Phase 1
    python scripts/backup_before_refactor.py --phase 1

    # Restore from a specific backup
    python scripts/backup_before_refactor.py --restore backups/phase1_20251227_120000
"""

import os
import sys
import shutil
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


# Files and directories to backup
CRITICAL_FILES = [
    'menu.py',
    'main.py',
    'src/exceptions.py',
    'src/constants.py',
    'src/__init__.py',
]

CRITICAL_DIRECTORIES = [
    'src/core',
    'src/pages',
    'src/scenarios',
    'src/services',
    'src/utils',
    'src/api',
]

# Exclude patterns (relative to source directory)
EXCLUDE_PATTERNS = [
    '__pycache__',
    '*.pyc',
    '*.pyo',
    '.git',
    '.env',
    'venv',
    'env',
    '.venv',
]


def should_exclude(path: Path) -> bool:
    """Check if a path should be excluded from backup."""
    path_str = str(path)
    for pattern in EXCLUDE_PATTERNS:
        if pattern.startswith('*'):
            if path_str.endswith(pattern[1:]):
                return True
        elif pattern in path_str:
            return True
    return False


def get_backup_dir(phase: int) -> Path:
    """Generate a timestamped backup directory name."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f"phase{phase}_{timestamp}"
    return PROJECT_ROOT / 'backups' / backup_name


def copy_file(src: Path, dst: Path) -> bool:
    """Copy a single file with error handling."""
    try:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        return True
    except Exception as e:
        print(f"  ERROR: Failed to copy {src}: {e}")
        return False


def copy_directory(src: Path, dst: Path) -> int:
    """
    Copy a directory recursively, respecting exclude patterns.

    Returns:
        Number of files copied.
    """
    copied = 0
    try:
        for item in src.rglob('*'):
            if item.is_file() and not should_exclude(item):
                relative_path = item.relative_to(src)
                dst_path = dst / relative_path
                if copy_file(item, dst_path):
                    copied += 1
    except Exception as e:
        print(f"  ERROR: Failed to copy directory {src}: {e}")
    return copied


def create_manifest(backup_dir: Path, phase: int, files_backed_up: List[str]) -> Dict:
    """Create a backup manifest with metadata."""
    manifest = {
        'phase': phase,
        'timestamp': datetime.now().isoformat(),
        'project_root': str(PROJECT_ROOT),
        'backup_dir': str(backup_dir),
        'files_backed_up': files_backed_up,
        'total_files': len(files_backed_up),
        'python_version': sys.version,
    }

    manifest_path = backup_dir / 'manifest.json'
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    return manifest


def backup_phase(phase: int) -> Optional[Path]:
    """
    Create a backup for a specific refactoring phase.

    Args:
        phase: The phase number (0, 1, 2, or 3).

    Returns:
        Path to the backup directory if successful, None otherwise.
    """
    print(f"\n{'='*60}")
    print(f"  EEBot Backup - Phase {phase}")
    print(f"{'='*60}\n")

    backup_dir = get_backup_dir(phase)
    backup_dir.mkdir(parents=True, exist_ok=True)

    files_backed_up = []
    total_copied = 0

    # Backup critical files
    print("Backing up critical files...")
    for file_path in CRITICAL_FILES:
        src = PROJECT_ROOT / file_path
        if src.exists():
            dst = backup_dir / file_path
            if copy_file(src, dst):
                files_backed_up.append(file_path)
                total_copied += 1
                print(f"  ✓ {file_path}")
        else:
            print(f"  ⚠ {file_path} (not found, skipped)")

    # Backup critical directories
    print("\nBacking up critical directories...")
    for dir_path in CRITICAL_DIRECTORIES:
        src = PROJECT_ROOT / dir_path
        if src.exists():
            dst = backup_dir / dir_path
            copied = copy_directory(src, dst)
            if copied > 0:
                files_backed_up.extend([
                    str(p.relative_to(backup_dir))
                    for p in (backup_dir / dir_path).rglob('*')
                    if p.is_file()
                ])
                total_copied += copied
                print(f"  ✓ {dir_path}/ ({copied} files)")
        else:
            print(f"  ⚠ {dir_path}/ (not found, skipped)")

    # Create manifest
    print("\nCreating backup manifest...")
    manifest = create_manifest(backup_dir, phase, files_backed_up)
    print(f"  ✓ manifest.json ({manifest['total_files']} files recorded)")

    # Summary
    print(f"\n{'='*60}")
    print(f"  Backup Complete!")
    print(f"{'='*60}")
    print(f"  Phase: {phase}")
    print(f"  Location: {backup_dir}")
    print(f"  Total files: {total_copied}")
    print(f"  Timestamp: {manifest['timestamp']}")
    print()

    return backup_dir


def restore_backup(backup_dir: Path) -> bool:
    """
    Restore files from a backup directory.

    Args:
        backup_dir: Path to the backup directory.

    Returns:
        True if restore was successful, False otherwise.
    """
    manifest_path = backup_dir / 'manifest.json'
    if not manifest_path.exists():
        print(f"ERROR: No manifest found in {backup_dir}")
        return False

    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)

    print(f"\n{'='*60}")
    print(f"  EEBot Restore - Phase {manifest['phase']}")
    print(f"{'='*60}")
    print(f"  From: {backup_dir}")
    print(f"  Backup timestamp: {manifest['timestamp']}")
    print(f"  Files to restore: {manifest['total_files']}")
    print()

    # Confirm restore
    confirm = input("Are you sure you want to restore? This will overwrite existing files. [y/N]: ")
    if confirm.lower() != 'y':
        print("Restore cancelled.")
        return False

    restored = 0
    failed = 0

    print("\nRestoring files...")
    for file_path in manifest['files_backed_up']:
        src = backup_dir / file_path
        dst = PROJECT_ROOT / file_path

        if src.exists():
            if copy_file(src, dst):
                restored += 1
                print(f"  ✓ {file_path}")
            else:
                failed += 1
        else:
            print(f"  ⚠ {file_path} (not in backup)")

    print(f"\n{'='*60}")
    print(f"  Restore Complete!")
    print(f"{'='*60}")
    print(f"  Restored: {restored} files")
    print(f"  Failed: {failed} files")
    print()

    return failed == 0


def list_backups() -> List[Path]:
    """List all available backups."""
    backups_dir = PROJECT_ROOT / 'backups'
    if not backups_dir.exists():
        return []

    backups = []
    for item in sorted(backups_dir.iterdir()):
        if item.is_dir() and (item / 'manifest.json').exists():
            backups.append(item)

    return backups


def main():
    parser = argparse.ArgumentParser(
        description='Backup and restore tool for EEBot progressive refactoring.'
    )
    parser.add_argument(
        '--phase', '-p',
        type=int,
        choices=[0, 1, 2, 3],
        help='Create backup for specified phase (0-3)'
    )
    parser.add_argument(
        '--restore', '-r',
        type=str,
        help='Restore from specified backup directory'
    )
    parser.add_argument(
        '--list', '-l',
        action='store_true',
        help='List all available backups'
    )

    args = parser.parse_args()

    if args.list:
        backups = list_backups()
        if not backups:
            print("No backups found.")
        else:
            print("\nAvailable backups:")
            print("-" * 60)
            for backup in backups:
                manifest_path = backup / 'manifest.json'
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    manifest = json.load(f)
                print(f"  Phase {manifest['phase']}: {backup.name}")
                print(f"    Created: {manifest['timestamp']}")
                print(f"    Files: {manifest['total_files']}")
                print()
        return

    if args.restore:
        backup_path = Path(args.restore)
        if not backup_path.is_absolute():
            backup_path = PROJECT_ROOT / backup_path
        if not backup_path.exists():
            print(f"ERROR: Backup directory not found: {backup_path}")
            sys.exit(1)
        success = restore_backup(backup_path)
        sys.exit(0 if success else 1)

    if args.phase is not None:
        backup_dir = backup_phase(args.phase)
        if backup_dir is None:
            sys.exit(1)
        return

    # No arguments - show help
    parser.print_help()


if __name__ == '__main__':
    main()
