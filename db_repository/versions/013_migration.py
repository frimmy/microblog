from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
projects = Table('projects', pre_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('user_id', Integer),
    Column('title', String),
    Column('description', String),
    Column('git_hub_link', String),
    Column('demo_link', String),
    Column('screen_shot', String),
)

project = Table('project', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('user_id', Integer),
    Column('title', String(length=30)),
    Column('description', String(length=140)),
    Column('git_hub_link', String(length=255)),
    Column('demo_link', String(length=255)),
    Column('screen_shot', String(length=255)),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['projects'].drop()
    post_meta.tables['project'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['projects'].create()
    post_meta.tables['project'].drop()
