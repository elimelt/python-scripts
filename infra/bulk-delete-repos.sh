#!/bin/bash

# check org provided
if [ -z "$1" ]; then
  echo "Usage: $0 <org> <regex-pattern>"
  exit 1
fi

# check regex provided
if [ -z "$2" ]; then
  echo "Usage: $0 <org> <regex-pattern>"
  exit 1
fi

ORG=$1
REGEX_PATTERN=$1

repos=$(gh repo list $ORG --json nameWithOwner | jq -r '.[].nameWithOwner')
echo "Found repositories matching the pattern '$REGEX_PATTERN':"
for repo in $repos; do
  if [[ $repo =~ $REGEX_PATTERN ]]; then

    read -p "Do you want to delete $repo? (y/n): " confirm
    if [ "$confirm" == "y" ]; then
      gh repo delete $repo --yes
    fi
  fi
done
