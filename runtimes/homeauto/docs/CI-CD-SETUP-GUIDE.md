---
title: "CI/CD Setup Guide for uHomeNest"
status: draft
last_updated: 2026-04-22T23:26:13+10:00
category: guide
tags: [guide, ucode3]
description: "This guide provides step-by-step instructions for setting up the CI/CD pipeline for uHomeNest."
---
# CI/CD Setup Guide for uHomeNest

This guide provides step-by-step instructions for setting up the CI/CD pipeline for uHomeNest.

## Prerequisites

- GitHub repository admin access
- PyPI account for package publishing
- Codecov account for coverage reporting

## Required Secrets

The CI/CD workflows require the following GitHub secrets to be configured:

### 1. PyPI API Token (for package publishing)

**Secret Name**: `PYPI_API_TOKEN`
**Purpose**: Authenticates with PyPI for package publishing
**How to obtain**:
1. Go to [PyPI](https://pypi.org/)
2. Log in to your account
3. Navigate to "Account Settings" > "API tokens"
4. Create a new API token with "Entire account" scope
5. Copy the token value

### 2. Codecov Token (for coverage reporting)

**Secret Name**: `CODECOV_TOKEN`
**Purpose**: Authenticates with Codecov for coverage reporting
**How to obtain**:
1. Go to [Codecov](https://codecov.io/)
2. Sign up/log in with your GitHub account
3. Add the uHomeNest repository to your Codecov account
4. Copy the repository upload token

## Setup Instructions

### Step 1: Access GitHub Repository Secrets

1. Go to your uHomeNest repository on GitHub
2. Click on "Settings" tab
3. Select "Secrets and variables" > "Actions"
4. Click "New repository secret"

### Step 2: Add PyPI API Token

1. **Name**: `PYPI_API_TOKEN`
2. **Value**: Paste your PyPI API token
3. Click "Add secret"

### Step 3: Add Codecov Token

1. **Name**: `CODECOV_TOKEN`
2. **Value**: Paste your Codecov repository token
3. Click "Add secret"

### Step 4: Verify Secrets

After adding the secrets, you should see:
- `PYPI_API_TOKEN` in the secrets list
- `CODECOV_TOKEN` in the secrets list

## Testing the CI/CD Pipeline

### Manual Trigger

You can manually trigger the workflow to test:

1. Go to "Actions" tab in your repository
2. Select "Python CI" workflow
3. Click "Run workflow" > "Run workflow"

### Automatic Trigger

The workflow will automatically run on:
- Pushes to `main` branch
- Pull requests targeting `main` branch
- Tag pushes (for releases)

## Troubleshooting

### Common Issues

1. **Workflow permissions**: Ensure GitHub Actions has read/write permissions
   - Go to "Settings" > "Actions" > "General"
   - Set "Workflow permissions" to "Read and write permissions"

2. **Secret not found**: Double-check the secret names are exactly as specified

3. **PyPI upload failures**: Verify your PyPI token has the correct permissions

### Debugging

- Check workflow logs in the "Actions" tab
- Look for specific error messages
- Verify all required files are present in the repository

## Workflow Files

### `python-ci.yml`

Located in `.github/workflows/python-ci.yml`
- Runs tests across Python 3.9, 3.10, 3.11
- Performs linting with flake8, black, isort
- Uploads coverage reports to Codecov

### `release.yml`

Located in `.github/workflows/release.yml`
- Triggers on version tags (e.g., `v1.0.0`)
- Builds and publishes package to PyPI
- Creates GitHub release

## Branch Protection

For enhanced CI/CD reliability, consider setting up branch protection:

1. Go to "Settings" > "Branches"
2. Click "Add branch protection rule"
3. Branch name pattern: `main`
4. Check:
   - "Require a pull request before merging"
   - "Require status checks to pass before merging"
   - "Require conversations to be resolved before merging"
   - "Require signed commits"
5. Select required status checks:
   - "Python CI" (test job)
   - "Python CI" (lint job)

## Next Steps

After setting up the secrets:
1. ✅ Test the CI workflow manually
2. ✅ Create a test pull request to verify PR triggers
3. ✅ Monitor workflow execution and logs
4. ✅ Address any issues that arise

Once the CI/CD pipeline is working correctly, you can proceed with:
- Media foundation implementation
- Documentation updates
- Regular development workflow

## Support

If you encounter issues with the CI/CD setup:
- Check the workflow logs for specific error messages
- Verify all secrets are correctly configured
- Ensure all required files are present in the repository
- Consult the GitHub Actions documentation