import os

ENDPOINTS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'endpoints.txt')

def load_endpoints(file_path=ENDPOINTS_FILE):
    endpoints = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    for line in lines[2:]:  # Skip header lines
        if not line.strip():
            continue
        parts = line.strip().split('\t')
        if len(parts) == 2:
            service, url = parts
            endpoints[service.strip()] = url.strip()
    return endpoints

ENDPOINTS = load_endpoints()
