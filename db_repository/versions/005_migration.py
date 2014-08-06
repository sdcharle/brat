from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
user = Table('user', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('nickname', String(length=64)),
    Column('email', String(length=120)),
    Column('username', String(length=64)),
    Column('first_name', String(length=24)),
    Column('last_name', String(length=50)),
    Column('rfid_access', Boolean, default=ColumnDefault(False)),
    Column('rfid_tag', String(length=20)),
    Column('rfied_description', String(length=50)),
    Column('role', SmallInteger, default=ColumnDefault(0)),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['user'].columns['rfid_tag'].create()
    post_meta.tables['user'].columns['rfied_description'].create()
    post_meta.tables['user'].columns['username'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['user'].columns['rfid_tag'].drop()
    post_meta.tables['user'].columns['rfied_description'].drop()
    post_meta.tables['user'].columns['username'].drop()
