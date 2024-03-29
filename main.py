#1 terminal:connected
print({"message":"connected to terminal"})

#2 server run
import uvicorn
from project import project
from config import config_data as config

from starlette.middleware.cors import CORSMiddleware

origins = ["*"]

project.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
print({"message":"cors middleware added"})

if __name__ == "__main__":
    uvicorn.run("project:project",host=config['backend_server_host'], port=int(config['backend_server_port']),workers=8,http='h11',reload=True)

#3 server:started
print({"message":"project server started"})