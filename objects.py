from typing import Optional, Any
from uuid import uuid4
from apiServer import ApiServer
from databaseObjects import testObjects


ManagementServer = ApiServer({"channels": {}})

MainServer = ApiServer({"customers": {}})


class DefaultObjects:  # Every object will have a similar layout to this default class

    def __init__(self, id: str, name: str, ):
        self.id = id
        self.name = name

    def createChild(self, name: str) -> str: # each object will override create child to make their own child object
        pass

class Schema:  # this is a singleton that mimics the schema we would have in the real system

    def __init__(self):
        self.schema = ""

    def getSchema(self): # create a "schema"
        if not self.schema:
            self.schema = "Active"
            return self.schema
        else:
            return self.schema

    def checkValueAgainstSchema(self, value: Any) -> None:
        # this is only used for test purposes
        schema = self.getSchema()
        if (not bool(value)) and schema:  # check the schema is active and there is some value in response
            raise Exception("Invalid value")

class AccessToken(DefaultObjects): # this object exists as the end of chain
    def __init__(self, token_id: str, name: str):
        super().__init__(token_id, name)

class User(DefaultObjects):
    def __init__(self, user_id: str, name: str, customerId: str, accessTokens: Optional[list[str]] = None):
        super().__init__(user_id, name)
        self.customerId = customerId
        if accessTokens is None:
            accessTokens = {}
        self.accessTokens = accessTokens

    def createChild(self, name: Optional[str] = None) -> str:
        tokenId = str(uuid4())
        if name is None:
            name = f"Token {len(self.accessTokens)+1}"
        newToken = AccessToken(tokenId, name)
        testObjects["accessTokens"][tokenId] = newToken
        self.accessTokens.update({tokenId: {}})
        MainServer.database["customers"][self.customerId]["users"][self.id]["accessTokens"] = self.accessTokens
        return tokenId

    def getAccessTokens(self) -> list[str]:
        return self.accessTokens

    def deleteAccessToken(self, token: str) -> None:
        del self.accessTokens[token]  # code here fix from original design so tests run clean


class Customer(DefaultObjects):

    def __init__(self, customer_id: str, name: str, version: int):
        super().__init__(customer_id, name)
        self.version = version
        self.users = {}

    def createChild(self, name: str) -> str:
        userId = str(uuid4())
        newUser = User(userId, name, self.id)
        testObjects["users"][userId] = newUser
        self.users.update({userId: {}})
        MainServer.database["customers"][self.id]["users"] = self.users
        return userId

    def getUsers(self) -> list[str]:
        return list(self.users.keys())

    def deleteUser(self, user_id: str) -> None:
        self.users.pop(user_id)


class Channel(DefaultObjects):
    def __init__(self, channel_id: str, name: str):
        super().__init__(channel_id, name)
        self.customers: dict[str, dict] = {}
        ManagementServer.database["channels"].update({channel_id: {"customers": self.customers}})
        testObjects["channels"][channel_id] = self

    def createChild(self, name: str) -> str:
        customerId = str(uuid4())
        newCustomer = Customer(customerId, name, 1)
        testObjects["customers"][customerId] = newCustomer
        self.customers.update({customerId: {}})
        ManagementServer.database["channels"][self.id]["customers"] = self.customers
        MainServer.database["customers"].update({customerId: {"users": newCustomer.users}})
        return customerId

    def getCustomers(self) -> list[str]:
        return list(self.customers.keys())

    def deleteCustomer(self, customerId: str) -> None:
        self.customers.pop(customerId)
        ManagementServer.database["channels"][self.id]["customers"] = self.customers
        MainServer.database["customers"].pop(customerId)

    def updateCustomerVersion(self, customer_id: str) -> None:
        testObjects["customers"][customer_id].version += 1

    def downgradeCustomerVersion(self, customer_id: str) -> None:
        testObjects["customers"][customer_id].version -= 1
