from invitemedia.library.decorator import abstract

class BaseModel(object):
    def __init__(self, model_name, connection):
        self.model_name = model_name
        self.connection = connection
        
    @abstract
    def all(self, *args, **kwds):
        """
        Fetch all instances of the model in the REST database, with possible
        keyword arguments.
        """
        pass
    
    @abstract
    def new(self, **kwds):
        pass
    
    @abstract
    def get(self, id, *args, **kwds):
        pass
    
    @abstract
    def get_many(self, ids):
        pass

    @abstract
    def update_instance(self, model_instance, dirty_fields=[]):
        pass
    
    @abstract
    def create_instance(self, model_instance):
        pass

    @abstract
    def delete_instance(self, model_instance):
        pass
