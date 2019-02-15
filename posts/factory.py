import factory
import random
import faker
from django.utils import timezone

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
        called once and is therefore a single number for all
        posts created in the current command.
        """
        fake = faker.Faker()
        body_length = max(
            round(random.betavariate(1.2, 3)*2000),
            10
        )
        kwargs['body'] = fake.text(body_length)
        return super()._create(model_class, *args, **kwargs)
        
    title = factory.Faker(
        'paragraph',
        nb_sentences=1,
        variable_nb_sentences=True
    )
    created = factory.Faker(
        'date_time_between',
        start_date="-1y",
        end_date="now",
        tzinfo=timezone.utc
    )
    updated = created
