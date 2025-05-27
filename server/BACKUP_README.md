# Firebase Database Backup & Restore System

This document describes the Firebase Firestore backup and restore functionality implemented for the World Riichi Tournament application.

## Overview

The backup system provides a complete solution for backing up and restoring the Firebase Firestore database. It uses JSON format for maximum compatibility, simplicity, and human readability.

## Features

- **Complete Database Backup**: Backs up all collections, documents, and subcollections
- **JSON Format**: Human-readable, portable, and easy to inspect
- **Metadata Preservation**: Maintains Firestore-specific data types (timestamps, etc.)
- **Web Interface**: Easy-to-use admin interface for backup/restore operations
- **Safety Measures**: Confirmation dialogs and explicit confirmation requirements
- **File Management**: List, view, and delete backup files

## File Structure

```
/operations/firebase_backup.py    # Core backup/restore functionality
/run/admin.py                     # Admin routes for backup operations
/templates/adminlist.html         # Web interface for backup management
/test_backup.py                   # Test script to verify functionality
/backups/                         # Directory where backup files are stored
```

## How It Works

### Backup Process

1. **Collection Enumeration**: Iterates through all root collections in Firestore
2. **Document Processing**: For each document, extracts all field data
3. **Subcollection Handling**: Recursively processes any subcollections
4. **Data Serialization**: Converts Firestore-specific types to JSON-compatible format
5. **File Creation**: Saves the complete backup as a timestamped JSON file

### Restore Process

1. **File Validation**: Verifies the backup file exists and has valid structure
2. **Data Deserialization**: Converts JSON data back to Firestore format
3. **Collection Recreation**: Recreates all collections and documents
4. **Subcollection Restoration**: Recursively restores subcollections
5. **Verification**: Logs the restoration process for verification

## Usage

### Creating a Backup

1. Navigate to the admin page (`/admin/list`)
2. Ensure you're logged in as SUPERADMIN
3. Click the "🗄️ Create Firebase Backup" button
4. Confirm the operation when prompted
5. Wait for the backup to complete (may take several minutes for large databases)

### Restoring from Backup

1. Navigate to the admin page (`/admin/list`)
2. Find the desired backup file in the "Available Backup Files" table
3. Click the "🔄 Restore" button for the chosen backup
4. **CAREFULLY READ THE WARNING** - this will completely replace the current database
5. Confirm the operation by clicking "Yes, Restore Database"
6. Wait for the restore to complete

### Managing Backup Files

- **View Files**: All backup files are listed with creation date and size
- **Delete Files**: Use the "🗑️ Delete" button to remove unwanted backups
- **File Location**: Backups are stored in the `/backups/` directory

## Backup File Format

Backup files use the following JSON structure:

```json
{
  "backup_info": {
    "created_at": "2024-01-15T10:30:00Z",
    "version": "1.0",
    "description": "Complete Firebase Firestore backup"
  },
  "collections": {
    "tournaments": {
      "tournament_id_1": {
        "name": "Tournament Name",
        "status": "live",
        "_subcollections": {
          "v3": {
            "players": { ... },
            "scores": { ... }
          }
        }
      }
    },
    "metadata": { ... }
  }
}
```

## Data Type Handling

The system properly handles Firestore-specific data types:

- **Timestamps**: Converted to ISO format strings with type markers
- **Dates**: Preserved as ISO format strings
- **Numbers**: Maintained as JSON numbers
- **Strings**: Preserved as-is
- **Booleans**: Maintained as JSON booleans
- **Arrays**: Preserved with recursive type handling
- **Objects**: Recursively processed

## Safety Features

### Confirmation Requirements

- **Backup Creation**: Requires user confirmation due to potential processing time
- **Database Restore**: Requires explicit confirmation due to destructive nature
- **File Deletion**: Requires confirmation to prevent accidental loss

### Error Handling

- Comprehensive error logging for troubleshooting
- Graceful failure handling with user-friendly error messages
- Transaction-like behavior where possible

### Access Control

- All backup operations restricted to SUPERADMIN users only
- Additional authentication checks in place

## Testing

Run the test script to verify functionality:

```bash
python test_backup.py
```

This will test:
- Import functionality
- Data serialization/deserialization
- Directory creation
- JSON structure validation

## Backup Best Practices

### Regular Backups

- Create backups before major operations
- Schedule regular backups (daily/weekly depending on activity)
- Keep multiple backup versions for different time points

### Storage Management

- Monitor backup file sizes
- Delete old backups periodically to save disk space
- Consider external backup storage for critical data

### Testing Restores

- Periodically test restore functionality with non-production data
- Verify backup integrity by examining file contents
- Document restore procedures for emergency situations

## Troubleshooting

### Common Issues

1. **Permission Errors**: Ensure the application has write access to the backup directory
2. **Large Database Timeouts**: For very large databases, consider increasing timeout values
3. **Memory Issues**: Large backups may require sufficient system memory
4. **Firebase Quota**: Be aware of Firestore read/write quotas during operations

### Log Files

Check application logs for detailed error information:
- Backup operations are logged with collection-level progress
- Restore operations include document-level logging
- Error conditions are logged with full stack traces

## Security Considerations

- Backup files contain complete database contents - secure appropriately
- Limit access to backup directory and files
- Consider encryption for sensitive backup data
- Regularly audit backup access and usage

## Future Enhancements

Potential improvements for the backup system:

- **Incremental Backups**: Only backup changed data since last backup
- **Compression**: Compress backup files to save storage space
- **Cloud Storage**: Integration with cloud storage services
- **Scheduled Backups**: Automatic backup scheduling
- **Backup Verification**: Automated integrity checking
- **Selective Restore**: Restore only specific collections or documents

## Support

For issues or questions regarding the backup system:

1. Check the application logs for error details
2. Run the test script to verify basic functionality
3. Review this documentation for usage guidelines
4. Contact the system administrator for assistance 