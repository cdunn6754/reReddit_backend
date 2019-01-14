import factory
import random

from subs.models import Sub
from redditors.models import User, UserSubMembership

class SubredditFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Sub
    
    @classmethod
    def slug_to_title(cls, slug):
        return ''.join([
            x for x in slug.replace("-", " ").title() if not x.isspace()
        ])
    @classmethod
    def modify_description(cls, description):
        return " ".join(description)
    
    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """
        Need to perform some custom changes to Faker outputs
        and some complex relationships
        """
        kwargs['title'] = cls.slug_to_title(kwargs['title'])
        kwargs['description'] = cls.modify_description(kwargs['description'])
        return super()._create(model_class, *args, **kwargs)
        
    title = factory.Faker('slug')
    description = factory.Faker('sentences', nb=random.randint(1,10))
    
    @factory.post_generation
    def moderators(self, create, extracted, **kwargs):
        
        if not create:
            return
            
        if extracted:
            for user in extracted:
                self.moderators.add(user)
                
class UserSubredditMembershipFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserSubMembership
    
    
    
    
    
        
