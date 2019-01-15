from faker import Faker
import requests
import numpy as np
import json
import random

import AppState
from ...redditors.models import User
from ...redditors.serializers import UserSerializer
from ...subs.models import Sub
from ...subs.serializers import SubSerializer

class Populate:
    def __init__(self):
        self.state = AppState()

        # Use the same password for all automatically create users
        self.password = 'testPassword'
        
        # Faker instance for names, post text, ...
        self.fake = Faker()
        
    def user_login(self, credentials):
        res = requests.post(API_USER_LOGIN_URL, json=credentials)
        res.raise_for_status()
        token = res.json()['token']
        return token
        
    def add_users(self, n_users=1):
        print("Adding {} users to database:".format(n_users))
        print("----------------------------\n")
        
        for u in range(n_users):
            username = self.fake.user_name()
            # check if we already added one with this name
            while username in self.users:
                username = username + str(9)
            password = self.password
            credentials = {'username': username,
                            'email': self.fake.email(),
                            'password': password
                          }
            res = requests.post(API_USER_CREATE_URL, data=credentials)
            res.raise_for_status()
            user_data = UserSerializer(User.objects.get(username=username))
            user_data["token"] = self.user_login(user_data)
            print("User: {} added succesfully".format(username))
            self.state.users.append(user_data)
            
    def fakeDescription(self):
        n_sentences = random.randint(1,10)
        return " ".join(fake.sentences(nb=n_sentences))
        
    def fakeTitle(self):
        slug = faker.slug()
        return ''.join([
            x for x in slug.replace("-", " ").title() if not x.isspace()
        ])
            
    def add_subreddits(self, n_subreddits=1):
        print("\n\nAdding {} subreddits to database:".format(n_subreddits))
        print("----------------------------\n")
        
        for subreddit in n_subreddits:
            # Randomly select a User to be the creator and original moderator
            token = random.choice(self.state.users)['token']
            
            title = self.fake.Title
            description = self.fakeDescription
            sub_data = {'title': title,
                        'description': description}
            
            header = {'Authorization': "Token {}".format(token)}
            try:
                res = requests.post(API_SUB_URL, headers=header, json=sub_data)
                res.raise_for_status()
                self.state.subreddits.append(
                    SubSerializer(Sub.objects.get(title=title)).data
                )
                print("Subreddit: {} added succesfully".format(title))
            except requests.HTTPError as e:
                print(e)
                print(res.text)

if __name__ == '__main__':
    p = Populate()
    p.add_users()
