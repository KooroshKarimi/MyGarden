#!/bin/bash
# scripts/fix_nas_perms.sh
# Fixes permission issues for the .env file on Synology NAS

TARGET_DIR="/volume1/docker/MyGarden"
ENV_FILE="$TARGET_DIR/.env"

echo "Starting permission fix for $TARGET_DIR"

if [ ! -d "$TARGET_DIR" ]; then
    echo "Target directory $TARGET_DIR does not exist. Creating it..."
    mkdir -p "$TARGET_DIR"
fi

if [ -f "$ENV_FILE" ]; then
    echo "Updating permissions for $ENV_FILE"
    # Set read/write for owner and group, read for others. 
    # This helps if the deploy user is in the same group but not the owner.
    chmod 664 "$ENV_FILE"
    
    # Log current permissions
    ls -l "$ENV_FILE"
else
    echo "Warning: $ENV_FILE does not exist yet."
fi

# Ensure directory is writable by group so new files can be created/updated
chmod 775 "$TARGET_DIR"

echo "Permissions fixed."
