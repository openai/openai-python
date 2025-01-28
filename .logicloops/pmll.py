#!/bin/bash
#
# pmll.sh
#
# Shell script wrapper for pmll.py to manage persistent key-value memory.

# Path to pmll.py
PMLL_PY="pmll.py"

# Function to display usage
usage() {
    echo "Usage:"
    echo "  $0 add <key> <value>       # Add or update a key-value pair"
    echo "  $0 get <key>               # Retrieve a value by key"
    echo "  $0 remove <key>            # Remove a key-value pair"
    echo "  $0 list                    # List all keys"
    echo "  $0 clear                   # Clear all memory"
    echo "  $0 display                 # Display all memory (debugging)"
    exit 1
}

# Check if pmll.py exists
if [ ! -f "$PMLL_PY" ]; then
    echo "[pmll.sh] Error: '$PMLL_PY' not found in the current directory."
    exit 1
fi

# Check for at least one argument
if [ $# -lt 1 ]; then
    echo "[pmll.sh] Error: No command provided."
    usage
fi

# Parse command
COMMAND="$1"
shift

case "$COMMAND" in
    add)
        if [ $# -ne 2 ]; then
            echo "[pmll.sh] Error: 'add' requires <key> and <value>."
            usage
        fi
        KEY="$1"
        VALUE="$2"
        python3 "$PMLL_PY" add "$KEY" "$VALUE"
        ;;
    get)
        if [ $# -ne 1 ]; then
            echo "[pmll.sh] Error: 'get' requires <key>."
            usage
        fi
        KEY="$1"
        python3 "$PMLL_PY" get "$KEY"
        ;;
    remove)
        if [ $# -ne 1 ]; then
            echo "[pmll.sh] Error: 'remove' requires <key>."
            usage
        fi
        KEY="$1"
        python3 "$PMLL_PY" remove "$KEY"
        ;;
    list)
        if [ $# -ne 0 ]; then
            echo "[pmll.sh] Error: 'list' does not take any arguments."
            usage
        fi
        python3 "$PMLL_PY" list
        ;;
    clear)
        if [ $# -ne 0 ]; then
            echo "[pmll.sh] Error: 'clear' does not take any arguments."
            usage
        fi
        python3 "$PMLL_PY" clear
        ;;
    display)
        if [ $# -ne 0 ]; then
            echo "[pmll.sh] Error: 'display' does not take any arguments."
            usage
        fi
        python3 "$PMLL_PY" display
        ;;
    *)
        echo "[pmll.sh] Error: Unknown command '$COMMAND'."
        usage
        ;;
esac
