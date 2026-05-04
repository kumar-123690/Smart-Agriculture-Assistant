import urllib.request, json
data = json.dumps({'nitrogen': 120, 'phosphorus': 50, 'potassium': 60, 'ph': 6.5, 'temperature': 25, 'humidity': 80, 'rainfall': 150}).encode('utf-8')
req = urllib.request.Request('http://127.0.0.1:8000/api/predict/crop', data=data, headers={'Content-Type': 'application/json'})
try:
    print(urllib.request.urlopen(req).read().decode('utf-8'))
except Exception as e:
    print('ERROR:', e.read().decode('utf-8'))
