from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse

from typing import List, Dict

from app.models.database import get_db
#from starlette.status import HTTP_400_BAD_REQUEST

from app.models import core
from uuid import UUID, uuid4

#from models.schemas import Menu, MenuCreate, MenuUpdate, Message



from starlette.status import HTTP_200_OK
from starlette.status import HTTP_201_CREATED

from app.services import menus as menu_service
from app.models import schemas
from typing import List, Optional


menu_router = APIRouter(prefix='/api/v1/menus')

@menu_router.get("/", response_model=List[schemas.Menu])
def get_menus(db: Session = Depends(get_db)):
    return menu_service.get_menus(db)

def test_get_menus_not_empty(db: Session):
    # Create some menus in the database
    menu_create_payloads = [
        {"title": "Menu 1", "description": "Description 1"},
        {"title": "Menu 2", "description": "Description 2"},
    ]
    for payload in menu_create_payloads:
        client.post("/api/v1/menus/", json=payload)
   
    # Send a GET request to retrieve all menus
    response = client.get("/api/v1/menus/")
   
    # Verify the response status code and JSON data
    assert response.status_code == 200
    retrieved_menus = response.json()
    assert len(retrieved_menus) == len(menu_create_payloads)
   
    for i, payload in enumerate(menu_create_payloads):
        assert retrieved_menus[i]["title"] == payload["title"]
        assert retrieved_menus[i]["description"] == payload["description"]
        assert retrieved_menus[i]["submenus_count"] == 0
        assert retrieved_menus[i]["dishes_count"] == 0

@menu_router.get("/{menu_id}", response_model=schemas.Menu)
def get_menu(menu_id: Optional[UUID], db: Session = Depends(get_db)):
    
    menu = menu_service.get_menu(db, menu_id)
    if menu is None:
        raise HTTPException(status_code=404, detail=f'menu not found')


    return menu

@menu_router.post("/", response_model=schemas.Menu, status_code=HTTP_201_CREATED)
def create_menu(menu: schemas.MenuCreate, db: Session = Depends(get_db)):
    db_menu = menu_service.create_menu(db, menu)
    db.refresh(db_menu)

    response_model = schemas.Menu(
        id=uuid4(),
        title=db_menu.title,
        description=db_menu.description,
        submenus_count=0,
        dishes_count=0
    )
    return db_menu

@menu_router.patch("/{menu_id}", response_model=schemas.Menu)
def update_menu(menu_id: UUID, menu_update: schemas.MenuUpdate, db: Session = Depends(get_db)):
    db_menu = menu_service.update_menu(db, menu_id, menu_update)
    if db_menu:
        return db_menu
    else:
        raise HTTPException(status_code=404, detail="Menu not found")



@menu_router.delete("/{menu_id}")
def delete_menu(menu_id: UUID, db: Session = Depends(get_db)):
    response = menu_service.delete_menu(db, menu_id)
    if response:
        # Return a 200 status code when the menu is successfully deleted
        return {"status": True, "message": "The menu has been deleted"}
    else:
        raise HTTPException(status_code=404, detail="menu not found")
