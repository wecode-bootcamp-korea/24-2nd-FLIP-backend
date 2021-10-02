##

---

# FLIP | 플립

<img src='./flip_log.png' alt='logo'>

<br><br>

---

## frip | 프립

- [프립](https://www.frip.co.kr/) 사이트
- 소개: 여가, 액티비티 공유 플랫폼



## 팀원

- Front-end: 금보배, 김세준, 지의선
- Back-end: 서동규, 성우진, 손명희(PM)



## 개발 기간

- 기간: 2021.09.13 ~ 2021.10.01 (16일)



## 적용 기술

- Back-end: Django, Python, MySQL, jwt, bcrypt, Storage, Transaction, AWS S3, AWS RDS, AWS EC2
- 협업툴: Trello, Slack, Github(Rebase), AQuery



## 영상

[프립 구현 영상](http://www.youtube.com)



## 구현 기능 및 개인 역할

`서동규`

- 숙소 상세페이지
  - React-slick 활용한 image slider 구현
  - React-dates 기반 숙소 예약 탭 기능 구현
  - 숙소 bookmark 기능
  - Kakao map API 활용, 숙소 위치 로딩 및 마커 설정 기능
- 회원가입 및 로그인
  - Firebase 기반 Google social login 기능 구현
  - Redux로 user 로그인 상태 글로벌 관리

`성우진`

-

`손명희`
- Kakao Social login 기능구현
- JWT - access token을 발행 하고 서버에서 access token을 복호화해 권한을 확인
- 계좌정보 등록 및 S3, transaction을 활용한 상품등록 기능구현
- Soft Delete model 활용한 회원관리
- REST API, POST/ GET 메소드를 통한 HTTP 통신
- UNIT TEST를 통한 효율적인 테스트 구현
- AWS deploy (EC2 / RDS / S3)


## EndPoint

[post] UserProductView         : /products/host/<int:user_id> <br>

[get] UserProductView          : /products/host/<int:user_id> <br>

[get] ListCategoryView         : /products/main_category/<int:main_category_id> <br>

[get] ProductDetailView        : /product/<int:product_id> <br>

[post] LikeView                : /product/<int:product_id>/like<br>

[get] ReviewView               : /product/<int:product_id>/review <br>

[get] MainPageCategoryView     : /products/main_page_category

[post] LocationView            : /product/<int:product_id>/location

[post] ImageUploadView         : /product/<int:product_id>/host/<int:user_id>/image_upload

[post] KakaoSignInView         : /signin

[post] BankAccountView         : /bank_account/<int:user_id>

[get] BankAccountView          : /bank_account/<int:user_id>

[get] ProductListView          : /products/list/<int:main_category_id>?sub_category_id=&order=



## Modeling

<img src='./flip_log.png' alt='logo'>

## 소감 및 후기

- 서동규: ([후기](https://업로드후수정.com)-개인 벨로그)

- 성우진: ([후기](https://업로드후수정.com)-개인 벨로그)

- 손명희: ([후기](https://업로드후수정.com)-개인 벨로그)


## 레퍼런스

- 이 프로젝트는 [프립](https://www.frip.co.kr/) 사이트를 참조하여 학습목적으로 만들었습니다.
- 실무수준의 프로젝트이지만 학습용으로 만들었기 때문에 이 코드를 활용하여 이득을 취하거나 무단 배포할 경우 법적으로 문제될 수 있습니다.
- 이 프로젝트에서 사용하고 있는 사진 대부분은 위코드에서 구매한 것이므로 해당 프로젝트 외부인이 사용할 수 없습니다.