# Fitness Agent - Setup Guide

Complete setup instructions for the Fitness Agent system.

## Prerequisites

- Python 3.9 or higher
- Google Cloud Platform account (for deployment)
- API accounts for:
  - Anthropic (Claude)
  - OpenAI (GPT)
  - Google (Gemini)
  - SendGrid (Email)

## Step 1: Clone and Install

```bash
# Clone the repository
git clone https://github.com/veritas6161/fitness-agent-rr.git
cd fitness-agent-rr/fitness-agent

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Configure Environment Variables

### 2.1 Create .env File

Copy the example file:
```bash
cp .env.example .env
```

### 2.2 Get API Keys

#### Anthropic API Key (Claude)
1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Sign up or log in
3. Navigate to API Keys
4. Create a new API key
5. Copy the key to `.env` as `ANTHROPIC_API_KEY`

#### OpenAI API Key (GPT)
1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Sign up or log in
3. Create a new API key
4. Copy the key to `.env` as `OPENAI_API_KEY`

#### Google Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with Google account
3. Create API key
4. Copy the key to `.env` as `GEMINI_API_KEY`

#### SendGrid API Key
1. Go to [SendGrid](https://sendgrid.com) and create an account
2. Verify your email address (check inbox)
3. Go to **Settings** > **API Keys**
4. Click **Create API Key**
5. Choose **Full Access** or **Restricted Access** with "Mail Send" permission
6. Copy the API key immediately (you won't see it again!)
7. Paste into `.env` as `SENDGRID_API_KEY`

**Note:** SendGrid free tier allows 100 emails/day, which is sufficient for daily workout emails.

#### Email Recipient
- Set `EMAIL_RECIPIENT` to the email address where you want to receive workout emails
- This should be a verified email address

### 2.3 Google Sheets Setup

#### Create Service Account
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Enable **Google Sheets API**:
   - Go to **APIs & Services** > **Library**
   - Search for "Google Sheets API"
   - Click **Enable**
4. Create Service Account:
   - Go to **IAM & Admin** > **Service Accounts**
   - Click **Create Service Account**
   - Name it (e.g., "fitness-agent")
   - Click **Create and Continue**
   - Skip role assignment, click **Done**
5. Create Key:
   - Click on the service account you just created
   - Go to **Keys** tab
   - Click **Add Key** > **Create new key**
   - Choose **JSON** format
   - Download the JSON file

#### Configure Google Sheets
1. Open the downloaded JSON file
2. Copy the entire JSON content
3. Paste into `.env` as `GOOGLE_CREDENTIALS` (as a single line, or use environment variable)
4. Note the `client_email` from the JSON (e.g., `fitness-agent@project-id.iam.gserviceaccount.com`)
5. Create or open your Google Sheet
6. Click **Share** button
7. Add the service account email (from step 4) with **Editor** permissions
8. Get the Spreadsheet ID from the URL:
   - URL format: `https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit`
   - Copy `SPREADSHEET_ID` to `.env`

## Step 3: Test Configuration

### 3.1 Test API Keys
```bash
python test_keys.py
```

This verifies all LLM API keys are working.

### 3.2 Test Email Integration
```bash
python test_email.py
```

This tests SendGrid connection and email sending.

### 3.3 Test Full Workflow
```bash
python main.py
```

This runs the complete workout generation workflow locally.

## Step 4: Verify Setup

Check that your `.env` file contains:
- ✅ `ANTHROPIC_API_KEY`
- ✅ `OPENAI_API_KEY`
- ✅ `GEMINI_API_KEY`
- ✅ `SENDGRID_API_KEY`
- ✅ `EMAIL_RECIPIENT`
- ✅ `SPREADSHEET_ID`
- ✅ `GOOGLE_CREDENTIALS`

## Troubleshooting

### SendGrid Issues
- **"API key not configured"**: Check that `SENDGRID_API_KEY` is in `.env`
- **"401 Unauthorized"**: API key is invalid or expired - generate a new one
- **"403 Forbidden"**: API key doesn't have "Mail Send" permission - recreate with correct permissions
- **Email not received**: Check spam folder, verify sender email in SendGrid dashboard

### Google Sheets Issues
- **"GOOGLE_CREDENTIALS not set"**: Check that JSON is properly formatted in `.env`
- **"Permission denied"**: Make sure service account email has Editor access to the sheet
- **"Spreadsheet not found"**: Verify `SPREADSHEET_ID` is correct from the sheet URL

### API Key Issues
- **"Invalid API key"**: Verify key is copied correctly (no extra spaces)
- **"Rate limit exceeded"**: Wait a few minutes and try again
- **"Model not found"**: Check that model names in `config.py` are correct

## Next Steps

Once local testing works:
1. Deploy to Cloud Functions (see `docs/DEPLOYMENT.md`)
2. Set up Cloud Scheduler for daily triggers
3. Monitor logs and adjust as needed

## Security Notes

- **Never commit `.env` file to git** (it's in `.gitignore`)
- **Rotate API keys periodically** for security
- **Use environment variables in Cloud** instead of hardcoding
- **Limit service account permissions** to only what's needed


