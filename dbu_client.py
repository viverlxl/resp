#coding:utf-8
import threading 
import time
from pool import ConnPool
import inspect

class TestObj:
    def __init__(self, hello, world, name="didi", age= 10):
        self.hello = hello
        self.world = world
        self.name = name
        self.age = age
        self.code_status = True

    def status(self):
        print("返回status %s"%self.code_status)
        return self.code_status

    def reconn(self):
        print("重置status")
        self.code_status = True
        return self

    def conn(self):
        return self

    def action(self):
        print ("hello world")

    def change_status(self):
        time.sleep(5)
        print("change status")
        self.code_status = False

    def __getattr__(self, name):
        tmp = {"jj": 2}
        return tmp.get(name, None)
        
        

# test = type("TestObj", (), {"name": "didi"})
# print (type(test()))
# print(test().hello)
# print(inspect.getcallargs(TestObj.__init__, "1", "2", "hah"))
sig = inspect.signature(TestObj.__init__)
bound = sig.bind(
    "1",
    "2",
    "duoduo",
    30
)
# print (type((bound)))
# for name, value in bound.arguments.items():
#     print (name, value)

# print (type(bound.kwargs))
# test = TestObj(*bound.args, **bound.kwargs)
# test.action()

def params_init(obj, *args, **kwargs):
    # sig = inspect.signature(obj.__init__)
    # print (args, kwargs)
    
    # bound = sig.bind(
    #     args
    # )
    # for name, value in bound.arguments.items():
    #     print (name, value)

    init_obj = obj(*args, **kwargs)
    return init_obj

test = params_init(TestObj, "1", "2", "duoduo", 30)
print(test.hello)
test.action()
print(test.jj)


# for each in inspect.signature(TestObj.__init__).parameters.items():
#     print(each[0])
# for i in (inspect.signature(TestObj.__init__)):
#     print (i)
# obj = TestObj(hello = "hello", world = "world")
# pool = ConnPool(TestObj, 5, auto_check = True)

# def test_func():
#     obj = pool.get_obj()
#     if obj:
#         obj.action()
#         time.sleep(1)
#         pool.release_obj()

# threads = []

# for i in range(5):
#     threads.append(threading.Thread(target = test_func))
#     threads[i].start()

# for i in range(5):
#     threads[i].join()



# threads = []

# for i in range(5):
#     threads.append(threading.Thread(target = test_func))
#     threads[i].start()

# for i in range(5):
#     threads[i].join()


# other_obj = pool.get_obj()
# other_obj.action()
# other_obj.change_status()
# pool.release_obj()


        


        

    
