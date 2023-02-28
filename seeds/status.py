import os 
dir_path = os.path.dirname(os.path.realpath(__file__))
# # print('CURRENT PATH:', dir_path)
from pathlib import Path
parent_dir = str(Path(dir_path).parent)
# # print('PARENT PATH:', parent_dir)
import sys
#  # setting path
sys.path.append(parent_dir)


#print('PATH:', sys.path)
from flask_seeder import Seeder, Faker, generator
from apps.home.models import Status
from apps import db
        
# All seeders inherit from Seeder
class StatusSeeder(Seeder):
    def __init__(self, db = None):
        super().__init__(db=db)
        self.priority = 10
        
  # run() will be called by Flask-Seeder
    def run(self):
        # Create a new Faker and tell it how to create User objects
        print("Creating Status Data")
        self.db.session.add(Status('Creada'))
        self.db.session.add(Status('Enviada'))
        self.db.session.add(Status('Pagada'))
        self.db.session.add(Status('Cancelada'))