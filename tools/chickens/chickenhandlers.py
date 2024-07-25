import logging
logger = logging.getLogger('botcore')

# Shared event classes for the chicken commands        
class RollLimit:
    obj_list = []
    def __init__(self, user_id, current, chickens=None):
        RollLimit.obj_list.append(self)
        self.user_id = user_id
        self.current = current
        self.chickens = chickens

    @staticmethod
    def read(user_id):
        for obj in RollLimit.obj_list:
            if obj.user_id == user_id:
                return obj
        return None
    
    @staticmethod
    def remove(obj):
        try:
            RollLimit.obj_list.remove(obj)
        except Exception as e:
            logger.error("Error removing object from list.", e)
    
    @staticmethod
    def remove_all():
        RollLimit.obj_list.clear()

class EventData():
    obj_list = []
    allowed_keys = ['author', 'target']

    def __init__(self, **kwargs):
        if any(key in kwargs for key in EventData.allowed_keys if key not in kwargs):
            raise ValueError("Missing required keys.")
        else:
            for key in kwargs:
                if key in EventData.allowed_keys:
                    setattr(self, key, kwargs[key])
            EventData.obj_list.append(self)

    @staticmethod
    def read_kwargs(**kwargs):
        for obj in EventData.obj_list:
            for key in kwargs:
                if key in EventData.allowed_keys and key in obj.__dict__:
                    if getattr(obj, key) == kwargs[key]:
                        return True
        return False
    
    @staticmethod
    def remove(obj):
        try:
            EventData.obj_list.remove(obj)
        except Exception as e:
            logger.error("Error removing object from list.", e)

    @staticmethod
    def remove_all():
        EventData.obj_list.clear()
