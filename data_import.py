#!/usr/bin/env python3
"""
Data Import Utility for Bareera HR Module

This script imports/restores JSON data files and uploaded documents from a backup folder.
Can restore from either a backup folder or a ZIP archive.

Usage:
    python data_import.py /path/to/backup_folder          # Restore from folder
    python data_import.py /path/to/backup.zip             # Restore from ZIP
    python data_import.py --list                          # List available backups
    python data_import.py --latest                        # Restore latest backup
"""

import os
import json
import shutil
from datetime import datetime
import argparse
import sys
import zipfile
import tempfile

# Configuration
DATA_DIR = 'data'
BACKUP_BASE_DIR = 'backups'

# Files to import
JSON_FILES = [
    'employees.json',
    'departments.json',
    'users.json',
    'attendance.json',
    'leaves.json',
    'payrolls.json',
    'jobs.json',
    'applicants.json'
]

def list_available_backups(backup_dir=BACKUP_BASE_DIR):
    """List all available backup folders"""
    if not os.path.exists(backup_dir):
        print(f"No backups directory found at: {backup_dir}")
        return []
    
    backups = []
    for item in os.listdir(backup_dir):
        item_path = os.path.join(backup_dir, item)
        
        # Check if it's a backup folder
        if os.path.isdir(item_path) and item.startswith('hr_data_backup_'):
            manifest_path = os.path.join(item_path, 'BACKUP_MANIFEST.json')
            if os.path.exists(manifest_path):
                with open(manifest_path, 'r') as f:
                    manifest = json.load(f)
                backups.append({
                    'path': item_path,
                    'name': item,
                    'timestamp': manifest['backup_info']['timestamp'],
                    'files': manifest['exported_data']['total_files'],
                    'records': sum(f['records'] for f in manifest['exported_data']['json_files'])
                })
        
        # Check if it's a ZIP archive
        elif item.endswith('.zip') and 'hr_data_backup_' in item:
            backups.append({
                'path': item_path,
                'name': item,
                'timestamp': 'Unknown',
                'files': '?',
                'records': '?',
                'is_archive': True
            })
    
    return sorted(backups, key=lambda x: x['timestamp'], reverse=True)

def print_available_backups(backups):
    """Print formatted list of available backups"""
    if not backups:
        print("No backups found.")
        return
    
    print("\n" + "="*80)
    print("AVAILABLE BACKUPS")
    print("="*80)
    print(f"{'#':<4} {'Backup Name':<35} {'Timestamp':<20} {'Files':<8} {'Records':<8}")
    print("-"*80)
    
    for i, backup in enumerate(backups, 1):
        is_archive = backup.get('is_archive', False)
        archive_mark = " (ZIP)" if is_archive else ""
        print(f"{i:<4} {backup['name'][:35]:<35}{archive_mark} {backup['timestamp'][:19]:<20} "
              f"{str(backup['files']):<8} {str(backup['records']):<8}")
    
    print("="*80)

def extract_zip_backup(zip_path):
    """Extract ZIP archive to temporary directory"""
    print(f"\n📦 Extracting ZIP archive...")
    
    try:
        temp_dir = tempfile.mkdtemp(prefix='hr_restore_')
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # Find the backup folder inside temp directory
        extracted_items = os.listdir(temp_dir)
        if len(extracted_items) == 1:
            backup_folder = os.path.join(temp_dir, extracted_items[0])
            if os.path.isdir(backup_folder):
                print(f"  ✅ Extracted to temporary location")
                return backup_folder
        
        return temp_dir
    
    except Exception as e:
        print(f"  ❌ Error extracting ZIP: {str(e)}")
        return None

def validate_backup(backup_path):
    """Validate backup folder structure and manifest"""
    print("\n🔍 Validating backup...")
    
    # Check if manifest exists
    manifest_path = os.path.join(backup_path, 'BACKUP_MANIFEST.json')
    if not os.path.exists(manifest_path):
        print("  ⚠️  Warning: No manifest file found. Proceeding with caution...")
        return None
    
    # Read and validate manifest
    try:
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        
        print(f"  ✅ Backup validated")
        print(f"     Timestamp: {manifest['backup_info']['timestamp']}")
        print(f"     Files: {manifest['exported_data']['total_files']}")
        print(f"     Version: {manifest['backup_info'].get('hr_module_version', 'Unknown')}")
        
        return manifest
    
    except Exception as e:
        print(f"  ⚠️  Error reading manifest: {str(e)}")
        return None

def create_backup_of_current_data(data_dir):
    """Create a safety backup of current data before restoring"""
    print("\n💾 Creating safety backup of current data...")
    
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safety_backup = f'data_before_restore_{timestamp}'
        backup_path = os.path.join('backups', safety_backup)
        
        os.makedirs(backup_path, exist_ok=True)
        
        # Copy current data
        if os.path.exists(data_dir):
            for item in os.listdir(data_dir):
                source = os.path.join(data_dir, item)
                dest = os.path.join(backup_path, item)
                
                if os.path.isfile(source):
                    shutil.copy2(source, dest)
                elif os.path.isdir(source):
                    shutil.copytree(source, dest)
        
        print(f"  ✅ Safety backup created: {backup_path}")
        return backup_path
    
    except Exception as e:
        print(f"  ⚠️  Warning: Could not create safety backup: {str(e)}")
        return None

def import_json_files(source_dir, dest_dir, dry_run=False):
    """Import JSON files from backup to data directory"""
    imported_files = []
    failed_files = []
    
    print(f"\n📄 {'[DRY RUN] ' if dry_run else ''}Importing JSON files...")
    
    for json_file in JSON_FILES:
        source_path = os.path.join(source_dir, json_file)
        dest_path = os.path.join(dest_dir, json_file)
        
        try:
            if os.path.exists(source_path):
                # Validate JSON
                with open(source_path, 'r') as f:
                    data = json.load(f)
                    record_count = len(data) if isinstance(data, list) else 1
                
                # Copy file (unless dry run)
                if not dry_run:
                    shutil.copy2(source_path, dest_path)
                
                imported_files.append({
                    'file': json_file,
                    'records': record_count
                })
                print(f"  ✅ {json_file} ({record_count} records)")
            else:
                print(f"  ⚠️  {json_file} (not found in backup, skipping)")
        
        except Exception as e:
            print(f"  ❌ {json_file} (error: {str(e)})")
            failed_files.append({'file': json_file, 'error': str(e)})
    
    return imported_files, failed_files

def import_uploaded_files(source_dir, dest_dir, dry_run=False):
    """Import uploaded files from backup"""
    files_source = os.path.join(source_dir, 'files')
    files_dest = os.path.join(dest_dir, 'files')
    
    print(f"\n📎 {'[DRY RUN] ' if dry_run else ''}Importing uploaded files...")
    
    if not os.path.exists(files_source):
        print("  ℹ️  No files directory in backup")
        return 0
    
    try:
        # Create destination directory
        if not dry_run:
            os.makedirs(files_dest, exist_ok=True)
        
        # Copy files
        files = [f for f in os.listdir(files_source) if os.path.isfile(os.path.join(files_source, f))]
        
        if not files:
            print("  ℹ️  No uploaded files in backup")
            return 0
        
        if not dry_run:
            for file in files:
                source_path = os.path.join(files_source, file)
                dest_path = os.path.join(files_dest, file)
                shutil.copy2(source_path, dest_path)
        
        print(f"  ✅ {'Would import' if dry_run else 'Imported'} {len(files)} file(s)")
        return len(files)
    
    except Exception as e:
        print(f"  ❌ Error importing files: {str(e)}")
        return 0

def print_import_summary(imported_files, uploaded_file_count, failed_files, dry_run=False):
    """Print import summary"""
    print("\n" + "="*60)
    print(f"{'DRY RUN - ' if dry_run else ''}IMPORT SUMMARY")
    print("="*60)
    print(f"JSON Files Imported: {len(imported_files)}")
    print(f"Uploaded Files: {uploaded_file_count}")
    
    total_records = sum(f['records'] for f in imported_files)
    print(f"Total Records: {total_records}")
    
    if failed_files:
        print(f"\n⚠️  {len(failed_files)} file(s) failed to import:")
        for f in failed_files:
            print(f"   - {f['file']}: {f['error']}")
    else:
        print("\n✅ All files imported successfully!")
    
    print("="*60)

def main():
    """Main import function"""
    parser = argparse.ArgumentParser(
        description='Import/Restore HR Module data from a backup'
    )
    parser.add_argument(
        'backup_path',
        nargs='?',
        help='Path to backup folder or ZIP file'
    )
    parser.add_argument(
        '--list',
        action='store_true',
        help='List all available backups'
    )
    parser.add_argument(
        '--latest',
        action='store_true',
        help='Restore from the latest backup'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be imported without actually importing'
    )
    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Skip creating safety backup of current data'
    )
    parser.add_argument(
        '--data-dir',
        type=str,
        default=DATA_DIR,
        help='Destination data directory (default: ./data/)'
    )
    
    args = parser.parse_args()
    
    print("="*60)
    print("BAREERA HR MODULE - DATA IMPORT UTILITY")
    print("="*60)
    
    # List backups if requested
    if args.list:
        backups = list_available_backups()
        print_available_backups(backups)
        return 0
    
    # Determine backup path
    backup_path = None
    is_zip = False
    temp_dir = None
    
    if args.latest:
        # Get latest backup
        backups = list_available_backups()
        if not backups:
            print("❌ No backups found!")
            return 1
        backup_path = backups[0]['path']
        is_zip = backup_path.endswith('.zip')
        print(f"Using latest backup: {backups[0]['name']}")
    
    elif args.backup_path:
        backup_path = args.backup_path
        is_zip = backup_path.endswith('.zip')
    
    else:
        print("❌ Error: Please specify a backup path, use --latest, or --list")
        parser.print_help()
        return 1
    
    # Check if backup exists
    if not os.path.exists(backup_path):
        print(f"❌ Error: Backup not found: {backup_path}")
        return 1
    
    # Extract ZIP if necessary
    if is_zip:
        backup_path = extract_zip_backup(backup_path)
        if not backup_path:
            return 1
        temp_dir = backup_path
    
    # Validate backup
    manifest = validate_backup(backup_path)
    
    # Confirm action (unless dry run)
    if not args.dry_run:
        print(f"\n⚠️  WARNING: This will replace all data in '{args.data_dir}/'")
        response = input("Do you want to continue? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("❌ Import cancelled by user")
            if temp_dir:
                shutil.rmtree(temp_dir, ignore_errors=True)
            return 0
        
        # Create safety backup
        if not args.no_backup:
            create_backup_of_current_data(args.data_dir)
    
    # Ensure data directory exists
    os.makedirs(args.data_dir, exist_ok=True)
    
    # Import JSON files
    imported_files, failed_files = import_json_files(backup_path, args.data_dir, args.dry_run)
    
    # Import uploaded files
    uploaded_file_count = import_uploaded_files(backup_path, args.data_dir, args.dry_run)
    
    # Print summary
    print_import_summary(imported_files, uploaded_file_count, failed_files, args.dry_run)
    
    # Cleanup temp directory if used
    if temp_dir:
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    if args.dry_run:
        print("\n💡 This was a dry run. Use without --dry-run to actually import data.")
    else:
        print("\n✨ Import completed!")
    
    return 0 if not failed_files else 1

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Import cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)

