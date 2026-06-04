# Setup Guide

## GitHub Secrets Configuration

The dashboard requires DataDog API credentials to fetch metrics. These must be configured as GitHub repository secrets.

### Required Secrets

Navigate to your repository settings: `Settings` → `Secrets and variables` → `Actions` → `New repository secret`

Add the following secrets:

1. **DD_ACCESS_TOKEN**
   - Your DataDog Access Token
   - Used for API authentication
   - Format: `dd_access_token_xxxxxxxxxxxxx`

2. **DD_APP_KEY** (if using API Key + App Key authentication)
   - Your DataDog Application Key
   - Format: `xxxxxxxxxxxxx`

### How to Get DataDog Credentials

1. Log into DataDog: https://app.datadoghq.com
2. Navigate to: `Organization Settings` → `API Keys` or `Access Tokens`
3. Create a new token/key with read permissions for metrics
4. Copy the token and add it to GitHub secrets

### Network Access

**Q: Can GitHub Actions runners call DataDog API?**

**A: Yes.** GitHub Actions ephemeral runners have outbound internet access and can call external APIs like DataDog. This is standard practice for CI/CD workflows.

- ✅ Outbound HTTPS requests to DataDog API are allowed
- ✅ No special network configuration needed
- ✅ Secure: Credentials stored as encrypted GitHub secrets
- ✅ Ephemeral: Runners are destroyed after each workflow run

### Workflow Triggers

The dashboard workflow can be triggered in two ways:

1. **Automatic**: On push to `main` branch (only)
2. **Manual**: Via GitHub Actions UI from **ANY branch**
   - Go to `Actions` tab
   - Select `Generate Dashboard` workflow
   - Click `Run workflow`
   - **Select your branch** from dropdown (main, feature branches, etc.)
   - Click `Run workflow` button

**Key Point:** Manual trigger allows testing from feature branches before merging to main.

### Testing

To test the setup:

1. Add secrets to repository
2. Go to `Actions` tab
3. Select `Generate Dashboard` workflow
4. Click `Run workflow` → Select branch → `Run workflow`
5. Monitor the workflow execution
6. Check GitHub Pages for deployed dashboard

### Troubleshooting

**Authentication Errors:**
- Verify DD_ACCESS_TOKEN is correctly set in GitHub secrets
- Check token has not expired
- Ensure token has read permissions for metrics API

**Network Errors:**
- GitHub Actions runners should have internet access by default
- If behind corporate proxy, contact GitHub Enterprise admin
- Check DataDog API status: https://status.datadoghq.com

**Deployment Errors:**
- Ensure GitHub Pages is enabled in repository settings
- Verify workflow has write permissions to deploy
- Check `Settings` → `Actions` → `General` → `Workflow permissions` is set to "Read and write permissions"