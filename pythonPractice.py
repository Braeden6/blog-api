
#getInput = input("Enter a number: ")
#print(getInput)


class TestClass:
    def __init__(self, name):
        self.name = name

    def getName(self):
        return self.name

    def setName(self, name):
        self.name = name
    
class TestClass2(TestClass):
    def __init__(self, name, age):
        super().__init__(name)
        self.age = age

    def getAge(self):
        return self.age

    def setAge(self, age):
        self.age = age

# tuple is immutable
test = (1,2,3)
try:
    test[0] = 4
except Exception as e:
    print("error test is immutable")
print(test)
# set is mutable, no duplicates
test = {1,1,3}
test.add(4)
print(test)
# list is mutable
test = [1,2,3]
test[0] = 4
print(test)


from aTestFolder import doSomething
doSomething.doSomething()


test = TestClass("test")
print(test.getName())

test2 = TestClass2("test2", 2)
print(test2.getName() + " " + str(test2.getAge()))
