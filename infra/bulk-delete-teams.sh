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
REGEX_PATTERN=$2

list teams in org
teams=$(gh api orgs/$ORG/teams --jq '.[].slug')
echo "Found teams matching the pattern '$REGEX_PATTERN':"
for team in $teams; do
  if [[ $team =~ $REGEX_PATTERN ]]; then
    echo "Found matching team: $team"
    read -p "Do you want to delete the team $team? (y/n): " confirm
    if [ "$confirm" == "y" ]; then
      gh api -X DELETE "orgs/$ORG/teams/$team" --silent
      echo "Team $team has been deleted."
    else
      echo "Team $team was not deleted."
    fi
  fi
done
