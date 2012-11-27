from django.db import models

class GA_SiteManager(models.Manager):
    def create_site(self, account, profile_id, active = True):
        try:
            return super(GA_SiteManager, self).get(profile_id = profile_id, account = account)
        except self.model().DoesNotExist:
            pass
        
        site = account.get_ga_sites(profile_id)
        if(not site):
            return None

        new_site = self.model()
        new_site.account = account
        new_site.name = site.title
        new_site.profile_id = profile_id
        new_site.is_active = active
        new_site.save()
        return new_site