# features/migrations/0001_initial.py
from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True
    
    # Make sure we have no dependencies that could cause circular references
    dependencies = []
    
    # Empty operations - we're just registering the app in the migration system
    operations = []