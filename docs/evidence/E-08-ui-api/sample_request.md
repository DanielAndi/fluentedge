```http
POST /predict HTTP/1.1
Host: localhost:8000
Content-Type: multipart/form-data

expected_phrase=the quick brown fox
file=@tests/fixtures/synthetic/clip_000.wav
```
