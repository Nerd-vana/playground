#!/bin/bash

declare -a entered_strings

while true; do
  read -p "Enter a string: " user_input

  if [[ " ${entered_strings[@]} " =~ " ${user_input} " ]]; then
    echo "You have already entered this string: $user_input"
  else
    entered_strings+=("$user_input")
  fi
done
