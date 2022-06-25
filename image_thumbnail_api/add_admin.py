from users.models import User
from users.models import Tier
enterprise_plan = Tier.objects.get(name='Enterprise')
User.objects.create_superuser(username='admin', password='admin', tier=enterprise_plan)
