import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from server import app

code = """
#include <stdio.h>

main() {   // ❌ no return type
    printf("Hello");
}
"""

print("Starting test...")
with app.app_context():
    with app.test_client() as client:
        try:
            print("Sending POST request to /api/analyze...")
            response = client.post('/api/analyze', json={'code': code})
            print("Status code:", response.status_code)
            if response.status_code == 500:
                print("500 ERROR DETAILS:", response.data.decode('utf-8')[:500])
            print("Response data successfully parsed.")
        except Exception as e:
            import traceback
            traceback.print_exc()

print("Test complete.")
