from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
serviceURL = Table('serviceURL', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('service_description', String(length=100)),
    Column('service_name', String(length=20)),
    Column('service_URL', String(length=75)),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['serviceURL'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['serviceURL'].drop()
