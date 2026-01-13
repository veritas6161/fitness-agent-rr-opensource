# Fitness Agent - Deployment Guide

Complete guide for deploying Fitness Agent to Google Cloud Functions and setting up Cloud Scheduler.

## Prerequisites

- Google Cloud Platform account with billing enabled
- `gcloud` CLI installed and configured
- All API keys configured (see `docs/SETUP.md`)
- Local testing verified (run `python main.py` successfully)

## Step 1: Prepare for Deployment

### 1.1 Verify Local Setup

```bash
cd fitness-agent

# Test API keys
python test_keys.py

# Test email integration (if SendGrid is set up)
python test_email.py

# Test Sheets integration
python test_sheets.py

# Test full workflow
python main.py
```

### 1.2 Check .gcloudignore

Verify `.gcloudignore` exists and excludes:
- `.env` files
- `__pycache__/`
- Test files
- Personal/archive folders

## Step 2: Deploy to Cloud Functions

### 2.1 Set Up GCP Project

```bash
# Set your project
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable cloudscheduler.googleapis.com
gcloud services enable sheets.googleapis.com
```

### 2.2 Deploy Function

From the `fitness-agent/` directory:

```bash
gcloud functions deploy fitness-agent \
  --gen2 \
  --runtime python39 \
  --trigger-http \
  --allow-unauthenticated \
  --entry-point generate_workout \
  --source . \
  --region us-central1 \
  --timeout 540s \
  --memory 512MB
```

**Note:** 
- `--gen2` uses Cloud Functions 2nd generation (better performance)
- `--timeout 540s` allows up to 9 minutes (workout generation can take time)
- `--memory 512MB` should be sufficient (increase if needed)

### 2.3 Set Environment Variables

After deployment, set environment variables:

```bash
# Get your function name and region
FUNCTION_NAME=fitness-agent
REGION=us-central1

# Set API keys
gcloud functions deploy $FUNCTION_NAME \
  --gen2 \
  --region $REGION \
  --update-env-vars ANTHROPIC_API_KEY=your-key-here

gcloud functions deploy $FUNCTION_NAME \
  --gen2 \
  --region $REGION \
  --update-env-vars OPENAI_API_KEY=your-key-here

gcloud functions deploy $FUNCTION_NAME \
  --gen2 \
  --region $REGION \
  --update-env-vars GEMINI_API_KEY=your-key-here

gcloud functions deploy $FUNCTION_NAME \
  --gen2 \
  --region $REGION \
  --update-env-vars SENDGRID_API_KEY=your-key-here

gcloud functions deploy $FUNCTION_NAME \
  --gen2 \
  --region $REGION \
  --update-env-vars EMAIL_RECIPIENT=your-email@example.com

gcloud functions deploy $FUNCTION_NAME \
  --gen2 \
  --region $REGION \
  --update-env-vars SPREADSHEET_ID=your-sheet-id

# For GOOGLE_CREDENTIALS (JSON), you need to escape it properly
# Option 1: Set as single line (escape quotes)
gcloud functions deploy $FUNCTION_NAME \
  --gen2 \
  --region $REGION \
  --update-env-vars GOOGLE_CREDENTIALS='{"type":"service_account",...}'

# Option 2: Use a file (recommended for complex JSON)
gcloud functions deploy $FUNCTION_NAME \
  --gen2 \
  --region $REGION \
  --update-secrets GOOGLE_CREDENTIALS=google-credentials:latest
```

**Better approach - Set all at once:**

Create a file `env.yaml`:
```yaml
ANTHROPIC_API_KEY: your-key-here
OPENAI_API_KEY: your-key-here
GEMINI_API_KEY: your-key-here
SENDGRID_API_KEY: your-key-here
EMAIL_RECIPIENT: your-email@example.com
SPREADSHEET_ID: your-sheet-id
GOOGLE_CREDENTIALS: '{"type":"service_account",...}'
```

Then deploy with:
```bash
gcloud functions deploy fitness-agent \
  --gen2 \
  --region us-central1 \
  --update-env-vars-file env.yaml
```

### 2.4 Test Deployed Function

Get the function URL:
```bash
gcloud functions describe fitness-agent \
  --gen2 \
  --region us-central1 \
  --format="value(serviceConfig.uri)"
```

Test with a manual trigger:
```bash
# Get the URL
FUNCTION_URL=$(gcloud functions describe fitness-agent \
  --gen2 \
  --region us-central1 \
  --format="value(serviceConfig.uri)")

# Test with GET request
curl "$FUNCTION_URL?trigger=manual"
```

Or test in browser:
```
https://[REGION]-[PROJECT].cloudfunctions.net/fitness-agent?trigger=manual
```

## Step 3: Set Up Cloud Scheduler

### 3.1 Create Scheduler Job

```bash
# Get your function URL
FUNCTION_URL=$(gcloud functions describe fitness-agent \
  --gen2 \
  --region us-central1 \
  --format="value(serviceConfig.uri)")

# Create scheduler job
gcloud scheduler jobs create http fitness-agent-daily \
  --location=us-central1 \
  --schedule="0 6 * * *" \
  --uri="$FUNCTION_URL?trigger=cron" \
  --http-method=GET \
  --time-zone="America/Los_Angeles" \
  --description="Daily workout generation at 6 AM PST"
```

**Schedule Details:**
- `0 6 * * *` = 6 AM (06:00) every day
- `America/Los_Angeles` = Pacific Time
- `?trigger=cron` = Identifies this as a cron trigger (Friday skip logic)

### 3.2 Test Scheduler

```bash
# Run job immediately (for testing)
gcloud scheduler jobs run fitness-agent-daily \
  --location=us-central1
```

### 3.3 Verify Schedule

```bash
# List scheduler jobs
gcloud scheduler jobs list --location=us-central1

# Describe job details
gcloud scheduler jobs describe fitness-agent-daily \
  --location=us-central1
```

## Step 4: Monitor and Verify

### 4.1 Check Logs

```bash
# View recent logs
gcloud functions logs read fitness-agent \
  --gen2 \
  --region us-central1 \
  --limit 50

# Follow logs in real-time
gcloud functions logs read fitness-agent \
  --gen2 \
  --region us-central1 \
  --follow
```

### 4.2 Verify Friday Skip

The function should automatically skip Fridays (trainer day). Test by:
1. Manually triggering on a Friday
2. Checking response for `"status": "skipped"`

### 4.3 Check Email Delivery

- Verify workout emails are received daily at 6 AM PST (except Fridays)
- Check spam folder if emails not received
- Verify email formatting is correct

### 4.4 Check Sheets Updates

- Verify new workout tabs are created daily
- Check that workout data is written correctly
- Verify tab naming: `Workout_YYYY-MM-DD`

## Step 5: Troubleshooting

### Function Not Deploying

```bash
# Check for errors
gcloud functions describe fitness-agent \
  --gen2 \
  --region us-central1

# Check build logs
gcloud builds list --limit=5
```

### Function Timeout

- Increase timeout: `--timeout 900s` (15 minutes)
- Check logs for slow operations
- Verify API keys are working

### Environment Variables Not Set

```bash
# List current env vars
gcloud functions describe fitness-agent \
  --gen2 \
  --region us-central1 \
  --format="value(serviceConfig.environmentVariables)"
```

### Scheduler Not Triggering

```bash
# Check scheduler status
gcloud scheduler jobs describe fitness-agent-daily \
  --location=us-central1

# Check scheduler logs
gcloud logging read "resource.type=cloud_scheduler_job" \
  --limit=10
```

### Email Not Sending

- Verify `SENDGRID_API_KEY` is set correctly
- Check SendGrid dashboard for delivery status
- Verify `EMAIL_RECIPIENT` is correct
- Check function logs for email errors

### Sheets Not Updating

- Verify `GOOGLE_CREDENTIALS` is valid JSON
- Check that service account has access to sheet
- Verify `SPREADSHEET_ID` is correct
- Check function logs for Sheets errors

## Step 6: Update and Redeploy

### Update Code

```bash
# Make changes to code
# ...

# Redeploy
gcloud functions deploy fitness-agent \
  --gen2 \
  --region us-central1 \
  --source .
```

### Update Environment Variables

```bash
# Update single variable
gcloud functions deploy fitness-agent \
  --gen2 \
  --region us-central1 \
  --update-env-vars SPREADSHEET_ID=new-sheet-id

# Or update from file
gcloud functions deploy fitness-agent \
  --gen2 \
  --region us-central1 \
  --update-env-vars-file env.yaml
```

## Security Best Practices

1. **Use Secret Manager** for sensitive credentials:
   ```bash
   # Create secret
   echo -n 'your-api-key' | gcloud secrets create sendgrid-api-key --data-file=-
   
   # Grant function access
   gcloud secrets add-iam-policy-binding sendgrid-api-key \
     --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
     --role="roles/secretmanager.secretAccessor"
   
   # Use in function
   gcloud functions deploy fitness-agent \
     --gen2 \
     --region us-central1 \
     --update-secrets SENDGRID_API_KEY=sendgrid-api-key:latest
   ```

2. **Restrict Function Access** (optional):
   ```bash
   # Remove --allow-unauthenticated and use IAM
   gcloud functions remove-iam-policy-binding fitness-agent \
     --gen2 \
     --region us-central1 \
     --member="allUsers" \
     --role="roles/cloudfunctions.invoker"
   ```

3. **Monitor Costs**: Cloud Functions and Scheduler have free tiers, but monitor usage

## Next Steps

- Set up Cloud Monitoring alerts for errors
- Configure error notifications
- Set up backup/archival for old workout tabs
- Consider adding webhook support for manual triggers


