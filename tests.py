from copy import deepcopy
from objects import MainServer, ManagementServer, Channel, Schema
from databaseObjects import testObjects

# Here we instantiate default objects for use across tests
F_DEFAULT_CHANNEL = Channel("channel1", "Channel 1")
F_DEFAULT_CUSTOMER = testObjects["customers"][F_DEFAULT_CHANNEL.createChild("Customer 1")]
F_DEFAULT_USER = testObjects["users"][F_DEFAULT_CUSTOMER.createChild("User1")]
F_DEFAULT_ACCESS_TOKEN = testObjects["accessTokens"][F_DEFAULT_USER.createChild()]

MainSchema = Schema()
ManagementSchema = Schema()


def test_create_customers() -> None: # customer straddles across both serves so much be checked thoroughly
    # in this test we:
    # Adds a new customer
    response = ManagementServer.sendCommand("post", "customers", {"name": "Customer1", "from": F_DEFAULT_CHANNEL})
    # Checks for a schema response
    ManagementSchema.checkValueAgainstSchema(response)
    # retrieves the data of all customers
    allCustomers = MainServer.sendCommand("get", "customers")
    # Checks for a valid schema and response
    MainSchema.checkValueAgainstSchema(allCustomers)
    if response["statusCode"] != 200:
        raise Exception("Customer was not created")
    # checks the customer has been created
    if response["data"] not in (allCustomers["data"].keys()):
        raise Exception("Customer was not found after creation")

def test_retrieve_users():  # here we check we can retrieve users
    # in this test we:
    # retrieve all users
    response = MainServer.sendCommand("get", f"customers/{F_DEFAULT_CUSTOMER.id}/users")
    # check the schema and that we have found some number of users
    MainSchema.checkValueAgainstSchema(response)
    if response["statusCode"] != 200:
        raise Exception("Could not find users customers")

def test_update_channels():  # here we check we can update a channel
    # in this test we:
    response = ManagementServer.sendCommand("put", f"channels/{F_DEFAULT_CHANNEL.id}", {"name": "test2"})
    ManagementSchema.checkValueAgainstSchema(response)
    if response["statusCode"] != 201:
        raise Exception("Update unsuccessful")
    if testObjects["channels"][F_DEFAULT_CHANNEL.id].name != "test2":
        raise Exception("Update unsuccessful")

def test_delete_access_token():  # here we check we delete an access token
    # in this test we:
    # get the existing access tokens
    original = deepcopy(MainServer.sendCommand("get", f"customers/{F_DEFAULT_CUSTOMER.id}/users/{F_DEFAULT_USER.id}"))
    # due to the nature of these being mock up tests we require a deep copy of the delete to avoid updating it later
    # delete the access token
    response = MainServer.sendCommand("delete", f"customers/{F_DEFAULT_CUSTOMER.id}/users/{F_DEFAULT_USER.id}/accessTokens/{F_DEFAULT_ACCESS_TOKEN.id}")
    # check the response schema is correct and check it has been deleted
    MainSchema.checkValueAgainstSchema(response)
    new = MainServer.sendCommand("get", f"customers/{F_DEFAULT_CUSTOMER.id}/users/{F_DEFAULT_USER.id}")
    if original["statusCode"] == 404 or new["statusCode"] == 404:
        raise Exception("Test failed to complete")
    if original == new:
        raise Exception("unable to delete token")

def test_intentionally_failing_test():  # this test is used as an example of a failing test
    # in this test we:
    # do a test of an element that has not been implemented
    response = MainServer.sendCommand("patch", "customer/blah/person/", {"Bad": "data"})
    if response["statusCode"] != 200:
        raise Exception("Cannot patch")
    MainSchema.getSchema()

def test_that_includes_a_logic_error():  # altered version of get test to show what happens when a test is written incorretly
    # in this test we:
    # purposely use a logic error to fail
    response = MainServer.sendCommand("get", f"customers/{F_DEFAULT_CUSTOMER.id}/users")
    MainSchema.checkValueAgainstSchema(response)
    if response["statusCode"] != 200:
        raise Exception("Could not find users customers")
    if not response["message"]:
        raise Exception("No message")


def run_tests(tests: list[()]):  # this function is fed a list of functions to run as tests
    printout = "_____Tests_____\n"
    for test in tests:  # test any functions added to the list
        try:
            test()
            printout += f"\n{test.__name__}: Success\n"
        except Exception as e:  # if we fail we want to test the rest of them but also know how they failed
            printout += f"\n{test.__name__}: Failed\nEncountered error: {type(e).__name__}: {e}\n"
    printout += "\n\n_____Completed Tests_____"

    print(printout)  # return a useful printout to the user


# Run all tests by default
run_tests([
    test_create_customers,
    test_retrieve_users,
    test_update_channels,
    test_delete_access_token,
    test_intentionally_failing_test,
    test_that_includes_a_logic_error
])
