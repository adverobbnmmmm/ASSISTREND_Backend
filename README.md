# Create a virtual environment
python3 -m venv env

# Activate the virtual environment
source env/bin/activate 
or 
env\Scripts\activate

# Install requirements
navigate to service folder using command: cd service_folder_name
pip install -r requirements.txt

# Create .env files for env variables
cp .env.sample .env