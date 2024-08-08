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
