#!/bin/bash

# Function to recursively process directories and files
process_directory() {
    local root_dir="$1"
    local current_dir="$2"
    shift 2
    local ignore_list=("$@")

    for file in "$current_dir"/*; do
        # Get the base name of the file or directory
        local base_name=$(basename "$file")

        # Check if the base name is in the ignore list
        if [[ " ${ignore_list[@]} " =~ " ${base_name} " ]]; then
            continue
        fi

        if [ -d "$file" ]; then
            # If it's a directory, recursively process it
            process_directory "$root_dir" "$file" "${ignore_list[@]}"
        elif [ -f "$file" ]; then
            # Print the relative path and file contents
            relative_path="${file#$root_dir/}"
            echo "# $relative_path"
            cat "$file"
            echo ""
        fi
    done
}

# Main script logic
main() {
    local output_file="$1"
    local root_dir="$2"
    shift 2
    local ignore_list=("$@")

    # Start processing from the root directory and redirect output to the specified file
    process_directory "$root_dir" "$root_dir" "${ignore_list[@]}" > "$output_file"
}

# Run the script with the provided arguments
main "$@"
