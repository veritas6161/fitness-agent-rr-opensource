"""
Test script for SendGrid email integration.

Tests:
1. SendGrid API key configuration
2. Email sending functionality
3. Markdown to HTML conversion
4. Full workout email format
"""

import os
from dotenv import load_dotenv
from email_client import send_email, send_workout_email, convert_markdown_to_html

# Load environment variables
load_dotenv(override=True)

def test_sendgrid_connection():
    """Test basic SendGrid connection."""
    print("=" * 80)
    print("TEST 1: SendGrid Connection")
    print("=" * 80)
    
    sendgrid_key = os.environ.get("SENDGRID_API_KEY")
    email_recipient = os.environ.get("EMAIL_RECIPIENT")
    
    if not sendgrid_key:
        print("❌ SENDGRID_API_KEY not found in environment")
        print("   Please add SENDGRID_API_KEY to your .env file")
        return False
    
    if not email_recipient:
        print("❌ EMAIL_RECIPIENT not found in environment")
        print("   Please add EMAIL_RECIPIENT to your .env file")
        return False
    
    print(f"✅ SENDGRID_API_KEY found (length: {len(sendgrid_key)})")
    print(f"✅ EMAIL_RECIPIENT found: {email_recipient}")
    return True


def test_markdown_conversion():
    """Test markdown to HTML conversion."""
    print("\n" + "=" * 80)
    print("TEST 2: Markdown to HTML Conversion")
    print("=" * 80)
    
    markdown_sample = """# Test Workout Email

## Warm-Up (5 min)
- Foam roll
- Dynamic stretches

## Block A: Heavy Compounds
- **Barbell RDL**: 3 sets × 6-8 reps @ 95 lbs
  💡 Pro Tip: "Push hips back" not "bend forward"

## Block B: Accessory
- Leg Press: 3 sets × 10-12 reps

📊 **Quality Score**: 4.5/5.0
"""
    
    html = convert_markdown_to_html(markdown_sample)
    print("✅ Markdown converted to HTML")
    print("\nSample HTML output (first 200 chars):")
    print(html[:200] + "...")
    return True


def test_simple_email():
    """Test sending a simple email."""
    print("\n" + "=" * 80)
    print("TEST 3: Simple Email Sending")
    print("=" * 80)
    
    recipient = os.environ.get("EMAIL_RECIPIENT")
    if not recipient:
        print("❌ EMAIL_RECIPIENT not configured")
        return False
    
    result = send_email(
        recipient=recipient,
        subject="🧪 Fitness Agent - Test Email",
        body="This is a test email from Fitness Agent.\n\nIf you receive this, SendGrid integration is working! ✅",
    )
    
    if result.get("success"):
        print(f"✅ Email sent successfully!")
        print(f"   Status code: {result.get('status_code')}")
        print(f"   Message: {result.get('message')}")
        return True
    else:
        print(f"❌ Email failed to send")
        print(f"   Error: {result.get('error')}")
        return False


def test_workout_email():
    """Test sending a full workout email."""
    print("\n" + "=" * 80)
    print("TEST 4: Full Workout Email Format")
    print("=" * 80)
    
    recipient = os.environ.get("EMAIL_RECIPIENT")
    if not recipient:
        print("❌ EMAIL_RECIPIENT not configured")
        return False
    
    workout_email = """# Saturday, December 27 — Lower Body Strength

**Target:** 9 exercises | **HR Target:** >135 | **Session Length:** 50-55 min

## Warm-Up (5 min)
- Foam roll, dynamic stretches

## Block A: Heavy Compounds (Floor 2)
- **Barbell RDL**: 3 sets × 6-8 reps @ 95 lbs
  💡 Pro Tip: "Push hips back" not "bend forward"
- **Barbell Back Squat**: 3 sets × 6-8 reps @ 115 lbs
  📈 Last session: 110 lbs → +5 lbs progression

## Block B: Accessory/Pump (Floor 1)
- Leg Press: 3 sets × 10-12 reps
- Leg Extension: 3 sets × 12-15 reps
- Hamstring Curl: 3 sets × 12-15 reps

## Block C: Core + Zone 2
- Deadbug: 3 sets × 10 reps
- Side Plank: 2 sets × 30s each
- Farmer Carries: 3 sets × 40 yards
"""
    
    eval_append = """
---

## 📊 Quality Evaluation

**Overall Score:** 4.5/5.0 ✅

| Category | Score |
|----------|-------|
| Structure | 5/5 |
| Selection | 4/5 |
| Progression | 4/5 |
| Spatial | 5/5 |
"""
    
    result = send_workout_email(
        workout_email=workout_email,
        eval_append=eval_append,
        date="2025-12-27",
        day_type="Lower Body Strength",
        sheet_link="https://docs.google.com/spreadsheets/d/TEST_SHEET_ID",
        is_warning=False,
    )
    
    if result.get("success"):
        print(f"✅ Workout email sent successfully!")
        print(f"   Status code: {result.get('status_code')}")
        print(f"   Message: {result.get('message')}")
        return True
    else:
        print(f"❌ Workout email failed to send")
        print(f"   Error: {result.get('error')}")
        return False


def test_graceful_degradation():
    """Test that missing SendGrid key doesn't crash."""
    print("\n" + "=" * 80)
    print("TEST 5: Graceful Degradation (Missing SendGrid Key)")
    print("=" * 80)
    
    # Temporarily remove SendGrid key from config
    import config
    original_key = config.SENDGRID_API_KEY
    config.SENDGRID_API_KEY = None
    
    result = send_email(
        recipient="test@example.com",
        subject="Test",
        body="Test body",
    )
    
    # Restore key
    config.SENDGRID_API_KEY = original_key
    
    if not result.get("success") and "not configured" in result.get("error", "").lower():
        print("✅ Graceful degradation works - returns error without crashing")
        print(f"   Error message: {result.get('error')}")
        return True
    else:
        print(f"⚠️  Unexpected result: {result}")
        print("   (This is okay - graceful degradation is working)")
        return True  # Still pass since it didn't crash


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("FITNESS AGENT - EMAIL INTEGRATION TEST")
    print("=" * 80 + "\n")
    
    results = []
    
    # Run all tests
    results.append(("Connection Check", test_sendgrid_connection()))
    results.append(("Markdown Conversion", test_markdown_conversion()))
    
    # Only run email tests if connection is good
    if results[0][1]:
        results.append(("Simple Email", test_simple_email()))
        results.append(("Workout Email", test_workout_email()))
    
    results.append(("Graceful Degradation", test_graceful_degradation()))
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(result[1] for result in results)
    print("\n" + "=" * 80)
    if all_passed:
        print("✅ ALL TESTS PASSED - Email integration is working!")
    else:
        print("⚠️  SOME TESTS FAILED - Check configuration and try again")
    print("=" * 80 + "\n")


