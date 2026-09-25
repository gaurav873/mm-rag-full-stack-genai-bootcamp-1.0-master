from api.configs.storage import upload_bytes, download_bytes

test_key = "test/hello.txt"
upload_bytes(test_key, b"hello supabase storage", content_type="text/plain")
print(download_bytes(test_key))