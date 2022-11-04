# 알고리즘을 적용한 서버 구성

![image-20221104175141122](heeje.assets/image-20221104175141122.png)



### 요구사항

A. 유저 팔로우 기능 

B. 리뷰 좋아요 기능 

C. Movies 앱 기능 

	1. 전체 영화 목록 조회 
	1. 단일 영화 상세 조회 
	1. 영화 추천 기능



### 프로젝트 구상안

![image-20221104175420689](heeje.assets/image-20221104175420689.png)





## A.유저 팔로우 기능

![image-20221104175306217](heeje.assets/image-20221104175306217.png)

### view.py

```python
@require_POST
def follow(request, user_pk):
    if request.user.is_authenticated:
        User = get_user_model()
        me = request.user
        you = User.objects.get(pk=user_pk)
        if me != you:
            if you.followers.filter(pk=me.pk).exists():
                you.followers.remove(me)
                is_followed = False
            else:
                you.followers.add(me)
                is_followed = True
            context = {
                'is_followed': is_followed,
                'followers_count': you.followers.count(),
                'followings_count': you.followings.count(),
            }
            return JsonResponse(context)
        return redirect('accounts:profile', you.username)
    return redirect('accounts:login')
```



### templates/account/profile.html

```django
{% extends 'base.html' %}

{% block content %}
  <h1>{{ person.username }}의 프로필 페이지</h1>
  {% with followings=person.followings.all followers=person.followers.all %}
    <div>
      <div>
        팔로워 : <span id="followers-count">{{ person.followers.all|length }}</span> 
        팔로잉 : <span id="followings-count">{{ person.followings.all|length }}</span>
      </div>
      {% if user != person %}
        <div>
          <form id="follow-form" data-user-id="{{ person.pk }}">
            {% csrf_token %}
            {% if user in followers %}
              <button id="followBtn">언팔로우</button>
            {% else %}
              <button id="followBtn">팔로우</button>
            {% endif %}
          </form>
        </div>
      {% endif %}
    </div>
  {% endwith %}
{% endblock %}

{% block script %}
  <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
  <script>

  const form = document.querySelector('#follow-form')
  const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value
  form.addEventListener('submit', function (event) {
    event.preventDefault()
    const userId = event.target.dataset.userId
    axios({
      method: 'post',
      url: `/accounts/${userId}/follow/`,
      headers: {'X-CSRFToken': csrftoken,}
    })
      .then((response) => {
        const isFollowed = response.data.is_followed
        const followBtn = document.querySelector('#followBtn')
        const followersCountTag = document.querySelector('#followers-count')
        const followingsCountTag = document.querySelector('#followings-count')
        if (isFollowed === true) {
          followBtn.innerText = '언팔로우'
        } else {
          followBtn.innerText = '팔로우'
        }
        const followersCount = response.data.followers_count
        const followingsCount = response.data.followings_count
        followersCountTag.innerText = followersCount
        followingsCountTag.innerText = followingsCount
      })
  })
  </script>
{% endblock script %}
```

### 학습한 내용

- AJAX 통신을 이용하여 서버에서 데이터를 받아와 상황에 맞게 HTML 화면을 구성하는 법

### 어려웠던 부분 

- AJAX 통신 그 자체를 이해하는 과정이 어려웠다.
- AJAX 비동기 처리를 하며, 팔로워 팔로우 인원 수 뿐만이 아닌 유저들 정보도 얻어오고 싶었는데,
  쿼리셋을 json으로 전달할 수 없다는 오류를 해결하지 못하였다.
- AJAX랑 view랑 template 데이터를 주고 받는 방법이 어려웠다.

### 느낀 점

- 공부를 전체적으로 한 번 훑듯이 해야되겠다.
- Ajax통신을 공부해야겠다.





## B. 리뷰 좋아요 기능

![image-20221104175223883](heeje.assets/image-20221104175223883.png)

### view.py

```python
@require_POST
def like(request, review_pk):
    if request.user.is_authenticated:
        review = Review.objects.get(pk=review_pk)#get_object_or_404(Review, pk=review_pk)
        user = request.user

        if review.like_users.filter(pk=user.pk).exists():
            review.like_users.remove(user)
            is_liked = False
        else:
            review.like_users.add(user)
            is_liked = True
        context = {
            'is_liked': is_liked,
            'likes_count': review.like_users.count(),
        }
        return JsonResponse(context)
        #return redirect('community:index')
    return redirect('accounts:login')
```





### templates/community/index.html

```django
{% extends 'base.html' %}

{% block content %}
  <h1 class="fw-bold">Community</h1>
  <hr>
  {% for review in reviews %}
    <p>작성자 : <a href="{% url 'accounts:profile' review.user.username %}">{{ review.user }}</a></p>
    <p>글 번호: {{ review.pk }}</p>
    <p>글 제목: {{ review.title }}</p>
    <p>글 내용: {{ review.content }}</p>
    <form class="like-forms" data-review-id="{{ review.pk }}">
      {% csrf_token %}
      {% if user in review.like_users.all %}
        <input  type="submit"  id="like-{{ review.pk }}" value="좋아요 취소"/>
      {% else %}
        <input  type="submit"  id="like-{{ review.pk }}" value="좋아요"/>
      {% endif %}
    </form>
    <p>
      <span id="likes-{{ review.pk }}">{{ review.like_users.all|length }}</span> 명이 이 글을 좋아합니다.
    </p>
    <a href="{% url 'community:detail' review.pk %}">[detail]</a>
    <hr>
  {% endfor %}
{% endblock %}

{% block script %}
<script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
<script>
  const forms = document.querySelectorAll('.like-forms')
  const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value
  forms.forEach((form) => {
    form.addEventListener('submit', function (event){
      event.preventDefault()
      const reviewId = event.target.dataset.reviewId

      axios({
        method:"post",
        url:`/community/${reviewId}/like/`,
        headers: {'X-CSRFToken': csrftoken,}
      })
        .then((response)=>{
          const isLiked = response.data.is_liked
          const likeBtn = document.querySelector(`#like-${reviewId}`)
          if (isLiked === true) {
            likeBtn.value = '좋아요 취소'
          } else {
            likeBtn.value = '좋아요'
          }
          const likesCountTag = document.querySelector(`#likes-${reviewId}`)
          const likesCount = response.data.likes_count
          likesCountTag.innerText = likesCount
        })
    })
  })
</script>
{% endblock script %}
```

### 학습한 내용

- AJAX 통신을 이용하여 서버에서 데이터를 받아와 상황에 맞게 HTML 화면을 구성하는 법

### 어려웠던 부분 

- AJAX 통신 그 자체를 이해하는 과정이 어려웠다.
- AJAX랑 view랑 template 데이터를 주고 받는 방법이 어려웠다.
- 여러개 버튼을 동시에 넣는 것이 어려웠다.

### 느낀 점

- 공부를 전체적으로 한 번 훑듯이 해야되겠다.
- Ajax통신을 공부해야겠다.