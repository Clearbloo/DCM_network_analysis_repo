#!/bin/bash
# run_script.sh

# Initialize save_flag variable
save_flag=""

# Loop through command-line arguments
while [[ $# -gt 0 ]]
do
    case $1 in
        -s|--save)
        save_flag="--save"
        shift # Remove the argument from processing
        ;;
        *) # No more options, break the loop
        break
        ;;
    esac
done

# Run Python script with parameters
if [[ -n $save_flag ]]; then
    python src/quick_graph.py "$@" $save_flag
else
    python src/quick_graph.py "$@"
fi
