from invitemedia.library.model import ModelInstance, BaseModel

class Model(BaseModel):

    def __init__(self, model_name, connection):
        super(Model, self).__init__(model_name, connection)
        
    def filter(self,**kwds):
        """
        Fetch all instances of the model in the REST database, only return objects with
        fields matching keyword arguments.
        """
        return self.all(**kwds)
        
    def all(self, **kwds):
        """
        Fetch all instances of the model in the REST database, with possible
        keyword arguments.
        """
        url = "%s/" % self.model_name
        con = self.connection
        
        return [ModelInstance(self, d) for d in con.get(url, get=kwds)]
    
    def new(self, **kwds):
        return ModelInstance(self, {'fields': kwds})
    
    def get(self, id=None, **kwds):
        if id:
            model_dict = self.connection.get("%s/%s/" % (self.model_name, str(id)),
                                             get=kwds)[0]
        else:
            model_dict = self.connection.get("%s/" % self.model_name,get=kwds)[0]
        
        return ModelInstance(self, model_dict)
    
    def get_many(self, ids):
        resource = '%s/' % self.model_name
        sep = '?'
        for i in ids:
            resource += '%sid=%i' % (sep, i)
            sep = '&'

        model_dicts = self.connection.get(resource)
        return [ModelInstance(self, model_dict) for model_dict in model_dicts]

    def get_resource(self, additional_resource_path, **kwds):
        resource = '%s/%s' % (self.model_name, additional_resource_path)
        model_dicts = self.connection.get(resource, get=kwds)
        return [ModelInstance(self, d) for d in model_dicts]

    def update_instance(self, model_instance, dirty_fields=[]):
        print 1
        if len(dirty_fields) < 1:
            
            return

        url = "%s/%i/" % (self.model_name, model_instance.id)
        params = {}
        
        for field in dirty_fields:
            params[field] = model_instance.fields[field]
        
        self.connection.put(url, post=params)
    
    def create_instance(self, model_instance):
        print 2
        url = "%s/new/" % (self.model_name)
        model_dict = self.connection.post(url, post=model_instance.fields)[0]
        
        model_instance.id = model_dict['pk']        
        for field in model_dict['fields'].keys():
            model_instance.fields[field] = model_dict['fields'][field]

    def delete_instance(self, model_instance):
        url = "%s/%i/" % (self.model_name, model_instance.id)
        self.connection.delete(url)