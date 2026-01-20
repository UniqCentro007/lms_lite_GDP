"""
Script to test API endpoints and show output
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_response(response, show_body=True):
    print(f"\nStatus Code: {response.status_code}")
    print(f"URL: {response.url}")
    if show_body and response.text:
        try:
            data = response.json()
            print("Response:")
            print(json.dumps(data, indent=2))
        except:
            print(f"Response: {response.text[:200]}")

# Test 1: Root API Endpoint
print_section("1. ROOT API ENDPOINT - Get API Documentation")
try:
    response = requests.get(f"{BASE_URL}/")
    print_response(response)
except Exception as e:
    print(f"Error: {e}")

# Test 2: Login
print_section("2. LOGIN - Authenticate Student")
try:
    login_data = {
        "username": "student1",
        "password": "student123"
    }
    response = requests.post(f"{BASE_URL}/api/auth/login/", json=login_data)
    print_response(response)
    
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data.get('tokens', {}).get('access')
        user_info = token_data.get('user', {})
        print(f"\n✅ Login Successful!")
        print(f"User: {user_info.get('username')} ({user_info.get('role')})")
        print(f"Access Token: {access_token[:50]}...")
    else:
        access_token = None
        print("❌ Login Failed")
except Exception as e:
    print(f"Error: {e}")
    access_token = None

# Test 3: Get Courses (with authentication)
print_section("3. GET COURSES - List Available Courses")
try:
    headers = {}
    if access_token:
        headers['Authorization'] = f'Bearer {access_token}'
    
    response = requests.get(f"{BASE_URL}/api/courses/", headers=headers)
    print_response(response)
except Exception as e:
    print(f"Error: {e}")

# Test 4: Get Dashboard
print_section("4. DASHBOARD - Get Student Dashboard Statistics")
try:
    headers = {}
    if access_token:
        headers['Authorization'] = f'Bearer {access_token}'
    
    response = requests.get(f"{BASE_URL}/api/reports/dashboard/", headers=headers)
    print_response(response)
except Exception as e:
    print(f"Error: {e}")

# Test 5: Get Course Details
print_section("5. COURSE DETAILS - Get Specific Course Information")
try:
    headers = {}
    if access_token:
        headers['Authorization'] = f'Bearer {access_token}'
    
    response = requests.get(f"{BASE_URL}/api/courses/", headers=headers)
    if response.status_code == 200:
        courses = response.json()
        if courses.get('results') and len(courses['results']) > 0:
            course_id = courses['results'][0]['id']
            detail_response = requests.get(f"{BASE_URL}/api/courses/{course_id}/", headers=headers)
            print_response(detail_response)
        else:
            print("No courses found")
except Exception as e:
    print(f"Error: {e}")

# Test 6: Get Quiz Questions
print_section("6. QUIZ QUESTIONS - Get Quiz Questions for a Course")
try:
    headers = {}
    if access_token:
        headers['Authorization'] = f'Bearer {access_token}'
    
    # First get courses to find quiz
    response = requests.get(f"{BASE_URL}/api/courses/", headers=headers)
    if response.status_code == 200:
        courses = response.json()
        if courses.get('results') and len(courses['results']) > 0:
            course_id = courses['results'][0]['id']
            quiz_response = requests.get(f"{BASE_URL}/api/quizzes/", headers=headers)
            if quiz_response.status_code == 200:
                quizzes = quiz_response.json()
                if quizzes.get('results') and len(quizzes['results']) > 0:
                    quiz_id = quizzes['results'][0]['id']
                    questions_response = requests.get(f"{BASE_URL}/api/quizzes/{quiz_id}/questions/", headers=headers)
                    print_response(questions_response)
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*60)
print("  API TESTING COMPLETE")
print("="*60)
print("\n💡 Tip: You can also test these endpoints using:")
print("   - Browser: http://127.0.0.1:8000/")
print("   - Postman or any API client")
print("   - cURL commands (see QUICK_START.md)")




