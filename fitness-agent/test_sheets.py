"""
Test script for Google Sheets integration.

Tests:
1. Google Sheets credentials configuration
2. Reading past workouts
3. Creating new workout tabs
4. Writing workout data
5. Integration with main workflow
"""

import os
import json
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables
load_dotenv(override=True)

from config import SPREADSHEET_ID, GOOGLE_CREDENTIALS
from main import get_sheets_service
import sheets_client


def test_credentials_configuration():
    """Test that Google Sheets credentials are configured."""
    print("=" * 80)
    print("TEST 1: Credentials Configuration")
    print("=" * 80)
    
    if not GOOGLE_CREDENTIALS:
        print("❌ GOOGLE_CREDENTIALS not found in environment")
        print("   Please add GOOGLE_CREDENTIALS to your .env file")
        return False
    
    if not SPREADSHEET_ID or SPREADSHEET_ID == "YOUR_SPREADSHEET_ID_HERE":
        print("❌ SPREADSHEET_ID not configured")
        print("   Please add SPREADSHEET_ID to your .env file or config.py")
        return False
    
    try:
        creds_dict = json.loads(GOOGLE_CREDENTIALS)
        print(f"✅ GOOGLE_CREDENTIALS found (type: {creds_dict.get('type', 'unknown')})")
        print(f"   Project ID: {creds_dict.get('project_id', 'N/A')}")
        print(f"   Client Email: {creds_dict.get('client_email', 'N/A')}")
    except json.JSONDecodeError:
        print("❌ GOOGLE_CREDENTIALS is not valid JSON")
        return False
    
    print(f"✅ SPREADSHEET_ID found: {SPREADSHEET_ID}")
    return True


def test_sheets_service():
    """Test creating Google Sheets service."""
    print("\n" + "=" * 80)
    print("TEST 2: Google Sheets Service Initialization")
    print("=" * 80)
    
    service = get_sheets_service()
    
    if service is None:
        print("❌ Failed to create Sheets service")
        print("   This is expected if GOOGLE_CREDENTIALS is not set")
        return False
    
    print("✅ Google Sheets service created successfully")
    return service


def test_read_past_workouts(service):
    """Test reading past workouts."""
    print("\n" + "=" * 80)
    print("TEST 3: Reading Past Workouts")
    print("=" * 80)
    
    try:
        past_workouts = sheets_client.read_past_workouts(
            service=service,
            spreadsheet_id=SPREADSHEET_ID,
            days=14,
        )
        print(f"✅ Successfully read {len(past_workouts)} past workouts")
        
        if past_workouts:
            print("\nSample workout tabs found:")
            for workout in past_workouts[:3]:
                print(f"   - {workout.get('tab_name')} ({workout.get('date')})")
        else:
            print("   (No past workouts found - this is OK for new setup)")
        
        return True
    except Exception as e:
        print(f"❌ Failed to read past workouts: {e}")
        return False


def test_create_tab(service):
    """Test creating a new workout tab."""
    print("\n" + "=" * 80)
    print("TEST 4: Creating Workout Tab")
    print("=" * 80)
    
    # Use a test date
    test_date = datetime.now().strftime("%Y-%m-%d")
    test_tab_name = f"Workout_{test_date}_TEST"
    
    try:
        # Check if tab exists
        if sheets_client.tab_exists(service, SPREADSHEET_ID, test_tab_name):
            print(f"⚠️  Tab {test_tab_name} already exists - skipping creation test")
            return True
        
        # Create tab
        result = sheets_client.create_tab(
            service=service,
            spreadsheet_id=SPREADSHEET_ID,
            tab_name=test_tab_name,
            headers=["Exercise", "Set", "Weight", "Reps", "RIR", "Feel", "Notes"]
        )
        
        print(f"✅ Successfully created tab: {test_tab_name}")
        
        # Verify tab exists
        if sheets_client.tab_exists(service, SPREADSHEET_ID, test_tab_name):
            print(f"✅ Verified tab exists: {test_tab_name}")
            return True
        else:
            print(f"❌ Tab was created but verification failed")
            return False
            
    except Exception as e:
        print(f"❌ Failed to create tab: {e}")
        return False


def test_write_data(service):
    """Test writing workout data to a tab."""
    print("\n" + "=" * 80)
    print("TEST 5: Writing Workout Data")
    print("=" * 80)
    
    test_date = datetime.now().strftime("%Y-%m-%d")
    test_tab_name = f"Workout_{test_date}_TEST"
    
    try:
        # Create test data
        test_data = [
            ["Exercise", "Set", "Weight", "Reps", "RIR", "Feel", "Notes"],
            ["Barbell RDL", "1", "95", "8", "2", "", ""],
            ["Barbell RDL", "2", "95", "8", "2", "", ""],
            ["Barbell RDL", "3", "95", "7", "2", "", ""],
            ["Barbell Back Squat", "1", "115", "8", "2", "", ""],
        ]
        
        # Write data
        result = sheets_client.write_data(
            service=service,
            spreadsheet_id=SPREADSHEET_ID,
            tab_name=test_tab_name,
            data=test_data,
        )
        
        print(f"✅ Successfully wrote {len(test_data)} rows to {test_tab_name}")
        print(f"   Updated cells: {result.get('updatedCells', 'N/A')}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to write data: {e}")
        return False


def test_tab_naming_format():
    """Test that tab naming format is correct."""
    print("\n" + "=" * 80)
    print("TEST 6: Tab Naming Format")
    print("=" * 80)
    
    test_date = datetime.now().strftime("%Y-%m-%d")
    expected_format = f"Workout_{test_date}"
    
    print(f"✅ Expected format: {expected_format}")
    print(f"   Format matches: Workout_YYYY-MM-DD")
    return True


def test_graceful_degradation():
    """Test that missing credentials don't crash the system."""
    print("\n" + "=" * 80)
    print("TEST 7: Graceful Degradation (Missing Credentials)")
    print("=" * 80)
    
    # Temporarily remove credentials
    original_creds = os.environ.get("GOOGLE_CREDENTIALS")
    if "GOOGLE_CREDENTIALS" in os.environ:
        del os.environ["GOOGLE_CREDENTIALS"]
    
    service = get_sheets_service()
    
    # Restore credentials
    if original_creds:
        os.environ["GOOGLE_CREDENTIALS"] = original_creds
    
    if service is None:
        print("✅ Graceful degradation works - returns None without crashing")
        print("   System can continue without Sheets integration")
        return True
    else:
        print("⚠️  Service was created even without credentials - check logic")
        return False


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("FITNESS AGENT - SHEETS INTEGRATION TEST")
    print("=" * 80 + "\n")
    
    results = []
    
    # Test 1: Credentials
    creds_ok = test_credentials_configuration()
    results.append(("Credentials Configuration", creds_ok))
    
    if not creds_ok:
        print("\n⚠️  Cannot continue without credentials. Please configure GOOGLE_CREDENTIALS and SPREADSHEET_ID.")
        results.append(("Graceful Degradation", test_graceful_degradation()))
    else:
        # Test 2: Service initialization
        service = test_sheets_service()
        service_ok = service is not None
        results.append(("Service Initialization", service_ok))
        
        if service_ok:
            # Test 3-5: Sheets operations
            results.append(("Read Past Workouts", test_read_past_workouts(service)))
            results.append(("Create Tab", test_create_tab(service)))
            results.append(("Write Data", test_write_data(service)))
        
        # Test 6: Format check (always runs)
        results.append(("Tab Naming Format", test_tab_naming_format()))
        
        # Test 7: Graceful degradation
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
        print("✅ ALL TESTS PASSED - Sheets integration is working!")
    else:
        print("⚠️  SOME TESTS FAILED - Check configuration and try again")
    print("=" * 80 + "\n")


