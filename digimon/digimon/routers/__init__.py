from . import root
from . import users
from . import items
from . import merchants
from . import wallets
from . import authentication
from . import transaction


def init_router(app):
    app.include_router(root.router)
    app.include_router(users.router)
    app.include_router(authentication.router)
    app.include_router(items.router)
    app.include_router(merchants.router)
    app.include_router(wallets.router)
    app.include_router(transaction.router)
