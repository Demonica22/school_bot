from data.db_session import *
from data.__all_models import *

global_init('db\\data.sqlite')

session = create_session()
admin = Users()
admin.email = 'admin@admin'
admin.name = 'admin'
admin.surname = 'admin'
admin.password = '1bcda042231074a95b5f23f8c09b936acedc8bace722f1d0202e5ea6f8287f02:4751e4c77eb640e990a6c753b814ff35'
admin.role_id = 2

roles = Roles()
roles.id = 1
roles.name = 'user'

session.add(roles)

roles = Roles()
roles.id = 2
roles.name = 'admin'


session.add(admin)
session.add(roles)

session.commit()
