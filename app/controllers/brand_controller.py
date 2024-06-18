from fastapi import APIRouter, HTTPException, status, Security

from ..dependencies import get_oauth_scheme, get_current_user, databaseSession
from ..database import schemas, crud, tables
from ..services.brand import get_devices

oauth2_scheme = get_oauth_scheme()

router = APIRouter(
    prefix="/brands",
    tags=["brands"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


# APIs for brand.


# Get all brands.
@router.get("/")
async def get_brands(
        db: databaseSession,
        skip: int = 0,
        limit: int = 100,
        current_user: schemas.User = Security(get_current_user, scopes=["brand:list"]),
):
    brands = crud.select_all(db, tables.Brand, skip=skip, limit=limit)
    return brands


# Get all trashed brands.
# Reserved for admin.
@router.get("/trashed")
async def get_brands_trashed(
        db: databaseSession,
        skip: int = 0,
        limit: int = 100,
        current_user: schemas.User = Security(get_current_user, scopes=["brand:list", "trashed:list"]),
):
    brands = crud.select_all_with_trashed(db, tables.Brand, skip=skip, limit=limit)
    return brands


# Get brand by id.
@router.get("/{brand_id}")
async def get_brand(
        db: databaseSession,
        brand_id: int,
        current_user: schemas.User = Security(get_current_user, scopes=["brand:info"]),
):
    brand = crud.select_id(db, tables.Brand, brand_id)
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not exists",
        )
    return brand


# Get trashed brand by id.
# Reserved for admin.
@router.get("/{brand_id}/trashed")
async def get_brand(
        db: databaseSession,
        brand_id: int,
        current_user: schemas.User = Security(get_current_user, scopes=["brand:info", "trashed:info"]),
):
    brand = crud.select_id(db, tables.Brand, brand_id, with_trashed=True)
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not exists",
        )
    return brand


# Create brand.
@router.post("/")
async def create_brand(
        db: databaseSession,
        form_data: schemas.BrandCreateForm,
        current_user: schemas.User = Security(get_current_user, scopes=["brand:create"]),
):
    db_brand = crud.select_name(db, tables.Brand, form_data.name)
    if db_brand:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Brand already exists",
        )
    form_data.creator_id = current_user.id
    db_brand = crud.create(db, tables.Brand, form_data)
    return db_brand


# Update brand.
@router.put("/{brand_id}")
async def update_brand(
        db: databaseSession,
        brand_id: int,
        form_data: list[schemas.UpdateForm],
        current_user: schemas.User = Security(get_current_user, scopes=["brand:update"]),
):
    db_brand = crud.select_id(db, tables.Brand, brand_id)
    if not db_brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not exists",
        )
    db_brand = crud.update(db, tables.Brand, brand_id, form_data)
    return db_brand


# Delete brand.
@router.delete("/{brand_id}")
async def delete_brand(
        db: databaseSession,
        brand_id: int,
        current_user: schemas.User = Security(get_current_user, scopes=["brand:delete"]),
):
    db_brand = crud.select_id(db, tables.Brand, brand_id)
    if not db_brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not exists",
        )
    devices = get_devices(db, brand_id)
    if devices:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Brand has devices, please update devices first.",
        )
    db_brand = crud.delete(db, tables.Brand, brand_id)
    return db_brand


# Restore brand.
# Reserved for admin.
@router.put("/{brand_id}/restore")
async def restore_brand(
        db: databaseSession,
        brand_id: int,
        current_user: schemas.User = Security(get_current_user, scopes=["brand:update", "trashed:restore"]),
):
    db_brand = crud.select_id(db, tables.Brand, brand_id, with_trashed=True)
    if not db_brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not exists",
        )
    db_brand = crud.restore(db, tables.Brand, brand_id)
    return db_brand
