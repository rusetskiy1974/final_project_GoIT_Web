import os
from datetime import datetime
from pathlib import Path
from uuid import uuid4

import cloudinary
import cloudinary.uploader
from fastapi import UploadFile
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.models import Image, Tag, User
from src.conf.config import settings
from src.schemas.images import ImageCreateSchema


async def get_image(query, db: AsyncSession):
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_images(query, db: AsyncSession):
    images = await db.execute(query)
    return images.scalars().all()


# Delete file from uploads folder
async def delete_image_from_uploads(file_name):
    try:
        os.remove(settings.uploaded_files_path + file_name)
    except Exception as e:
        print(e)


# Save file to uploads folder
async def save_file_to_uploads(file, filename):
    if not os.path.exists(settings.uploaded_files_path):
        os.makedirs(settings.uploaded_files_path)
    image_path = f'{settings.uploaded_files_path}{filename}'
    with open(image_path, "wb") as uploaded_file:
        file_content = await file.read()
        uploaded_file.write(file_content)
        uploaded_file.close()
    return image_path


# Get file size
async def get_file_size(file):
    file_content = await file.read()
    file_size = len(file_content)
    await file.seek(0)
    return file_size


async def file_is_image(file: UploadFile):
    if file.content_type.startswith('image'):
        return True
    else:
        return False


# Update File in DB
async def update_image_title(image: Image, title: str, user: User, db: AsyncSession):
    image.title = title
    await db.commit()
    await db.refresh(image)
    return image


#
#
# Delete image from DB
async def delete_image_from_db(image: Image, db: AsyncSession):
    await db.delete(image)
    await db.commit()


async def get_images_by_tag(tag_name: str, limit: int, offset: int, db: AsyncSession):
    query = select(Tag).filter_by(name=tag_name)
    tag = await db.execute(query)
    tag = tag.scalar_one_or_none()
    if tag:
        query = select(Image).filter(Image.tags.contains(tag)).offset(offset).limit(limit)
        images = await db.execute(query)
        return images.scalars().all()
    return


async def get_all_images(limit: int, offset: int, db: AsyncSession):
    query = select(Image).offset(offset).limit(limit)
    images = await db.execute(query)
    return images.scalars().all()


async def add_tag_to_image(image_id: int, tag_name: str, db: AsyncSession):
    tag = await create_tag(tag_name, db)
    image = await db.get(Image, image_id)
    db.add(image.tags.append(tag))
    # if image:
    #     image.count_tags += 1
    #     # image.tags_
    #     await db.commit()
    #     await db.refresh(image)
    #     return image
    # return


async def create_tag(tag_name, db: AsyncSession):
    query = select(Tag).filter_by(name=tag_name)
    tag = await db.execute(query)
    tag = tag.scalar_one_or_none()
    if tag is None:
        new_tag = Tag(name=tag_name)
        db.add(new_tag)
        await db.commit()
        await db.refresh(new_tag)
        return new_tag
    return tag


async def create_upload_image(tag: str | None, user: User, db: AsyncSession, **kwargs):
    data = ImageCreateSchema(name=kwargs['name'], size=kwargs['size'], mime_type=kwargs['mime_type'],
                             title=kwargs['title'], image_path=kwargs['file_path'])
    new_image = Image(**data.model_dump(exclude_unset=True), owner_id=user.id)

    if tag:
        tag = await create_tag(tag, db)
        new_image.count_tags = 1
        new_image.tags.append(tag)
    db.add(new_image)
    await db.commit()
    await db.refresh(new_image)
    return new_image


async def format_filename(file):
    filename, ext = os.path.splitext(file.filename)
    new_filename = f"{uuid4().hex}{ext}"
    return new_filename
