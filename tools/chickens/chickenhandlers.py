import logging
logger = logging.getLogger('botcore')

# Shared event classes for the chicken commands        
class RollLimit:
    obj_list = {}

    @classmethod
    def read(cls, user_id):
        return cls.obj_list.get(user_id)
    

    @classmethod
    def read_key(cls, key):
        if key in cls.obj_list.keys():
            return True
        return False

    @classmethod
    def remove(cls, obj):
        try:
            cls.obj_list.pop(obj.user_id)
        except Exception as e:
            logger.error("Error removing object from list.", e)
    
    @classmethod
    def update(cls, user_id, current):
        obj = cls.obj_list.get(user_id)
        if obj:
            cls.obj_list[user_id] = current
        else:
            cls.obj_list[user_id] = current

    @classmethod
    def create(cls, user_id, current):
        cls.obj_list[user_id] = current

    @classmethod
    def remove_all(cls):
        cls.obj_list.clear()

class EventData():
    current_users_in_event = {}

    def __init__(self, user):
        self.user = user
        EventData.current_users_in_event[user.id] = self

    @staticmethod
    def check_user_in_event(user_id):
        if user_id in EventData.current_users_in_event.keys():
            return True
        return False
        
    @staticmethod
    def remove(obj):
        try:
            del EventData.current_users_in_event[obj.user.id]
        except ValueError:
            logger.warning("Error removing object from list. Probably already removed.")
        except KeyError:
            logger.warning("Error removing object from list. Probably already removed.")
        except Exception as e:
            logger.error("Error removing object from list.", e)
