import factory
import random
import faker

from comments.models import Comment

class CommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Comment
    
    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        fake = faker.Faker()
        kwargs['body'] = fake.text(max_nb_chars=random.randint(10,2500))
        return super()._create(model_class, *args, **kwargs)
