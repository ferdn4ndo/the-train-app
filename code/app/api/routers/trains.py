from fastapi import APIRouter

router = APIRouter()


@router.get('/trains/', tags=['trains'])
async def read_trains():
    """ToDo: retrieve a list of trains"""
    return [{'username': 'Foo'}, {'username': 'Bar'}]


@router.get('/trains/{prefix}', tags=['trains'])
async def read_train(prefix: str):
    """ToDo: retrieve a single train information based on its prefix"""
    return {"prefix": prefix}
