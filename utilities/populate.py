import os
import sys
from faker import Faker
import requests
import numpy as np
import json
import random

from constants import (API_SUB_URL, API_USER_CREATE_URL, API_USER_LOGIN_URL,
                       API_USER_URL, API_SUB_SUBSCRIBE_URL_, API_POST_URL,
                       API_COMMENT_URL,)

"""
TODO: Break this monster into smaller classes. I think one logical
route could be to make a base class that reads things from the database, i.e.
posts, subs and users. Then a subclass could handle the addition of new
instances when needed.
"""

class Populate:
    def __init__(self):
        # Number of subs and users to make
        self.n_users = 2
        self.n_subs = 3
        # Number of members per sub and mods per subs
        # These are the mean of a normal distribution not hard numbers
        self.mem_per_sub = 25
        self.mod_per_sub = 3
        # Use the same password for all automatically create users
        self.password = 'testPassword'
        
        # Faker instance for names, post text, ...
        self.fake = Faker()
        
        # List of users created, list contains dict of (username, token)
        self.users = []
        # List of subs created, list of sub titles
        self.subs = []
        # # List of posts created, list of post ids
        self.posts = []
        # List of comments, they are stored as a 2-tuple (id, post_title)
        self.comments = []
        
        # Get the users and subs currently in the database
        self.get_users()
        self.get_subs()
        self.get_posts()
        self.get_comments()
        
    def get_users(self):
        """
        Get the list of current users from api, use that to return a
        list of 2-tuples (username, token)
        """
        print("\nReading users currently in database")
        print("--------------------------------------")
        res = requests.get(API_USER_URL)
        for user in res.json():
            username = user['username']
            credentials = {'username': username,
                           'password': self.password}
            # try because there are a few users that may not have the default
            # password
            try:
                auth_res = requests.post(API_USER_LOGIN_URL,json=credentials)
                auth_res.raise_for_status()
                self.users.append((username, auth_res.json()['token']))
            except requests.exceptions.HTTPError:
                print("User: {} excluded from processing".format(username))
        
        print("{} users read from database successfully and"
              " logged in".format(len(self.users)))
              
    def get_subs(self):
        """
        Read the subreddits that exists in the database into our
        self.subs list, each entry is just the subreddit title.
        """
        print("\nReading subreddits currently in database")
        print("-------------------------------------------")
        res = requests.get(API_SUB_URL)
        for sub in res.json():
            title = sub['title']
            self.subs.append(title)
        print("{} subreddits read from database"
              " successfully".format(len(self.users)))
              
    def get_posts(self):
        """
        Read the posts that are currently in the database and
        store them in the self.posts list
        """
        print("\nReading posts currently in database")
        print("---------------------------------------")
    
        res = requests.get(API_POST_URL)
        for post in res.json():
            self.posts.append((post["pk"]))
            
        print("{} posts read from database successfully".format(
            len(self.posts))
        )
    def get_comments(self):
        """
        Read the comments from the database and store them in self.comments
        list, they are stored as a 2-tuple (comment id, comment post title)
        """
        print("\nReading posts currently in database")
        print("---------------------------------------")
        
        res = requests.get(API_COMMENT_URL)
        for comment in res.json():
            self.comments.append((comment['pk'], comment['post'],))

        print("{} comments read from database successfully".format(
            len(self.comments))
        )
    
    def populate(self):
        """
        Call the various population functions that make api calls
        """
        print("Populating Database:")
        print("######################\n")
        
        self.add_users(self.n_users)
        self.add_subs(self.n_subs)
        
    def add_users(self, n_users=0):
        print("Adding {} users to database:".format(n_users))
        print("----------------------------\n")
    
        for u in range(n_users):
            username = self.fake.user_name()
            # check if we already added one with this name
            while username in self.users:
                username = username + str(9)
            password = self.password
            user_data = {'username': username,
                         'email': self.fake.email(),
                         'password': password}
                                      
            res = requests.post(API_USER_CREATE_URL, data=user_data)
            res.raise_for_status()
            print("User: {} added succesfully".format(username))
            # login and get token to form store user tuple
            token = self.user_login(user_data)
            self.users.append((username, token))
                
    def user_login(self, credentials):
        res = requests.post(API_USER_LOGIN_URL, json=credentials)
        res.raise_for_status()
        token = res.json()['token']
        return token
                
    def add_subs(self, n_subs=0):
        print("\n\nAdding {} subreddits to database:".format(n_subs))
        print("----------------------------\n")
        
        # Normal distribution random length
        desc_len = [int(l) for l in np.random.normal(100, 30, n_subs)]
        
        # TODO: we can make this faster by assinging the mods to the subs
        # before hand on the chance that a single user may be selected to
        # create/moderate more than one sub. Save some time on logging in
        # if we handle all of the subs for a given user at one time.
        # For now just iterate through and pick a random user each time.
        
        for s in range(n_subs):
            # Randomly select a User to be the creator and original moderator
            token = random.choice(self.users)[1]
            
            title = self.fake.slug()
            description = self.fake.text(max_nb_chars=max(desc_len[s],1))
            sub_data = {'title': title,
                        'description': description}
            
            header = {'Authorization': "Token {}".format(token)}
            try:
                res = requests.post(API_SUB_URL, headers=header, json=sub_data)
                res.raise_for_status()
                self.subs.append(title)
                print("Subreddit: {} added succesfully".format(title))
            except requests.HTTPError as e:
                print(e)
                print(res.text)
                
    def add_members(self, n_mems=20):
        """
        n_mems is the mean number of members (i.e. subscriptions) for each sub.
        A random number of randomly selected users are subscribed to each sub.
        n_mems only indicates the mean of a normal distribution, not a
        deterministic value.
        """
        print("\nSubscribing users to subreddits")
        print("--------------------------------")
        
        # Normal distribution random number of members to add
        to_add = np.random.normal(n_mems, n_mems/5, len(self.subs)).astype(int)
        
        new_memberships = 0
        
        for idx,sub in enumerate(self.subs):
            user_sample_size = min(max(to_add[idx],0), len(self.users))
            users = random.sample(self.users, user_sample_size)
            for user in users:
                header = {"Authorization": "Token {}".format(user[1])}
                try:
                    res = requests.post(API_SUB_SUBSCRIBE_URL_(sub),
                                        headers=header,
                                        json={"action": "sub"})
                    res.raise_for_status()
                except requests.HTTPError as e:
                    print(res.json()['detail'])
                    exit()
                    
                new_memberships += 1
        print("{} users memberships created".format(new_memberships))
        
    def add_posts(self, n_per_user=20):
        """
        Add fake posts in subreddits. n_per_user is the mean of a normal
        distribution, so the number of posts actually added by each
        user is random. Those are added to random subreddits
        """
        print("\nPosting to subreddits")
        print("------------------------")
        
        n_posts_added = 0
                
        # for each user get random number of posts to add
        n_to_add = np.random.normal(n_per_user, n_per_user/3,
                                    len(self.users)).astype(int)
        
        for idx,user_data in enumerate(self.users):
            # Log in user to get the list of subreddits to which they subscribe
            username = user_data[0]
            login_data = {'username': username,
                          'password': self.password}
            res = requests.post(API_USER_LOGIN_URL, json = login_data)
            # this will be a list of dicts with subreddit info
            member_subs = res.json()['subs']
            # random sub for each post by this user
            subs = np.random.choice(member_subs, max(n_to_add[idx],0))
            for sub_dict in subs:
                length_of_title = max(np.random.normal(10,6), 1)
                post_title = self.fake.sentence(nb_words=13,
                                               variable_nb_words=True)
                post_body = self.fake.text(max_nb_chars=150)
                header = {'Authorization': 'Token {}'.format(user_data[1])}
                data = {'title': post_title,
                        'body': post_body}
                try:
                    res = requests.post(sub_dict['url'] + 'post/',
                                  headers=header,
                                  json=data)
                    res.raise_for_status()
                    n_posts_added += 1
                except requests.HTTPError as e:
                    print(e)
                    print(res.json())
                    exit()
            print("{} posts added by user: {}".format(n_posts_added, username))
        
    def add_root_comments(self, n_per_user=5, comment_length=50):
        """
        Add fake comments to random posts. Again n_per_user is a mean
        of a normal distribution from which each user is assigned a random
        number of comments to make. For now users need not be subscribed to
        a particlular subreddit to comment on posts made there so it pretty
        random now.
        
        Here we are only creating root comments, that is, comments without
        a parent.
        
        comment_length is the mean length of each comment in chars.
        """
        
        print("\nGenerating root comments")
        print("------------------------")
        n_comments_added = 0
        
        # Generate random number of comments for each user to create
        n_to_add = np.random.normal(
            n_per_user,
            n_per_user/2,
            len(self.users)
        ).astype(int)
        
        for idx, user_data in enumerate(self.users):
            # Choose a random post and comment
            posts = np.random.choice(self.posts, max(n_to_add[idx], 0))
            for post_pk in posts:
                nb = random.randint(0,10)
                body = (
                    self.fake.paragraph(nb_sentences=nb) +
                    self.fake.sentence(nb_words=nb+1)
                )
                upvotes = random.randint(1,500)
                header = {'Authorization': 'Token {}'.format(user_data[1])}
                data = {
                    'body': body,
                    'upvotes': upvotes,
                    'poster': user_data[0],
                    'parent_fn': "t2_{}".format(post_pk),
                }
                try:
                    res = requests.post(API_COMMENT_URL,
                        headers=header,
                        json=data
                    )
                    res.raise_for_status()
                    n_comments_added +=1
                except requests.HTTPError as e:
                    print(e)
                    print(res.json())
                    exit()
        print("{} root comments added".format(n_comments_added))
    
    def add_child_comments(self, n_per_user=10, comment_length=50):
        """
        Add fake comments to random posts. Again n_per_user is a mean
        of a normal distribution from which each user is assigned a random
        number of comments to make. For now users need not be subscribed to
        a particlular subreddit to comment on posts made there so it pretty
        random now.
        
        Here we are creating child comments that will all have a parent.
        The parents of a particular comment are seleted by randomly choosing
        a comment from self.comments.
        
        comment_length is the mean length of each comment in chars.
        """
        
        print("\nGenerating child comments")
        print("------------------------")
        n_comments_added = 0
        
        # Generate random number of comments for each user to create
        n_to_add = np.random.normal(
            n_per_user,
            n_per_user/2,
            len(self.users)
        ).astype(int)
        
        for idx, user_data in enumerate(self.users):
            
            # randomize the comment size a little
            nb = random.randint(0,10)
            body = (
                self.fake.paragraph(nb_sentences=nb) +
                self.fake.sentence(nb_words=nb+1)
            )
            upvotes = random.randint(1,500)
            idx = np.random.choice(len(self.comments))
            parent_comment = self.comments[idx]
            header = {'Authorization': 'Token {}'.format(user_data[1])}
            data = {
                'body': body,
                'upvotes': upvotes,
                'poster': user_data[0],
                'parent_fn': "t1_{}".format(parent_comment[0])
            }
            try:
                res = requests.post(API_COMMENT_URL,
                    headers=header,
                    json=data
                )
                res.raise_for_status()
                n_comments_added +=1
            except requests.HTTPError as e:
                print(e)
                print(res.json())
                exit()
        print("{} child comments added".format(n_comments_added))
        
                
if __name__ == '__main__':
    p = Populate()
    
    p.add_root_comments(5)
    p.add_child_comments(5)
    p.add_child_comments(5)
