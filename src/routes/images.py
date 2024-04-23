from typing import Optional, List

from fastapi import UploadFile, APIRouter, HTTPException, status, Depends, File, Response, Form, Query, Path
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import FileResponse

from src.database.db import get_db
from src.models.models import Image, User
from src.conf.config import settings
from src.services.auth import auth_service
from src.schemas.images import ImageCreateSchema, ImageReadSchema
from src.repository import images as repository_images

router = APIRouter(prefix='/images', tags=['image'])


@router.get('/tag', response_model=List[ImageReadSchema])
async def get_images_by_tag(tag_name: str = Query(description="Input tag", min_length=3, max_length=50),
                            limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
                            db: AsyncSession = Depends(get_db)):
    images = await repository_images.get_images_by_tag(tag_name, limit, offset, db)
    if not images:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="TAG NOT EXISTS")
    return images


@router.post('/add_tag/{image_id}', response_model=ImageReadSchema)
async def add_tag_to_image(image_id: int = Path(ge=1),
                           tag_name: str = Query(description="Input tag", min_length=3, max_length=50),
                           db: AsyncSession = Depends(get_db)):

    result = await repository_images.add_tag_to_image(image_id, tag_name, db)
    if not result:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                            detail=f"Max tags to add to image reached {settings.max_add_tags}")
    return result


@router.get('/all', response_model=List[ImageReadSchema])
async def get_images(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
                     db: AsyncSession = Depends(get_db)):
    query = select(Image).offset(offset).limit(limit)
    images = await repository_images.get_images(query, db)
    if not images:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return images


@router.post("/upload", response_model=ImageReadSchema, status_code=status.HTTP_201_CREATED)
async def upload_image(file: UploadFile = File(..., description="The image file to upload"),
                       title: str = Form(min_length=3, max_length=50),
                       tag: Optional[str] = None,
                       user: User = Depends(auth_service.get_current_user),
                       db: AsyncSession = Depends(get_db)):
    new_name = await repository_images.format_filename(file)
    size_is_valid = await repository_images.get_file_size(file)
    file_is_valid = await repository_images.file_is_image(file)
    if size_is_valid > settings.max_image_size:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            detail=f"File too large. Max size is {settings.max_image_size} bytes")
    if not file_is_valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"File is not an image. Only images are allowed")
    file_path = await repository_images.save_file_to_uploads(file, new_name)

    image = await repository_images.create_upload_image(name=new_name, size=size_is_valid, mime_type=file.content_type,
                                                        file_path=file_path, title=title,
                                                        tag=tag, user=user, db=db)

    return image


@router.get('/download/{image_id}', status_code=status.HTTP_200_OK)
async def download_image(image_id: int = Path(ge=1), db: AsyncSession = Depends(get_db)):
    query = select(Image).filter_by(id=image_id)
    image = await repository_images.get_image(query, db)
    if image:
        return FileResponse(image.image_path, media_type="image/png", filename=image.name)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")


@router.delete('/delete/{image_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_image(image_id: int = Path(ge=1),
                       user: User = Depends(auth_service.get_current_user),
                       db: AsyncSession = Depends(get_db)):
    query = select(Image).filter_by(id=image_id).filter_by(owner_id=user.id)
    image = await repository_images.get_image(query, db)
    if image:
        # Delete image from DB
        await repository_images.delete_image_from_db(image, db)
        # Delete file from uploads
        await repository_images.delete_image_from_uploads(image.name)
        return {'ditail': f'File {image.name} successfully deleted'}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")


@router.put('/update/{image_id}', response_model=ImageReadSchema, status_code=status.HTTP_200_OK)
async def update_image(image_id: int = Path(ge=1),
                       title: str = Form(min_length=3, max_length=50),
                       user: User = Depends(auth_service.get_current_user),
                       db: AsyncSession = Depends(get_db)):
    query = select(Image).filter_by(id=image_id).filter_by(owner_id=user.id)
    image = await repository_images.get_image(query, db)
    if image:
        image = await repository_images.update_image_title(image, title, user, db)
        return image
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")


@router.get('/', response_model=list[ImageReadSchema])
async def get_images_by_user(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
                             db: AsyncSession = Depends(get_db),
                             user: User = Depends(auth_service.get_current_user)):
    query = select(Image).filter_by(owner_id=user.id).offset(offset).limit(limit)
    images = await repository_images.get_images(query, db)
    if not images:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return images
