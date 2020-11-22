from fastapi import APIRouter, File, UploadFile
from starlette.requests import Request

from app.simulation.router.kml_route import KmlRouteReader

router = APIRouter()


@router.get('/routes/', tags=['routes'])
async def read_routes():
    """ToDo: retrieve the list of routes"""
    return []


@router.get('/routes/{route_name}', tags=['routes'])
async def read_route_from_name(route_name: str):
    """ToDo: retrieve a single route information based on its name"""
    return {'name': route_name}


@router.post('/routes/from-xml', tags=['routes'])
async def create_route_from_xml(*,  request: Request):
    """ToDo: save the route into a persistent layer"""
    if request.headers['content-type'] == 'application/xml':
        route_bytes = await request.body()
        route = KmlRouteReader(route_bytes, True)
        return {'data': route.serialize}
    else:
        # ToDo: return the error in a RESTful way
        return 'not file: ', request.headers['content-type']


@router.post('/routes/from-kml', tags=['routes'])
async def create_route_from_kml(file: UploadFile = File(...)):
    """ToDo: save the file and the processed route to a persistent layer"""
    contents = await file.file.read().decode('utf-8')
    route = KmlRouteReader(file.filename)
    return {'filename': file.filename, 'contents': contents, 'data': route.serialize}
