#coding:utf-8
"""
@author:viver
@E-mail: luoxianlinviver@gmail.com
"""
from threading import get_ident, Lock, Thread
import logging
import time
import inspect


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
)


class ConnPool:

    def __init__(self, pool_size = 5, init_size = 5,auto_check = False, retry_time = 10000, timeout = 60 * 60 * 1000):
        self.init_stack = LocalStack(pool_size)
        self.pool_size  = pool_size
        self.init_size  = init_size
        self.used_locals = Local()
        self.lock  = Lock()
        self.auto_check = auto_check
        self.retry_time = retry_time
        self.timeout     = timeout
    
    def add_obj(self,  obj, *args, **kwargs):
        self.obj = obj
        self.obj_args = args
        self.obj_kwargs = kwargs
        if not inspect.isclass(obj):
            raise TypeError("obj attr must be object type")
        self.__init_func()
        
    def __init_func(self):
       
        self.__init_conn_pool()

        if self.auto_check:
            """
            如果需要自动重连及删除失效连接，需遵守下述文档:

            self.obj对象需提供status方法和reconn方法
            status方法提供连接的状态
            reconn提供连接过期之后的重连对象
            eg: 
                class obj:
                    def __init__(self):
                        self.conn_status = True
                    ...
                    def reconn(self):
                        ...
                        self.conn_status = True
                        return self
                    
                    def status(self):
                        ...
                        return True
             """
            if not hasattr(self.obj, "reconn") or not hasattr(self.obj, "status"):
                raise RuntimeError("reconn or status methods not implement in obj class")
            self.monitor = MonitorObj(self.init_stack, self.retry_time, self.timeout)
            self.monitor.start()


    def get_obj(self):
        # 返回池对象, 检查是否被初始化, 检查是否超过对象池大小, 检查是否被已经处于被使用状态
        obj = None
        try:
            obj = self.used_locals.obj_name
            return obj['obj']
        except:
            pass

        if self.lock.acquire():
            try:
                obj = self.init_stack.pop()
            except:
                if self.init_stack.get_size() + self.used_locals.size() < self.pool_size:
                    try:
                        _ = self.used_locals.obj_name
                    except:
                        obj = self.obj(*self.obj_args, **self.obj_kwargs)
            finally:
                if obj:
                    self.used_locals.obj_name = obj

                self.lock.release()
        
        if obj:
            # 返回状态正常的连接
            tmp_obj = obj['obj']
            if tmp_obj.status():
                return tmp_obj
            if  self.lock.acquire():
                try:
                    self.used_locals.pop()
                    tmp_obj = self.obj(*self.obj_args, **self.obj_kwargs)
                    self.used_locals.obj_name = tmp_obj
                except Exception as e:
                    logging.info(e)
                    self.lock.release()
                    raise
                finally:
                    self.lock.release()
            return tmp_obj
                
        return obj


            
    def __init_conn_pool(self):
        if self.lock.acquire():
            try:
                for _ in range(self.init_size):
                    # 初始化对象
                    init_obj = self.obj(*self.obj_args, **self.obj_kwargs)
                    self.init_stack.put(init_obj)

            except Exception as e:
                logging.info(e)
                self.lock.release()
                raise RuntimeError("init obj error")
            self.lock.release()
        

    def release_obj(self):
        # 释放的对象重新入池
        if self.lock.acquire():
            try:
                obj = self.used_locals.obj_name
                self.used_locals.release()
                self.init_stack.put(obj['obj'])
            except:
                logging.info("release error")
                self.lock.release()
                raise RuntimeError("current thread can not get used obj")
            finally:
                self.lock.release()
                
        


class Local(object):
    """提供ThreadLocal功能"""
    def __init__(self):
        object.__setattr__(self, "__storage__", {})
        object.__setattr__(self, "__ident_func__", get_ident)

    def __getattr__(self, name):
        try:
            return self.__storage__[self.__ident_func__()][name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        ident = self.__ident_func__()
        storage = self.__storage__
        try:
            storage[ident][name] = value
        except KeyError:
            storage[ident] = {name: value}
    
    def __release_local__(self):
        self.__storage__.pop(self.__ident_func__(), None)
        
    def size(self):
        return len(self.__storage__)

    def release(self):
        self.__release_local__()

    def __str__(self):
        return str(self.__storage__)

    # def __iter__(self):
    #     return iter(self.__storage__.items())


class LocalStack(object):
    """提供遍历操作的栈"""

    def __init__(self, size = 20):
        self.__stack = []
        self.lock = Lock()

    def put(self, obj):
        if self.lock.acquire():
            tmp_dict = {"obj": obj, "init_time": int(time.time() * 1000)}
            self.__stack.append(tmp_dict)
        self.lock.release()
        

    def pop(self):
        tmp = None
        if self.lock.acquire():
            try:
                if len(self.__stack) > 0:
                    tmp = self.__stack[-1]
                    del self.__stack[-1]

            except Exception as e:
                logging.info("pop error %s"%e)
            finally:
                self.lock.release()
        return tmp

    def delete(self, offset):
        if  0 <= offset < self.get_size():
            del self.__stack[offset]
            return True
        return False
        

    def get_size(self):
        return len(self.__stack)

    def __iter__(self):
        return iter(self.__stack)

    def __str__(self):
        return str(self.__stack)

    
class MonitorObj(Thread):
    
    def __init__(self, local_stack, retry_time, timeout):
        super(MonitorObj, self).__init__()
        
        if not isinstance(local_stack, LocalStack):
            raise TypeError("type error")

        if retry_time <= 0 or timeout <= 0:
            retry_time = 10000
            timeout  = 10000

        self.local_stack = local_stack
        self.retry_time = retry_time
        self.timeout = timeout

    def action(self):
        offset = 0
        for each in self.local_stack:
            now_time = int(time.time() * 1000)
            obj   = each['obj']
            init_time = each['init_time']
            # 判断对象状态 和 对象是否超时
            if not obj.status() or not ((now_time - init_time) >= self.timeout):
                if not obj.reconn():
                    self.local_stack.delete(offset)
                    continue
        
                each['init_time'] = int(time.time() * 1000)
    
    def run(self):
        while True:
            self.action()
            print("try to check status")
            time.sleep(self.retry_time/1000)
