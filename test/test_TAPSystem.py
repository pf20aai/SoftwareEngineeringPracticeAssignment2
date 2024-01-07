import unittest
import copy
from objects import Channel
from databaseObjects import testObjects

# Setup Functions

def F_DEFAULT_CHANNEL():
    channel = Channel("defaultChannel", "defaultChannel")
    return channel

def F_DEFAULT_CUSTOMER():
    channel = F_DEFAULT_CHANNEL()
    customer = testObjects["customers"][channel.createChild("Customer 1")]
    return customer

def F_DEFAULT_USER():
    customer = F_DEFAULT_CUSTOMER()
    user = testObjects["users"][customer.createChild("User1")]
    return user

# Tests

class test_access_tokens(unittest.TestCase):

    def setUp(self) -> None:
        self.defaultUser = F_DEFAULT_USER()

    def test_token_details(self):
        expectedName = "Default Token"
        tokenId = self.defaultUser.createChild(expectedName)
        tokens = self.defaultUser.getAccessTokens()
        tokenName = ""
        for token in tokens:
            tokenObject = testObjects["accessTokens"][token]
            if tokenObject.id == tokenId:
                tokenName = tokenObject.name
            else:
                self.fail("Token not found")

        self.assertEqual(tokenName, expectedName)


class test_user_object(unittest.TestCase):
    
    def setUp(self) -> None:
        self.defaultUser = F_DEFAULT_USER()

    @staticmethod
    def generate_tokens(userClass, numberOfTokens):
        tokenList = []
        for requiredToken in range(1, numberOfTokens+1):
            tokenList.append(userClass.createChild(f"Token{requiredToken}"))
        return tokenList

    def test_create_access_token(self):
        expectedName = "Test Token"
        tokenId = self.defaultUser.createChild(expectedName)
        tokens = self.defaultUser.getAccessTokens()
        tokenName = ""
        counter = 0
        for token in tokens:
            tokenObject = testObjects["accessTokens"][token]
            if tokenObject.id == tokenId:
                counter += 1
                tokenName = tokenObject.name
            else:
                self.fail("Token not found")

        self.assertEqual(1, counter)
        self.assertEqual(tokenName, expectedName)

    def test_get_access_tokens(self):
        tokenList = self.generate_tokens(self.defaultUser, 3)

        for token in self.defaultUser.getAccessTokens():
            if token not in tokenList:
                self.fail("Token not found in list")

    def test_delete_access_tokens(self):
        tokenList = self.generate_tokens(self.defaultUser, 3)
        removedToken = copy.copy(tokenList[0])

        self.defaultUser.deleteAccessToken(removedToken)
        if removedToken in self.defaultUser.getAccessTokens():
            self.fail("Token not deleted")


class test_customer_object(unittest.TestCase):

    def setUp(self) -> None:
        self.defaultCustomer = F_DEFAULT_CUSTOMER()

    @staticmethod
    def generate_users(customerClass, numberOfUsers):
        userList = []
        for requiredUser in range(1, numberOfUsers + 1):
            userList.append(customerClass.createChild(f"User{requiredUser}"))
        return userList

    def test_create_user(self):
        expectedName = "Test User"
        userId = self.defaultCustomer.createChild(expectedName)
        users = self.defaultCustomer.getUsers()
        userName = ""
        counter = 0
        for user in users:
            userObject = testObjects["users"][user]
            if userObject.id == userId:
                counter += 1
                userName = userObject.name
            else:
                self.fail("User not found")

        self.assertEqual(1, counter)
        self.assertEqual(userName, expectedName)

    def test_get_users(self):
        userList = self.generate_users(self.defaultCustomer, 3)

        for user in self.defaultCustomer.getUsers():
            if user not in userList:
                self.fail("User not found in list")

    def test_delete_users(self):
        userList = self.generate_users(self.defaultCustomer, 3)
        removedUser = copy.copy(userList[0])

        self.defaultCustomer.deleteUser(removedUser)
        if removedUser in self.defaultCustomer.getUsers():
            self.fail("User not deleted")


class test_channel_object(unittest.TestCase):

    def setUp(self) -> None:
        self.defaultChannel = F_DEFAULT_CHANNEL()

    @staticmethod
    def generate_customers(channelClass, numberOfCustomers):
        customerList = []
        for requiredCustomer in range(1, numberOfCustomers + 1):
            customerList.append(channelClass.createChild(f"Customer{requiredCustomer}"))
        return customerList

    def test_create_customer(self):
        expectedName = "Test Customer"
        customerId = self.defaultChannel.createChild(expectedName)
        customers = self.defaultChannel.getCustomers()
        customerName = ""
        counter = 0
        for customer in customers:
            customerObject = testObjects["customers"][customer]
            if customerObject.id == customerId:
                counter += 1
                customerName = customerObject.name
            else:
                self.fail("Customer not found")

        self.assertEqual(1, counter)
        self.assertEqual(customerName, expectedName)

    def test_get_customers(self):
        customerList = self.generate_customers(self.defaultChannel, 3)

        for customer in self.defaultChannel.getCustomers():
            if customer not in customerList:
                self.fail("Customer not found in list")

    def test_delete_customers(self):
        customerList = self.generate_customers(self.defaultChannel, 3)
        removedCustomer = copy.copy(customerList[0])

        self.defaultChannel.deleteCustomer(removedCustomer)
        if removedCustomer in self.defaultChannel.getCustomers():
            self.fail("Customer not deleted")

    def test_upgrade_customer(self):
        customerId = self.generate_customers(self.defaultChannel, 1)[0]
        customerObject = testObjects["customers"][customerId]
        customerVersion = copy.copy(customerObject.version)  # a copy is required to prevent a false positive

        self.defaultChannel.updateCustomerVersion(customerId)

        self.assertEqual(customerVersion + 1, customerObject.version)

    def test_downgrade_customer(self):
        customerId = self.generate_customers(self.defaultChannel, 1)[0]
        customerObject = testObjects["customers"][customerId]
        customerVersion = copy.copy(customerObject.version)

        self.defaultChannel.downgradeCustomerVersion(customerId)

        self.assertEqual(customerVersion - 1, customerObject.version)

