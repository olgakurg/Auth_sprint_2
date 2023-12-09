import uuid

from sqlalchemy import Column, String, DateTime, ForeignKey, Table, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped, declarative_base

Base = declarative_base()

user_roles = Table('user_roles', Base.metadata,
                   Column('user_id', UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
                   Column('role_id', UUID(as_uuid=True), ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
                   )

role_permissions = Table('role_permissions', Base.metadata,
                         Column('role_id', UUID(as_uuid=True), ForeignKey('roles.id', ondelete='CASCADE'),
                                primary_key=True),
                         Column('permission_id', UUID(as_uuid=True), ForeignKey('permissions.id', ondelete='CASCADE'),
                                primary_key=True),
                         )


class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    login = Column(String(255), unique=True, nullable=False)
    password = Column(String(255))
    name = Column(String(255))
    roles = relationship('Role', secondary=user_roles, backref='users')
    sessions = relationship('UserSession')
    users_idx = Index('users_idx', id, unique=True)


class Role(Base):
    __tablename__ = 'roles'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = Column(String(255))
    description = Column(String)
    permissions: Mapped[list['Permission']] = relationship('Permission', secondary=role_permissions,
                                                           back_populates='roles')


class Permission(Base):
    __tablename__ = 'permissions'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = Column(String(255))
    roles: Mapped[list['Role']] = relationship('Role', secondary=role_permissions, back_populates='permissions')


class UserSession(Base):
    __tablename__ = 'user_sessions'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'))
    auth_date = Column(DateTime)
    last_date = Column(DateTime)
    creation_date = Column(DateTime)
    user_sessions_idx = Index('user_sessions_idx', user_id)
    sessions_idx = Index('sessions_idx', id)
