import logging
logger = logging.getLogger('botcore')

# Shared event classes for the chicken commands

class GiftData():
    obj_list = []

    def __init__ (self):
        self.author = {}
        self.target = {}
        self.identifier = []
        GiftData.obj_list.append(self)

    @staticmethod
    def get(identifier):
        for obj in GiftData.obj_list:
            if obj.identifier == identifier:
                return obj
        return None
    
    @staticmethod
    def remove(obj):
        try:
            GiftData.obj_list.remove(obj)
        except Exception as e:
            logger.error("Error removing object from list.", e)

    @staticmethod
    def get_all():
        return GiftData.obj_list
    
    @staticmethod
    def clear():
        GiftData.obj_list.clear()

    @staticmethod
    def read(author):
        for obj in GiftData.obj_list:
            for id in obj.identifier:
                if id == author:
                    return True
    @staticmethod
    def getall():
        for obj in GiftData.obj_list:
            return obj
        
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
    def removeAll():
        RollLimit.obj_list.clear()

class SellData():
    obj_list = []

    def __init__ (self, author_id):
        SellData.obj_list.append(self)
        self.author = author_id

    @staticmethod
    def get(author):
        for obj in SellData.obj_list:
            if obj.author == author:
                return obj
        return None
    
    @staticmethod
    def remove(obj):
        if obj in SellData.obj_list:
            SellData.obj_list.remove(obj)
        else:
            logger.error("Error removing object from list. Probably doesn't exist or already removed.")

    @staticmethod
    def get_all():
        return SellData.obj_list
    
    @staticmethod
    def clear():
        SellData.obj_list.clear()

    @staticmethod
    def read(author):
        for obj in SellData.obj_list:
            print(obj.author)
            if obj.author == author:
                return True
            
class TradeData():
    obj_list = []

    def __init__ (self):
        self.author = {}
        self.target = {}
        self.identifier = []
        TradeData.obj_list.append(self)

    @staticmethod
    def get(identifier):
        for obj in TradeData.obj_list:
            if obj.identifier == identifier:
                return obj
        return None
    @staticmethod
    def remove(obj):
        try:
            TradeData.obj_list.remove(obj)
        except Exception as e:
            logger.error("Error removing object from list.", e)

    @staticmethod
    def get_all():
        return TradeData.obj_list

    @staticmethod
    def clear():
        TradeData.obj_list.clear()

    @staticmethod
    def read(author):
        for obj in TradeData.obj_list:
            for id in obj.identifier:
                if id == author:
                    return True
        return None