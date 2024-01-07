from typing import Optional, Any
from databaseObjects import testObjects


class ApiServer:

    def __init__(self, database: dict[str, Any]):
        self.database = database  # create a database attribute for

    @staticmethod
    def generateResponse(code: int, data: dict[str, Any]) -> dict[str, Any]:
        return {"statusCode": code, "data": data}

    @staticmethod
    def seperatePath(path: str) -> list[str]:
        # split paths into a list so we can find the correct object
        return path.split("/")

    def findDbEntity(self, path: list[str]) -> Any:
        # search through the path until we find the correct object id in the database
        layer = self.database
        while len(path) > 0:
            entity = path.pop(0)
            layer = layer[entity]
        return layer

    def processGet(self, path: list[str]) -> dict[str, Any]:
        # search for the object id in the database and if it fails return a not found error
        try:
            return self.generateResponse(200, self.findDbEntity(path))
        except KeyError:
            return self.generateResponse(404, {"message": "Not found"})

    def processPost(self, path: list[str], data: dict[str, Any]) -> dict[str, Any]:
        # this method does not require a path but for simulation sake is has been left in
        # using the parent class we create a new child
        parent = data["from"]
        id = parent.createChild(data["name"])

        return self.generateResponse(200, id)

    def processPut(self, path: list[str], data: dict[str, Any]) -> dict[str, Any]:
        # search for the object id in the database and if it fails return a not found error if it doesn't then update its name
        try:
            self.findDbEntity(path.copy())  # does the object exist
        except KeyError:
            return self.generateResponse(404, {"message": "Not found"})

        objectId = path.pop()
        objectType = path.pop()
        testObjects[objectType][objectId].name = data["name"]  # for sake of simplicity we're only updating names at the moment
        return self.generateResponse(201, {"message": "updated"})

    def processDelete(self, path: list[str]) -> dict[str, any]:
        # search through to find the parent object to the target. Delete the target from the parent
        entityId = path.copy().pop()  # we need the ID but will also be using the path later
        layer = self.database
        searchPath = path.copy()
        while len(searchPath) > 1:
            entity = searchPath.pop(0)
            layer = layer[entity]
        layer.pop(entityId)

        # because we know the form of the path we can work out where the variables we need are
        objectId = path.pop()  # this will be the id of the object
        objectType = path.pop()  # this will be the type of object
        testObjects[objectType].pop(objectId)

        return self.generateResponse(200, {"message": "deleted"})

    def sendCommand(self, request: str, path: str, data: Optional[dict[str, Any]] = None) -> dict[str, Any]:

        # process commands sent to this object
        processedPath = self.seperatePath(path)

        if request.lower() == "get":
            return self.processGet(processedPath)
        elif request.lower() == "post":
            return self.processPost(processedPath, data)
        elif request.lower() == "put":
            return self.processPut(processedPath, data)
        elif request.lower() == "delete":
            return self.processDelete(processedPath)

        # Route all paths and if we can't return a 405 error

        return self.generateResponse(405, {"message": "Request not allowed"})
