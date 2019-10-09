#coding:utf-8
import threading 
import time
import pytest
from .connect import DataClient, DataBase
from ..psrc import ConnPool
from concurrent.futures import ProcessPoolExecutor,ThreadPoolExecutor,as_completed

app = None
DATABASECONFIG = {
    "test":{
        "host": "localhost",
        "port": 3306,
        "username": "root",
        "password": "",
        "schema"  : "test"
        }
}

class JJApp:
    def __init__(self):
        self.obj_pool = {}
        self.init_mysql_pool()
    

    def init_mysql_pool(self):
        debug = False
        for key in DATABASECONFIG:
            mysql_pool = ConnPool()
            mysql_pool.add_obj(DataBase, DATABASECONFIG[key], debug)
            self.obj_pool.setdefault(key, mysql_pool)
        
    def __getattr__(self, name):
        obj = None
        if name in DATABASECONFIG:
            pool = self.obj_pool[name]
            obj = pool.get_obj()
            if not obj:
                time.sleep(10)
                obj = pool.get_obj()
        return obj
        
    def release(self, name):
        if name in self.obj_pool:
            pool = self.obj_pool[name]
            pool.release_obj()

def print_func(lock):
    global app
    sql = u"""
        select * from test limit 10;
    """
    data = app.test.query(sql)
    if lock.acquire():
        for item in data:
            print(item['name'])
    lock.release()
    app.release("test")
    time.sleep(20)

def test_pool():
    global app
    app = JJApp()
    lock = threading.Lock()
    with ThreadPoolExecutor(3) as executor:
        for _ in range(5):
            executor.submit(print_func, lock)


