#!/bin/sh
# ci_post_clone.sh — Xcode Cloud post-clone script
#
# Sets CURRENT_PROJECT_VERSION from Xcode Cloud's auto-incrementing
# CI_BUILD_NUMBER so every build gets a unique, monotonically increasing
# build number across all targets.
#
# Prerequisites:
#   - VERSIONING_SYSTEM = "apple-generic" in project-level build settings
#   - This file at: <repo-root>/ci_scripts/ci_post_clone.sh
#   - Must be executable: chmod +x ci_scripts/ci_post_clone.sh

set -e

echo "=== ci_post_clone.sh ==="

if [ -z "$CI_BUILD_NUMBER" ]; then
    echo "CI_BUILD_NUMBER not set (not running in Xcode Cloud). Skipping."
    exit 0
fi

echo "Setting CURRENT_PROJECT_VERSION to $CI_BUILD_NUMBER for all targets..."

cd "$CI_PRIMARY_REPOSITORY_PATH"
agvtool new-version -all "$CI_BUILD_NUMBER"

echo "=== Build number set to $CI_BUILD_NUMBER ==="
