#!/bin/bash

file_paths=$(find / -type f -path "*/super_gradients/training/utils/checkpoint_utils.py" 2>/dev/null)

if [[ -z "$file_paths" ]]; then
    echo "No instances of super_gradients checkpoint_utils.py found!"
else
    for FILE_PATH in $file_paths; do
        if [[ ! -f "$FILE_PATH.bak" ]]; then
            cp "$FILE_PATH" "$FILE_PATH.bak"
            echo "Backup created for: $FILE_PATH"
        fi

        sed -i 's|https://sghub.deci.ai/models/|https://sg-hub-nv.s3.amazonaws.com/|g' "$FILE_PATH"
        echo "Done!"

        # Uncomment the break if you want to modify only one instance
        # break
    done
fi
