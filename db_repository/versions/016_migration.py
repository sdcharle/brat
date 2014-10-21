from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
access_event = Table('access_event', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('rfid_tag', String(length=20)),
    Column('user_id', Integer),
    Column('event_date', DateTime),
    Column('access_granted', Boolean, default=ColumnDefault(False)),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['access_event'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['access_event'].drop()
