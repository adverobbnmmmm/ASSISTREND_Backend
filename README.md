# Create a virtual environment
python3 -m venv env

# Activate the virtual environment
source env/bin/activate 
or 
env\Scripts\activate

# Install requirements
pip install -r requirements.txt

# Create .env files for env variables
cp .env.sample .env