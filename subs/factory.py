import factory
import random
import faker

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
    def get_description(cls, fake):
        description = fake.sentences(nb=random.randint(1,10))
        return " ".join(description)
    
    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """
        Need to perform some custom changes to Faker outputs
        and some complex relationships
        """
        fake = faker.Faker()
        kwargs['title'] = cls.slug_to_title(kwargs['title'])
        kwargs['description'] = cls.get_description(fake)
        return super()._create(model_class, *args, **kwargs)
        
    title = factory.Faker('slug')
    
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
    
    
    
    
    
        
