#coding:utf-8
# import threading, time
# from threading import get_ident

# global_data = threading.local()
# def show():
#     cur_thread = threading.current_thread()
#     print("thread name %s and num %s and id %s"%(cur_thread.getName(), global_data.num, get_ident()))


# def thread_cal():
#     global global_data 
#     global_data.num = 0
#     for i in range(5):
#         global_data.num += 1
#         show()

# threads = []
# for i in range(5):
#     threads.append(threading.Thread(target = thread_cal))
#     threads[i].start()

# for i in range(5):
#     threads[i].join()


# print("main end!")

from werkzeug.local import LocalStack, LocalProxy
from flask import Flask
user_stack = LocalStack()
user_stack.push({"name": "Bob"})
user_stack.push({"name": "John"})


def get_user():
        return user_stack.pop()

user = LocalProxy(get_user)
print(user["name"])
print(user["name"])