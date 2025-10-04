#!/bin/bash

REPO_PATHS=(
  "/DATA/REPOS/StudyMaterial"
  "/DATA/REPOS/Containers"
  "/DATA/REPOS/Builder"
)

for REPO_PATH in "${REPO_PATHS[@]}"
do
  echo "Processing $REPO_PATH ..."
  if [ -d "$REPO_PATH" ]; then
    cd "$REPO_PATH" || { echo "Failed to access $REPO_PATH"; continue; }
    if [ -d ".git" ]; then
      git pull
      echo "Updated $REPO_PATH"
    else
      echo "$REPO_PATH is not a git repository"
    fi
  else
    echo "Directory $REPO_PATH does not exist"
  fi
done

