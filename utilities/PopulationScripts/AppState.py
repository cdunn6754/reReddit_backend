import requests
from constants import (
    API_USER_URL, API_USER_LOGIN_URL, API_SUB_URL,
    API_POST_URL, API_COMMENT_URL,
)
class AppState:
    def __init__(self):
        # List of users created, list of dictionaries with
        # serialized user data plus the auth token with key 'token'
        self.users = []
        # List of subreddits created, serialized sub data
        self.subreddits = []
        # # List of posts created, list of post ids
        self.posts = []
        # List of comments, they are stored as a 2-tuple (id, post_title)
        self.comments = []
        
        # Get the users and subreddits currently in the database
        self.get_users()
        self.get_subreddits()
        self.get_posts()
        self.get_comments()
    
    def get_users(self):
        """
        Get the list of current users from api, log every user in and
        return a list of 2-tuples (username, token)
        """
        print("\nReading users currently in database")
        print("--------------------------------------")
        res = requests.get(API_USER_URL)
        for user in res.json():
            username = user['username']
            credentials = {'username': username,
                           'password': self.password}
            # try because there are a few users that may not have the default
            # password, self.password
            try:
                auth_res = requests.post(API_USER_LOGIN_URL,json=credentials)
                auth_res.raise_for_status()
                user['token'] = auth_res.json()['token']
                self.users.append(user)
            except requests.exceptions.HTTPError:
                print("User: {} excluded from processing".format(username))
        
        print("{} users read from database successfully and"
              " logged in".format(len(self.users)))
              
    def get_subreddits(self):
        """
        Read the subreddits that exists in the database into our
        self.subreddits list, each entry is just the subreddit title.
        """
        print("\nReading subreddits currently in database")
        print("-------------------------------------------")
        res = requests.get(API_SUB_URL)
        self.subreddits.extend(res.json())
        print("{} subreddits read from database"
              " successfully".format(len(res.json())))
              
    def get_posts(self):
        """
        Read the posts that are currently in the database and
        store them in the self.posts list
        """
        print("\nReading posts currently in database")
        print("---------------------------------------")
    
        res = requests.get(API_POST_URL)
        self.posts.extend(res.json())
            
        print("{} posts read from database successfully".format(
            len(res.json()))
        )
    def get_comments(self):
        """
        Read the comments from the database and store them in self.comments
        list
        """
        print("\nReading posts currently in database")
        print("---------------------------------------")
        
        res = requests.get(API_COMMENT_URL)
        self.comments.extend(res.json())

        print("{} comments read from database successfully".format(
            len(res.json()))
        )
        
if __name__ == '__main__':
    p = AppState()
