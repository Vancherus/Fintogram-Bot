from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Tuple
from database.models import User, ThoughtForm, Transfer

##################### User #####################################

async def orm_add_user(session: AsyncSession, user_id: int, username: str | None = None) -> None:
    query = select(User).where(User.id == user_id)
    result = await session.execute(query)
    user = result.scalar_one_or_none()
    
    if user is None:
        session.add(User(id=user_id, username=username))
        await session.commit()

async def orm_get_user(session: AsyncSession, user_id: int) -> User | None:
    result = await session.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


##################### ThoughtForm #####################################

async def orm_add_thought(session: AsyncSession, sender_id: int, idea: str) -> ThoughtForm:
    thought = ThoughtForm(owner_id=sender_id, content=idea)
    session.add(thought)
    await session.commit()
    await session.refresh(thought)
    return thought


async def orm_get_user_thoughts(session: AsyncSession, user_id: int) -> list[ThoughtForm]:
    result = await session.execute(
        select(ThoughtForm)
        .where(ThoughtForm.owner_id == user_id)
        .order_by(ThoughtForm.created.desc())
    )
    return list(result.scalars().all()) 

async def orm_delete_thought(session: AsyncSession, thought_id: str, user_id: int) -> bool:
    stmt = delete(ThoughtForm).where(ThoughtForm.id == thought_id, ThoughtForm.owner_id == user_id)
    result = await session.execute(stmt)
    await session.commit()
    return result.rowcount > 0  # will return True if something was deleted


##################### Transfer #####################################

async def orm_get_user_by_username(session: AsyncSession, username: str):
    stmt = select(User).where(User.username == username)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()

async def orm_transfer_thought(
    session: AsyncSession,
    thought_id: str,
    sender_id: int,
    receiver_username: str,
) -> Tuple[Transfer, ThoughtForm]:
    # 1. find original thoughtform
    stmt = select(ThoughtForm).where(ThoughtForm.id == thought_id)
    result = await session.execute(stmt)
    original_thought = result.scalar_one_or_none()

    if not original_thought:
        raise ValueError("Мыслеформа не найдена")

    # 2. Find recipient ID by username
    stmt = select(User).where(User.username == receiver_username)
    result = await session.execute(stmt)
    receiver = result.scalar_one_or_none()

    if not receiver:
        raise ValueError("Получатель не зарегистрирован")

    # 3. Clone a thought form
    new_thought = ThoughtForm(
        content=original_thought.content,
        owner_id=receiver.id
    )
    session.add(new_thought)

    # 4. Create a transfer record
    transfer = Transfer(
        thoughtform_id=thought_id,
        sender_id=sender_id,
        receiver_username=receiver_username,
    )
    session.add(transfer)

    # 5. save all
    await session.commit()
    await session.refresh(transfer)

    return transfer, new_thought


async def orm_get_incoming_thoughts(session: AsyncSession, username: str) -> list[ThoughtForm]:
    result = await session.execute(
        select(ThoughtForm)
        .join(Transfer, Transfer.thoughtform_id == ThoughtForm.id)
        .where(Transfer.receiver_username == username)
        .order_by(Transfer.created.desc())
    )
    return list(result.scalars().all())

async def orm_get_thought_by_id(session: AsyncSession, thought_id: str) -> ThoughtForm | None:
    result = await session.execute(
        select(ThoughtForm).where(ThoughtForm.id == thought_id)
    )
    return result.scalar_one_or_none()

# check to avoid duplicate transmissions of the same thought form
# that is, to ensure that we send only one thought form with a specific ID to a specific user
async def has_been_transferred(session: AsyncSession, thoughtform_id: str, receiver_username: str) -> bool: 
    result = await session.execute(
        select(Transfer).where(
            Transfer.thoughtform_id == thoughtform_id,
            Transfer.receiver_username == receiver_username
        )
    )
    return result.scalar_one_or_none() is not None


