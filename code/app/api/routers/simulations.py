from fastapi import APIRouter

router = APIRouter()


@router.get('/simulations/', tags=['simulations'])
async def read_simulations():
    """ToDo: retrieve the list of routes"""
    return []


@router.get('/simulations/{simulation_uuid}', tags=['simulations'])
async def read_simulation(simulation_uuid: str):
    """ToDo: retrieve a single simulation information based on its UUID"""
    return {'uuid': simulation_uuid}
