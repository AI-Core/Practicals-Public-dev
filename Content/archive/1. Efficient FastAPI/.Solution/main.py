import fastapi
import uvicorn
from starlette.staticfiles import StaticFiles

from api import dob_api
from views import home

api = fastapi.FastAPI()


def configure_routing():
    # api.mount('/static', StaticFiles(directory='static'), name='static')
    api.include_router(home.router)
    api.include_router(dob_api.router)


if __name__ == '__main__':
    configure_routing()
    uvicorn.run(api, port=8008, host='127.0.0.1')