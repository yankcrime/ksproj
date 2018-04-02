from ksproj import config
from ksproj import identity

config.load_config()

c = identity.client()

t = c.identity.session.get_token()
u = identity.UserIdentity(token=t)
