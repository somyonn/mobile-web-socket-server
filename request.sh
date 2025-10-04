curl -X POST -S -H "Authorization: JWT b181ce4155b7413ebd1d86f1379151a7e035f8bd" \
-F "author=somyeongzzang" \
-F "image=@test.jpeg;type=image/jpeg" \
-F "title=curl 테스트" \
-F "text=API curl로 작성된 AP 테스트 입력 입니다." \
-F "created_date=2024-06-10T18:34:00+09:00" \
-F "published_date=2024-06-10T18:34:00+09:00" \
http://127.0.0.1:8000/api_root/Post/