#coding:utf-8
import threading 
import time
from pool import ConnPool

class TestObj:
    def __init__(self, hello, world):
        self.hello = hello
        self.world = world

    def status(self):
        return True

    def reconn(self):
        return self

    def action(self):
        print ("hello world")




# pool = ConnPool(TestObj, 5, hello="hello", world="world")

# def test_func():
#     obj = pool.get_obj()
#     obj.action()
#     time.sleep(1)
#     pool.release_obj()

# threads = []

# for i in range(5):
#     threads.append(threading.Thread(target = test_func))
#     threads[i].start()

# for i in range(5):
#     threads[i].join()



class A:
    def __init__(self, x,y,z=3,*poster,**keypar):
        print (x, y, z)
        print (poster)
        print (keypar)



