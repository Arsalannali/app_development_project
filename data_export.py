#!/usr/bin/env python3
"""
Data Export Utility for Bareera HR Module

This script exports all JSON data files and uploaded documents to a timestamped backup folder.
Can optionally create a compressed ZIP archive for easy transfer.

Usage:
    python data_export.py                    # Export to backup folder
    python data_export.py --zip              # Export and create ZIP archive
    python data_export.py --output /path     # Specify custom output location
"""

import os
import json
import shutil
from datetime import datetime
import argparse
import sys

# Configuration
DATA_DIR = 'data'
BACKUP_BASE_DIR = 'backups'

# Files to backup
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

def create_backup_folder(base_dir=None):
    """Create a timestamped backup folder"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f'hr_data_backup_{timestamp}'
    
    if base_dir:
        backup_path = os.path.join(base_dir, backup_name)
    else:
        backup_path = os.path.join(BACKUP_BASE_DIR, backup_name)
    
    os.makedirs(backup_path, exist_ok=True)
    return backup_path

def export_json_files(source_dir, dest_dir):
    """Copy all JSON files from source to destination"""
    exported_files = []
    failed_files = []
    
    print("\n📄 Exporting JSON files...")
    for json_file in JSON_FILES:
        source_path = os.path.join(source_dir, json_file)
        dest_path = os.path.join(dest_dir, json_file)
        
        try:
            if os.path.exists(source_path):
                # Validate JSON before copying
                with open(source_path, 'r') as f:
                    data = json.load(f)
                    record_count = len(data) if isinstance(data, list) else 1
                
                # Copy file
                shutil.copy2(source_path, dest_path)
                exported_files.append({
                    'file': json_file,
                    'records': record_count,
                    'size': os.path.getsize(source_path)
                })
                print(f"  ✅ {json_file} ({record_count} records)")
            else:
                print(f"  ⚠️  {json_file} (not found, skipping)")
        except Exception as e:
            print(f"  ❌ {json_file} (error: {str(e)})")
            failed_files.append({'file': json_file, 'error': str(e)})
    
    return exported_files, failed_files

def export_uploaded_files(source_dir, dest_dir):
    """Copy all uploaded files (resumes, documents)"""
    files_source = os.path.join(source_dir, 'files')
    files_dest = os.path.join(dest_dir, 'files')
    
    print("\n📎 Exporting uploaded files...")
    
    if not os.path.exists(files_source):
        print("  ⚠️  No files directory found")
        return 0
    
    try:
        # Create destination files directory
        os.makedirs(files_dest, exist_ok=True)
        
        # Copy all files
        files = os.listdir(files_source)
        if not files:
            print("  ℹ️  No uploaded files found")
            return 0
        
        for file in files:
            source_path = os.path.join(files_source, file)
            dest_path = os.path.join(files_dest, file)
            
            if os.path.isfile(source_path):
                shutil.copy2(source_path, dest_path)
        
        print(f"  ✅ Exported {len(files)} file(s)")
        return len(files)
    
    except Exception as e:
        print(f"  ❌ Error exporting files: {str(e)}")
        return 0

def create_manifest(backup_path, exported_files, uploaded_file_count, failed_files):
    """Create a manifest file with backup metadata"""
    manifest = {
        'backup_info': {
            'timestamp': datetime.now().isoformat(),
            'backup_type': 'Full Export',
            'source_directory': DATA_DIR,
            'hr_module_version': '2.0'
        },
        'exported_data': {
            'json_files': exported_files,
            'total_files': len(exported_files),
            'uploaded_files_count': uploaded_file_count
        },
        'status': {
            'successful': len(failed_files) == 0,
            'failed_files': failed_files if failed_files else None
        }
    }
    
    manifest_path = os.path.join(backup_path, 'BACKUP_MANIFEST.json')
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"\n📋 Manifest created: BACKUP_MANIFEST.json")
    return manifest

def create_zip_archive(backup_path):
    """Create a ZIP archive of the backup folder"""
    print("\n📦 Creating ZIP archive...")
    
    try:
        archive_name = f"{backup_path}.zip"
        shutil.make_archive(backup_path, 'zip', backup_path)
        archive_size = os.path.getsize(archive_name)
        
        # Convert size to human-readable format
        size_mb = archive_size / (1024 * 1024)
        print(f"  ✅ Archive created: {os.path.basename(archive_name)} ({size_mb:.2f} MB)")
        
        return archive_name
    except Exception as e:
        print(f"  ❌ Error creating archive: {str(e)}")
        return None

def print_summary(backup_path, manifest, archive_path=None):
    """Print backup summary"""
    print("\n" + "="*60)
    print("BACKUP SUMMARY")
    print("="*60)
    print(f"Backup Location: {backup_path}")
    print(f"Timestamp: {manifest['backup_info']['timestamp']}")
    print(f"Total JSON Files: {manifest['exported_data']['total_files']}")
    print(f"Uploaded Files: {manifest['exported_data']['uploaded_files_count']}")
    
    # Calculate total records
    total_records = sum(f['records'] for f in manifest['exported_data']['json_files'])
    print(f"Total Records: {total_records}")
    
    if archive_path:
        print(f"ZIP Archive: {archive_path}")
    
    if manifest['status']['failed_files']:
        print(f"\n⚠️  {len(manifest['status']['failed_files'])} file(s) failed to export")
    else:
        print("\n✅ All files exported successfully!")
    
    print("="*60)

def main():
    """Main export function"""
    parser = argparse.ArgumentParser(
        description='Export HR Module data to a backup folder'
    )
    parser.add_argument(
        '--zip', 
        action='store_true',
        help='Create a ZIP archive of the backup'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Custom output directory for backups (default: ./backups/)'
    )
    parser.add_argument(
        '--data-dir',
        type=str,
        default=DATA_DIR,
        help='Source data directory (default: ./data/)'
    )
    
    args = parser.parse_args()
    
    # Check if data directory exists
    if not os.path.exists(args.data_dir):
        print(f"❌ Error: Data directory '{args.data_dir}' not found!")
        print("Make sure you're running this script from the project root directory.")
        sys.exit(1)
    
    print("="*60)
    print("BAREERA HR MODULE - DATA EXPORT UTILITY")
    print("="*60)
    print(f"Source: {args.data_dir}")
    
    # Create backup folder
    try:
        backup_path = create_backup_folder(args.output)
        print(f"Destination: {backup_path}")
    except Exception as e:
        print(f"\n❌ Error creating backup folder: {str(e)}")
        sys.exit(1)
    
    # Export JSON files
    exported_files, failed_files = export_json_files(args.data_dir, backup_path)
    
    # Export uploaded files
    uploaded_file_count = export_uploaded_files(args.data_dir, backup_path)
    
    # Create manifest
    manifest = create_manifest(backup_path, exported_files, uploaded_file_count, failed_files)
    
    # Create ZIP archive if requested
    archive_path = None
    if args.zip:
        archive_path = create_zip_archive(backup_path)
    
    # Print summary
    print_summary(backup_path, manifest, archive_path)
    
    print("\n✨ Export completed!")
    
    if not args.zip:
        print("\n💡 Tip: Use --zip flag to create a compressed archive for easy transfer")
    
    return 0 if not failed_files else 1

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Export cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)

