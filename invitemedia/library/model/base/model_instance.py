from invitemedia.library.decorator import abstract

class BaseModelInstance(object):
    """
    Represents a instantiated REST resource.  It is assumed that a
    ``ModelInstance`` without an ``id`` is not persisted to the REST service,
    and vice-versa for models with an id.
    
    Fields of the model can be read one of two ways.  Either
    ``entity.fields['field_name']``, or ``entity.field``.  Similarly, fields can
    be set with ``entity.fields['field_name'] = 'foo'`` or
    ``entity.set_field_name('foo')``.
    
    self.__dict__[a] = b trickery was stolen from the Python Cookbook, page 180
    
    :Parameters:
        model : Model
            The REST Model instance to route requets to
        model_dict : dict
            A dictionary of values that will be set in the model
    """
    def __init__(self, model, model_dict):
        self.__dict__['model'] = model
        self.__dict__['_dirty_fields'] = []
        self.__dict__['fields'] = {}
        
    def save(self):
        """
        If the model has a valid ``id``, it will be "updated" on the REST
        server.  If the ``id`` field is none, it will assume that this model
        is local-only, and will to attempt to create it on the REST server
        """
        if self.model is None:
            raise NotImplementedError, \
                  'This instance has no model, it was most likely generated recursively'
    
        
        if hasattr(self,"id") and self.id is not None:
            self.model.update_instance(self, self._dirty_fields)
        else:
            self.model.create_instance(self)
        
        self._dirty_fields = []
    
    def delete(self):
        """
        Deletes a model instance.
        """
        if self.model is None:
            raise NotImplementedError, \
                  'This instance has no model, it was most likely generated recursively'
        
        self.model.delete_instance(self)
    
    def __getattr__(self, attr):
        """
        Overloads ``__getattribute__`` so that we can access fields in the 
        REST models more tersley.  When called for an attribute, it will first
        attempt to route it correctly to the model, and if an ``AttributeError``
        is thrown, it will then try to look up the attribute in the ``field``
        dictionary
        """
        try:
            return object.__getattribute__(self, attr)
        except AttributeError:
            return self.fields[attr]
    
    def __setattr__(self, attr, value):
        """
        Overrides ``__setattr__`` in such a way so that known fields in the 
        model will be saved
        """
        if attr in dir(self):
            object.__setattr__(self, attr, value)
        elif attr in self.fields.keys():
            if self.fields[attr] != value:
                self.fields[attr] = value
                self._dirty_fields.append(attr)
        else:
            raise AttributeError("%s not in this rest model"%attr)
            
    def __repr__(self):
        return "%s %s" % (self.id, str(self.fields))
