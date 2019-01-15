import factory
import random
import faker

from posts.models import Post

class PostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Post
        
    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """
        Need some randomness in the body length that is difficult
        to provide in a class level variable. I.e. when random.randint
        is called in the aguements to factory.Faker() it is only
        called once.
        """
        fake = faker.Faker()
        kwargs['body'] = fake.text(max_nb_chars = random.randint(0, 2000))
        return super()._create(model_class, *args, **kwargs)
        
    title = factory.Faker(
        'paragraph',
        nb_sentences=1,
        variable_nb_sentences=True
    )
