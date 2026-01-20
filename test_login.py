"""
Simple script to test student login
"""
import json

# Test login with different methods
print("="*60)
print("STUDENT LOGIN TEST")
print("="*60)

# Method 1: Using urllib (built-in, no extra packages needed)
print("\n1. Testing with urllib (built-in)...")
try:
    import urllib.request
    import urllib.parse
    
    url = "http://127.0.0.1:8000/api/auth/login/"
    data = json.dumps({
        "username": "student1",
        "password": "student123"
    }).encode('utf-8')
    
    req = urllib.request.Request(
        url,
        data=data,
        headers={'Content-Type': 'application/json'}
    )
    
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode())
        print("✅ SUCCESS!")
        print(f"Status: {response.status}")
        print(f"User: {result['user']['username']} ({result['user']['role']})")
        print(f"Access Token: {result['tokens']['access'][:50]}...")
        print("\nFull Response:")
        print(json.dumps(result, indent=2))
        
except urllib.error.HTTPError as e:
    print(f"❌ HTTP Error: {e.code}")
    error_body = e.read().decode()
    print(f"Error Response: {error_body}")
except Exception as e:
    print(f"❌ Error: {e}")

# Method 2: Show what the request should look like
print("\n" + "="*60)
print("CORRECT REQUEST FORMAT")
print("="*60)
print("\nURL: http://127.0.0.1:8000/api/auth/login/")
print("Method: POST")
print("Headers:")
print("  Content-Type: application/json")
print("\nBody (JSON):")
print(json.dumps({
    "username": "student1",
    "password": "student123"
}, indent=2))

print("\n" + "="*60)
print("COMMON ERRORS")
print("="*60)
print("\n❌ 400 Bad Request:")
print("   - Missing username or password")
print("   - Wrong Content-Type header")
print("\n❌ 401 Unauthorized:")
print("   - Wrong username or password")
print("   - Username: 'student1' (exact)")
print("   - Password: 'student123' (exact)")
print("\n❌ 404 Not Found:")
print("   - Missing trailing slash: /api/auth/login/")
print("   - Wrong URL path")
print("\n❌ 405 Method Not Allowed:")
print("   - Using GET instead of POST")
print("   - Must use POST method")




