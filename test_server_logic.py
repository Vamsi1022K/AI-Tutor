import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from server import app

code = """
#include <stdio.h>

main() {
    printf("Hello");
}
"""

with app.app_context():
    with app.test_client() as client:
        print("Sending POST request to /api/analyze...")
        response = client.post('/api/analyze', json={'code': code})
        print("Status code:", response.status_code)
        print("Response data:", response.data.decode('utf-8'))
