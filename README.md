# reReddit API:

This is the backend api for my reddit clone website, reReddit. It uses
the following tools and frameworks:
* [Django](https://www.djangoproject.com/)
* [Django Rest Framework](https://www.django-rest-framework.org/)
* [Django MPTT](https://django-mptt.readthedocs.io/en/latest/)
* [Django Cors Headers](https://github.com/ottoyiu/django-cors-headers)
* [PostgreSQL](https://www.postgresql.org/) (in deployment)
* [NGINX](https://www.nginx.com/) (in deployment)

I designed this project to mirror a limited set of the functionality of the
real reddit api based on their documentation as a portfolio project and
learning exercise. Aside from that this project is not associated with reddit.

A live browseable demo version of the api is available:
[rereddit.api.clintdunn.org](https://rereddit.api.clintdunn.org)

The other part of this project is a single page react app:
[reReddit_frontend](https://github.com/cdunn6754/reReddit_frontend)

## Installation:

It would be best to use a virtual environment from
[virtualenv](https://virtualenv.pypa.io/en/latest/). I also use the
[virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/).

Assuming you have them installed you can now create a new virtual env,
clone the project, and install the requirements. With Linux:

```
$ mkvirtualenv DRF
(DRF) $ git clone https://github.com/cdunn6754/reReddit_backend.git ~/reReddit
(DRF) $ cd ~/reReddit/reReddit_backend
(DRF) $ pip install -r requirements.txt
```
#### Using the provided database:
A dump from the default sqlite database is provided so that the site can be
run with data off the bat.
The default settings in `settings.py` were left to assume a sqlite database
would be used.
To set up the sqlite database with the data from the dump file on Linux run:
```
$ sqlite3 db.sqlite3 < db_dump.sql
```
After running that command to import the data you should be good to go.
A super user has been added to the database with the following credentials
* username: `reredditUser`
* password: `reredditUserPassword`

#### Populating a new database:
You don't need to use this database but the website is going to be pretty boring
without a significant amount of data.
If you would prefer not to use the provided db.sqlite database you can populate
your own with the custom management command that was written to populate the database
in the first place. Once you have set up and migrated your new database just run
```
$ python manage seed_database
```
This command calls several other commands included within each app of the project to create
users, subreddits, posts, comments, and comment/post votes. You can customize the database seeding
buy altering the seed_database.py file found in the core app or by calling the individual management
commands separately (see each app's managment folder).

#### Running the server
Whatever you decide regarding a databse you should be able to run the tests and start the development server
after installing the dependencies

```
(venv) $ python manage.py test
 ... Success hopefully
(venv) $ python manage.py runserver
```

Then you can visit the browseable api in yor browser at the usual
location, `localhost:8000`.

__NOTE:__ I used Python version 3.6.3 and pip version 19.0.1.

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

* __GET `/profile/{username}/` (auth optional)__
Unlike the other user resources this one is not concerned with the information
of the authenticated user. Instead this view can be used to get the profile,
i.e. the publicly available, information about any other user. In
reReddit_fontend this is used to populate the user profile view.
Unauthenticated requests will be accepted and return profile data.
If the request is from an authenticated user the posts and comments will contain
an accurate `vote_state` field that indicates the authenticated users previous
votes on the comment/post. The ordering of posts and comments is reverse
chronological.

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
  
### `/posts/`

* __GET `/posts/ (auth optional)`__
Retrieve a list of all posts. Authentication is optional in the same sense
as for the `/users/profile/{users}` field above. Authenticated responses
will contain a non-zero `vote_state` field if the authed user has voted on the
post previously.

* __GET `/posts/{pk}/`__
Retrieve the details of a single post.

* __DELETE `/posts/{pk}/`__
The owner or a moderator of the subreddit can delete a post.

* __GET `/posts/subreddit-list/{subreddit title}/` (auth optional)__
This endpoint allows a consumer to fetch all of the posts made on a
particular subreddit. The optional query parameter
is `orderby`, this can be used to specify the order in which the posts should
be returned.
Authentication is optional in and is used to provide information for the
`vote_state` field in the response, see `/users/profile/{users}`.
  * orderby: optional, must be either `popular` or `new`
  
 * __POST `/posts/create/{subreddit_title}/` (auth)__
Allows authenticated users to create posts to the subreddit. You must
already be a member of the subreddit, i.e. subscribed, to create a post.
  * title: the title of the new post
  * body: the body of the new post

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

* __GET `/comments/post/{post pk}` (auth optional)__
Retrieves all comments related to a particular post. The comments are returned
in a nested fashion with each primary entry being a root post comment. The
`orderby` optional query parameter can be used as described
in the `/posts/` section above.
Authentication is optional in and is used to provide information for the
`vote_state` field in the response, see `/users/profile/{users}`.
  * orderby: optional, must be either `popular` or `new`
  
### `/search/`

* __GET `/search/`__
A very simple search implementation that searches post titles, subreddit titles
and user usernames against a query parameter `q`. A separate
list of each entity type is returned in the response
  * q: the search parameter
