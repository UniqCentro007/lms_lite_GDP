"""
Script to test instructor login functionality
"""
import requests
import json

# Base URL - adjust if your server is running on a different port
BASE_URL = 'http://127.0.0.1:8000'
LOGIN_URL = f'{BASE_URL}/api/auth/instructor/login/'

# Instructor credentials
credentials = {
    'username': 'test_instructor',
    'password': 'instructor123'
}

print("=" * 60)
print("Testing Instructor Login")
print("=" * 60)
print(f"\nLogin URL: {LOGIN_URL}")
print(f"Username: {credentials['username']}")
print(f"Password: {credentials['password']}")
print("\nAttempting login...")

try:
    # Make POST request to login endpoint
    response = requests.post(LOGIN_URL, json=credentials)
    
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("\n" + "=" * 60)
        print("SUCCESS: Login successful!")
        print("=" * 60)
        print(f"\nUser Information:")
        print(f"  Username: {data.get('user', {}).get('username', 'N/A')}")
        print(f"  Email: {data.get('user', {}).get('email', 'N/A')}")
        print(f"  Role: {data.get('user', {}).get('role', 'N/A')}")
        print(f"  First Name: {data.get('user', {}).get('first_name', 'N/A')}")
        print(f"  Last Name: {data.get('user', {}).get('last_name', 'N/A')}")
        print(f"\nTokens:")
        print(f"  Access Token: {data.get('tokens', {}).get('access', 'N/A')[:50]}...")
        print(f"  Refresh Token: {data.get('tokens', {}).get('refresh', 'N/A')[:50]}...")
        print(f"\nMessage: {data.get('message', 'N/A')}")
        print("\n" + "=" * 60)
        print("Login test PASSED!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("ERROR: Login failed!")
        print("=" * 60)
        try:
            error_data = response.json()
            print(f"Error: {error_data}")
        except:
            print(f"Response: {response.text}")
        print("\n" + "=" * 60)
        print("Login test FAILED!")
        print("=" * 60)
        
except requests.exceptions.ConnectionError:
    print("\n" + "=" * 60)
    print("ERROR: Could not connect to the server!")
    print("=" * 60)
    print("Make sure the Django development server is running:")
    print("  python manage.py runserver")
    print("\n" + "=" * 60)
except Exception as e:
    print(f"\nERROR: {str(e)}")
    print("\n" + "=" * 60)
    print("Login test FAILED!")
    print("=" * 60)
