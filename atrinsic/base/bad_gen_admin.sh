grep "models.Model" models.py | sed "s/class/admin.site.register(/g" | sed 's/\(models.Model.\):/)/' | sed 's/()/)/' >> admin.py

