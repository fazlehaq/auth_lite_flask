import time,threading

# structure of the session_obj 
# cache_obj : {
#   session_obj : {
#     id ,
#     data , 
#     expires_at
#   },
#   last_accessed : TimeStamp,
#}

class SessionCache :
    def __init__(self,cache_size):
        self.cache = {}
        self.cache_size = cache_size
        self.cache_cnt = 0
        self.lock = threading.Lock()
        
        
    def is_session_expired(self,session_id) -> bool:
        return self.cache[session_id]["session_obj"]["expires_at" ] > time.time()
    
    def get_session(self,session_id):
        with self.lock :
            session = self.cache.get(session_id)
            if session and self.is_session_expired(session_id) :
                return session["session_obj"]
            
            if session_id in self.cache :
                del self.cache[session_id]

            return None
    
    # adds new session  
    def insert_session(self,session_obj) :
        cache_obj = {
            "session_obj" : session_obj,
            "last_accessed" : time.time()
        }
        with self.lock :
            self.cache_cnt += 1
            if self.cache_cnt == self.cache_size : 
                self.pop() # Replaces LRU session
            self.cache[session_obj["id"]] = cache_obj 
            return True
        return False
    
    def delete_session(self,session_id) :
        with self.lock :
            if session_id in self.cache :
                del self.cache[session_id]
                self.cache_cnt -= 1
        return True
    
    def pop(self):
        with self.lock :
            if self.cache_cnt == 0 :
                return 
            
            lru_session = None
            for session in self.cache.items():
                if lru_session is None :
                    lru_session = session 
                else :
                    lru_session = lru_session if lru_session[1]["last_accessed"] > session[1]["last_accessed"] else session
            
            print(lru_session)
            del self.cache[lru_session[1]["session_obj"]["id"]]
            self.cache_cnt -= 1
            return 
        
    def printCache(self):
        for cache_elem in self.cache.items() :
            print(cache_elem)


# Test code for caching 
if __name__ == "__main__" :
    objs = [
        {
        "id" : 1,
        "data" : {
            "name" : "fazlehaq"
        },
        "expires_at" : time.time() - 60*60
        },
        {
            "id" : 2 ,
            "data" : {
                "name" : "gaus"
            },
            "expires_at" : time.time() + 60*3
        },
        {
            "id" : 3,
            "data" : {
                "name" : "gfff"
            },
            "expires_at" : time.time()
        }
    ]

    cache_data = SessionCache(cache_size=5)
    for obj in objs :
        cache_data.insert_session(obj)

    cache_data.printCache()
    cache_data.pop()
    print(cache_data.get_session(3))
    print(cache_data.get_session(2))