#### RESP

###### ABSTRACT

RESP is python resource pool, is can use in  DataBase、NoSql、WebSocket etc...

##### USE

```python
from pool import ConnPool
"""
	in this case, use pysql as testing
	app is your project
"""
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

class YourApp:
  def __init__(self):
    self.obj_pool = {}
    self.init_mysql_pool()
    
  def init_mysql_pool(self):
    debug = False
    for key in DATABASECONFIG:
      mysql_pool = ConnPool()
      mysql_pool.add_obj(DataBase, DATABASECONFIG[key], debug)
      self.obj_pool.setdefault(key, mysql_pool)
  
  def _getattr__(self, name):
    "__getattr__ must overwrite to get resource object"
    if name in DATABASECONFIG:
      pool = self.obj_pool[name]
      obj = pool.get_obj()
      if not obj:
        time.sleep(10)
        obj = pool.get_obj()
      return obj
  
 def release(self, name):
  "release must implement to release resouece when not use"
 	if name in self.obj_pool:
    pool = self.obj_pool[name]
    pool.release_obj()
```

if you had implemented your app as above, then 

```python
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
  app = YourApp()
  lock = threading.Lock()
  with ThreadPoolExecutor(3) as executor:
    for _ in range(5):
      executor.submit(print_func, lock)
```

if you wanted more details see test dir

