import logging
import discord
logger = logging.getLogger('botcore')

# Shared event classes for the chicken commands        
class RollLimit:
    obj_list = {}

    @classmethod
    def read(cls, user_id: int) -> object:
        return cls.obj_list.get(user_id)
    

    @classmethod
    def read_key(cls, key: int) -> bool:
        if key in cls.obj_list.keys():
            return True
        return False

    @classmethod
    def remove(cls, user_id: int) -> None:
        try:
            cls.obj_list.pop(user_id)
        except Exception as e:
            logger.error("Error removing object from list.", e)
    
    @classmethod
    def update(cls, user_id: int, current: int) -> None:
        obj = cls.obj_list.get(user_id)
        if obj:
            cls.obj_list[user_id] = current
        else:
            cls.obj_list[user_id] = current

    @classmethod
    def create(cls, user_id: int, current: int) -> None:
        cls.obj_list[user_id] = current

    @classmethod
    def remove_all(cls) -> None:
        cls.obj_list.clear()

class EventData():
    current_users_in_event = {}

    def __init__(self, user: discord.Member):
        self.user = user
        EventData.current_users_in_event[user.id] = self

    @staticmethod
    def check_user_in_event(user_id: int) -> bool:
        if user_id in EventData.current_users_in_event.keys():
            return True
        return False
        
    @staticmethod
    def remove(obj: object) -> None:
        try:
            del EventData.current_users_in_event[obj.user.id]
        except ValueError:
            logger.warning("Error removing object from list. Probably already removed.")
        except KeyError:
            logger.warning("Error removing object from list. Probably already removed.")
        except Exception as e:
            logger.error("Error removing object from list.", e)
