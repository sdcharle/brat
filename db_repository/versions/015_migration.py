from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
user = Table('user', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('nickname', VARCHAR(length=64)),
    Column('email', VARCHAR(length=120)),
    Column('role', SMALLINT),
    Column('first_name', VARCHAR(length=24)),
    Column('last_name', VARCHAR(length=50)),
    Column('rfid_access', BOOLEAN),
    Column('rfid_tag', VARCHAR(length=20)),
    Column('username', VARCHAR(length=64)),
    Column('rfid_description', VARCHAR(length=50)),
    Column('about_me', VARCHAR(length=140)),
    Column('last_seen', DATETIME),
    Column('language', VARCHAR(length=5)),
    Column('is_active', BOOLEAN),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['user'].columns['username'].drop()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['user'].columns['username'].create()
