import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Text, VARCHAR, BIGINT, Index, DateTime, func
from sqlmodel import Field, SQLModel


class UserPayload(SQLModel, table=False):
	id: Optional[str] = Field(default_factory=uuid.uuid4, sa_column=Column(VARCHAR(255), primary_key=True))
	email: str = Field(unique=True, nullable=False, regex=r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$')
	nickname: Optional[str] = Field(nullable=True, default="")
	avatar: str = Field(nullable=True, default="https://cdn-icons-png.flaticon.com/512/1698/1698535.png")
	description: str = Field(nullable=True, default="天苍苍，野茫茫，风吹草低见牛羊。")
	total_requests: int = Field(default=10)
	"""文本总提问次数，默认免费10次"""
	used_requests: int = Field(default=0)
	"""文本已使用提问次数"""
	total_image_requests: int = Field(default=3)
	"""图片总提问次数，默认根据用户不同，免费次数不同，新注册及普通用户免费3次，高级用户和管理员用户免费10次"""
	used_image_requests: int = Field(default=0)
	"""图片已使用提问次数"""
	meta: Optional[str] = Field(sa_column=Column(Text(), nullable=True), default=None)
	is_feishu_user: bool = Field(default=False)
	"""使用飞书登录的用户"""
	is_github_user: bool = Field(default=False)
	"""使用github登录的用户"""
	type: Optional[str] = Field(default="normal")
	"""
	用户类型：
		1. normal:普通用户，可以使用ChatGPT 3.5
		2. premium:高级用户，可以使用ChatGPT 3.5 & ChatGPT 4
		3. admin:管理员用户，拥有高级用户的权限，并可以访问所有模块
		4. super_admin:超级管理员用户，拥有管理员用户的权限，并可以添加订阅 & 创建普通用户等能力
	"""
	model: Optional[str] = Field(default="gpt-3.5-turbo")


class UserBase(UserPayload, table=False):
	password: Optional[str] = Field(nullable=True)
	token: Optional[str] = Field(sa_column=Column(Text, nullable=True), default=None)
	"""jwt token，每次用户名密码登录后都会更新"""


class User(UserBase, table=True):
	__tablename__ = "user"


class RegisterUserPayload(UserBase):
	verification_code: int


class Prompt(SQLModel, table=True):
	__tablename__ = "prompt"

	id: Optional[str] = Field(default_factory=uuid.uuid4, sa_column=Column(VARCHAR(255), primary_key=True))
	icon: Optional[str] = Field(nullable=True)
	title: str = Field(nullable=True, unique=True)
	description: str = Field(sa_column=Column(Text, nullable=True))
	greetings: str = Field(sa_column=Column(Text, nullable=True))
	is_deleted: Optional[bool] = Field(default=False)
	is_enabled: Optional[bool] = Field(default=False)
	category: str = Field(nullable=True)
	likes: int = Field(default=0)


class ChatHistoryMeta(SQLModel, table=True):
	__tablename__ = "chat_history_meta"

	id: Optional[str] = Field(default_factory=uuid.uuid4, sa_column=Column(VARCHAR(255), primary_key=True))
	user_id: Optional[str] = Field(sa_column=Column(VARCHAR(255), nullable=True))
	knowledge_base_id: Optional[str] = Field(default=None, sa_column=Column(VARCHAR(255), nullable=True))
	"""新增 本地知识库 聊天时，从 KnowledgeBase 表更新过来。默认为null"""
	title: str = Field(nullable=True)
	uuid: int = Field(sa_column=Column(BIGINT, nullable=True))
	ai_mode: str = Field(nullable=True)
	icon: Optional[str] = Field(nullable=True)
	description: Optional[str] = Field(sa_column=Column(Text, nullable=True))
	greetings: Optional[str] = Field(nullable=True)
	meta: Optional[str] = Field(sa_column=Column(Text(), nullable=True), default=None)


class VectorDocRecord(SQLModel, table=True):
	__tablename__ = "vector_doc_record"
	__table_args__ = (Index('idx_filename', 'filename'),)

	id: Optional[str] = Field(default_factory=uuid.uuid4, sa_column=Column(VARCHAR(255), primary_key=True))
	filename: str = Field(nullable=True)
	doc_id: str = Field(nullable=True)
	knowledge_base_id: Optional[str] = Field(sa_column=Column(VARCHAR(255), nullable=True))
	"""知识库id，指定当前文档属于哪个知识库，上传文档时必须指定知识库 （目前作为文件名标识index_name的一部分或全部）"""


class KnowledgeBase(SQLModel, table=True):
	__tablename__ = "knowledge_base"

	id: Optional[str] = Field(default_factory=uuid.uuid4, sa_column=Column(VARCHAR(255), primary_key=True))
	"""此id既是user id区分不同用户，也作为当前知识库包含的向量数据库的名称使用"""
	user_id: Optional[str] = Field(sa_column=Column(VARCHAR(255)))
	name: str = Field(nullable=True, unique=True)
	icon: Optional[str] = Field(nullable=True)
	description: str = Field(sa_column=Column(Text, nullable=True))
	is_global: bool = Field(default=False)
	use_plugins: Optional[str] = Field(sa_column=Column(Text, nullable=True))
	type: Optional[str] = Field(nullable=True)
	"""knowledge base type: 1. localai"""
	created_at: Optional[datetime] = Field(default_factory=datetime.now,
																				 sa_column=Column(DateTime(timezone=True), server_default=func.now(),
																													nullable=False))
	updated_at: Optional[datetime] = Field(default_factory=datetime.now,
																				 sa_column=Column(DateTime(timezone=True), onupdate=func.now(), nullable=False))


class ActivePlugin(SQLModel, table=True):
	__tablename__ = "active_plugin"

	id: Optional[str] = Field(default_factory=uuid.uuid4, sa_column=Column(VARCHAR(255), primary_key=True))
	name: str = Field(nullable=True, unique=True)


class TextToImage(SQLModel, table=True):
	__tablename__ = "text_to_image"

	id: Optional[str] = Field(default_factory=uuid.uuid4, sa_column=Column(VARCHAR(255), primary_key=True))
	user_id: Optional[str] = Field(sa_column=Column(VARCHAR(255)))
	is_global: Optional[bool] = Field(default=False)
	query: Optional[str] = Field(sa_column=Column(Text, nullable=True))
	model: Optional[str] = Field(nullable=True)
	size: Optional[str] = Field(nullable=True)
	image_url: Optional[str] = Field(sa_column=Column(Text, nullable=True))
	created_at: Optional[datetime] = Field(default_factory=datetime.now,
																				 sa_column=Column(DateTime(timezone=True), server_default=func.now(),
																													nullable=False))
	updated_at: Optional[datetime] = Field(default_factory=datetime.now,
																				 sa_column=Column(DateTime(timezone=True), onupdate=func.now(), nullable=False))
