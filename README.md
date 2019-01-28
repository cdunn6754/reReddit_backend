# reReddit API:

This is the backend api for my reddit clone website, reReddit. It uses
the following tools and frameworks:
* [Django](https://www.djangoproject.com/)
* [Django Rest Framework](https://www.django-rest-framework.org/)
* [Django MPTT](https://django-mptt.readthedocs.io/en/latest/)
* [Django Cors Headers](https://github.com/ottoyiu/django-cors-headers)
* [PostgreSQL](https://www.postgresql.org/)
* [NGINX](https://www.nginx.com/)

I designed this product to mirror a limited set of the functionality of the
real reddit api based on their documentation as a portfolio project and
learning exercise. Aside from that this project is not associated with reddit.

A live browseable demo version of the api is available:
[rereddit.api.clintdunn.org](https://rereddit.api.clintdunn.org)

## Documentation:

### `/users/`
* __GET `/users/`__
Retrieve a list of all users.

* __POST `/users/login/`__ Login a user.   
  * username
  * password

* __POST `/users/logout/` (auth)__
Logout a user.

* __POST `/users/create/`__
Create a new user, register.
  * username
  * password
  * email

* __GET `/users/{username}/`__
A detail view for the user with username

* __PATCH `/users/{username}/` (auth)__
Update the password or email for this user. The username can not be changed.
You must be authenticated as the user being updated to access this endpoint.
There is currently no email verification implemented.
  * email: optional, this is the updated email
  * new_password: optional
  * current_password

### `/subs/`
* __GET `/subs/`__
Retrieve a list of all subreddits.

* __GET `/subs/{title}/`__
Retrieve the details of a particular subreddit

* __POST `/subs/{title}/subscribe/` (auth)__
Subscribe to a subreddit. The `action` parameter describes whether you
would like to subscribe (`sub`) or unsubscribe (`unsub`). In both cases
the logical option must be selected or an error will result. E.g. if you
try to subscribe to a subreddit you are already a member a 400 error will
be returned
  * action: must be either `sub` or `unsub`

* __POST `/subs/{title}/post/` (auth)__
Allows authenticated users to create posts to the subreddit. You must
already be a member of the subreddit, i.e. subscribed, to create a post.
NOTE: In the future this view may be moved to the `/posts/` branch.
  * title: the title of the new post
  * body: the body of the new post
  
### `/posts/`

* __GET `/posts/`__
Retrieve a list of all posts. The optional query parameter `username` is
used to lookup the vote status of each post. The status of the users previous
voted will be indicated in the response.
  * username

* __GET `/posts/{pk}/`__
Retrieve the details of a single post.

* __GET `/posts/subreddit-list/{subreddit title}/`__
This endpoint allows a consumer to fetch all of the posts made on a
particular subreddit. There are two optional query parameters. The first
is `username`, for its use see the `/posts/{pk}/` documentation. The second
is `orderby`, this can be used to specify the order in which the posts should
be returned
  * username: optional
  * orderby: optional, must be either `popular` or `new`

### `/comments/`

* __GET `/comments/`__
Retrieve a list of all comments

* __POST `/comments/` (auth)__
Allows authenticated users to create a comment on either a post
or another comment. The `parent_fn` (full name, as used in the reddit api)
parameter is used to indicate both the type and identity of the parent to the
created comment. `parent_fn` can begin with either 't1_', to indicate that the
parent is anther comment, or 't2_' which means that the parent is a post and the
created comment is a root comment on that post. In either both cases
the prefix should be followed by the pk of the parent comment or post.
  * parent_fn
  * body: the body of the comment
  
* __GET `/comments/{pk}`__
Retrieve the details of a single comment.

* __PATCH `/comments/{pk}` (auth)__
Allows the poster to update the body of a comment. Must be authenticated
to edit a comment and must be the poster of the comment.
  * body: The updated comment body

* __DELETE `/comments/{pk}` (auth)__
Perform a customized delete on the comment. Must be authenticated and the
poster of the comment to delete. This does not remove the comment from the
database but will overwrite the body and poster fields. The comments are
preserved in this way to facilitate reddit-like comment display trees in the
front end.

* __GET `/comments/post/{post pk}`__
Retrieves all comments related to a particular post. The comments are returned
in a nested fashion with each primary entry being a root post comment. The
`username` and `orderby` optional query parameters can be used as described
in the `/posts/` section above.
  * username: optional
  * orderby: optional, must be either `popular` or `new`
  
### `/search/`

* __GET `/search/`__
A very simple search implementation that searches post titles, subreddit titles
and user usernames against a query parameter `q`. A separate
list of each entity type is returned in the response
  * q: the search parameter
