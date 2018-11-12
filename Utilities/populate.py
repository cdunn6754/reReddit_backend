import os
import sys
from faker import Faker
import requests
import numpy as np
import json
import random

from constants import (API_SUB_URL, API_USER_CREATE_URL, API_USER_LOGIN_URL)

class Populate:    
    def __init__(self):
        # Number of subs and users to make
        self.n_users = 2
        self.n_subs = 3
        # Number of members per sub and mods per subs
        # These are the mean of a normal distribution not hard numbers
        self.mem_per_sub = 25
        self.mod_per_sub = 3
        
        # Faker instance for names, post text, ...
        self.fake = Faker()
        
        # List of users created, list contains tuple of (username, token)
        self.users = []
        # List of subs created, list of sub titles
        self.subs = []
    
    def populate(self):
        """
        Call the various population functions that make api calls
        """
        print("Populating Database:")
        print("######################\n")
        
        self.add_users(self.n_users)
        self.add_subs(self.n_subs)
        self.add_members(self.mem_per_sub)
        
    def add_users(self, n_users=0):
        print("Adding {} users to database:".format(n_users))
        print("----------------------------\n")
    
        for u in range(n_users):
            username = self.fake.user_name()
            # check if we already added one with this name
            while username in self.users:
                username = username + str(9)
            password = 'testPassword'
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
            except requests.HTTPError as e:
                print(e)
                print(res.text)
                
    def add_members(self, n_mems=0):
        """
        Assuming we have users and subs created. Now subscribe some of those
        users to the subs. n_mems is the mean number of members 
        (i.e. subscriptions) for each sub. 
        """
        
        # Normal distribution random number of members to add
        to_add = np.random.normal(n_mems, n_mems/3, len(self.subs)).as_type(int)        
        
        for idx,sub in enumerate(self.subs):
            users = random.sample(self.users, to_add[idx])
            for user in users:
                pass
        
        

                
if __name__ == '__main__':
    p = Populate()
    
    p.populate()