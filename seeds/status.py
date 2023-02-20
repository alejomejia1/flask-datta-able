import sys
 # setting path
sys.path.append('../../apps')

print('PATH:', sys.path)
from flask_seeder import Seeder, Faker, generator
from apps.home.models import Status


        
# All seeders inherit from Seeder
class StatusSeeder(Seeder):
    def __init__(self, db=None):
        super().__init__(db=db)
        self.priority = 10
    
  # run() will be called by Flask-Seeder
    def run(self):
        # Create a new Faker and tell it how to create User objects
        print("Creating Status Data")
        self.db.session.add(Status('1','Creada'))
        self.db.session.add(Status('2','Enviada'))
        self.db.session.add(Status('3','Pagada'))
        self.db.session.add(Status('4','Cancelada'))