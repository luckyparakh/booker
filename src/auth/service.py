from .schema import UserSchema
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from .models import User
from .utils import get_password_hash


class UserService:
    async def get_user_by_email(self, email: str, session: AsyncSession):
        statement = select(User).where(User.email == email)
        result = await session.exec(statement)
        user = result.first()
        return user

    async def create_user(self, user: UserSchema, session: AsyncSession):
        data = user.model_dump()
        new_user = User(**data)
        print("*************", new_user )
        new_user.password_hash = get_password_hash(data["password"])
        print("*************", new_user )
        session.add(new_user)
        await session.commit()
        return new_user
