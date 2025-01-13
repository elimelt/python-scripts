#!/bin/bash

# Function to convert string to slug format
slugify() {
    echo "$1" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9-]/-/g' | sed 's/--*/-/g' | sed 's/^-//' | sed 's/-$//'
}

# Function to check if repository exists
check_repo_exists() {
    gh repo view "$org_name/$team_slug" &> /dev/null
    return $?
}

# Function to wait for repository with timeout
wait_for_repo() {
    local timeout=30
    local start_time=$(date +%s)

    while ! check_repo_exists; do
        local current_time=$(date +%s)
        local elapsed_time=$((current_time - start_time))

        if [ $elapsed_time -ge $timeout ]; then
            echo "Timeout waiting for repository to be created"
            return 1
        fi

        echo "Waiting for repository to be fully created..."
        sleep 2
    done
    return 0
}

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "GitHub CLI (gh) is not installed. Please install it first."
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo "Please authenticate with GitHub first using 'gh auth login'"
    exit 1
fi

# Get organization name
read -p "Enter your GitHub organization name: " org_name

# Get team name
read -p "Enter team name: " team_name
team_slug=$(slugify "$team_name")

# Get GitHub usernames (comma-separated)
read -p "Enter GitHub usernames (comma-separated): " github_users
IFS=',' read -ra github_array <<< "$github_users"

# Get template repository (optional)
read -p "Enter template repository name (press Enter to skip): " template_repo

# Create team
echo "Creating team: $team_slug"
gh api \
  --method POST \
  --silent \
  -H "Accept: application/vnd.github+json" \
  "/orgs/$org_name/teams" \
  -f name="$team_name" \
  -f permission="push" \
  -f privacy="closed" > /dev/null

# Create repository
echo "Creating repository: $team_slug"
if [ -n "$template_repo" ]; then
    # First create from template
    gh repo create "$org_name/$team_slug" \
        --public \
        --template "$org_name/$template_repo" > /dev/null
else
    # create with main branch
    gh repo create "$org_name/$team_slug" \
        --public > /dev/null

    # create main branch
    git clone "https://github.com/$org_name/$team_slug.git"
    cd "$team_slug"
    git checkout -b main
    touch README.md
    git add .
    git commit -m "Initial commit"
    git push -u origin main
    cd ..
    rm -rf "$team_slug"
fi

# Wait for repository to be fully created
if ! wait_for_repo; then
    echo "Failed to create repository"
    exit 1
fi

# Add team to the repository
echo "Adding team to repository"
gh api \
    --method PUT \
    --silent \
    -H "Accept: application/vnd.github+json" \
    "/orgs/$org_name/teams/$team_slug/repos/$org_name/$team_slug" \
    -f permission="push" > /dev/null

# Add team members
for username in "${github_array[@]}"; do
    username=$(echo "$username" | tr -d ' ')
    echo "Adding $username to team $team_slug"
    gh api \
        --method PUT \
        --silent \
        -H "Accept: application/vnd.github+json" \
        "/orgs/$org_name/teams/$team_slug/memberships/$username" \
        -f role="member" > /dev/null
done

# Wait a bit before setting branch protection
sleep 5

echo "Setting up branch protection rules for main branch"
gh api repos/$org_name/$team_slug/branches/main/protection --method PUT \
  -F "required_pull_request_reviews[dismiss_stale_reviews]=true" \
  -F "required_pull_request_reviews[require_code_owner_reviews]=false" \
  -F "required_pull_request_reviews[required_approving_review_count]=1" \
  -F "allow_force_pushes=true" \
  -F "allow_deletions=true" \
  -F "restrictions=null" \
  -F "required_status_checks=null" \
  -F "enforce_admins=null"

