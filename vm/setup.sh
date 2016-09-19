echo "Tailsocket VM provision start..."

echo "en_GB.UTF-8 UTF-8" | sudo tee -a /etc/locale.gen
sudo locale-gen
export LANGUAGE=en_GB.UTF-8
export LANG=en_GB.UTF-8
export LC_ALL=en_GB.UTF-8
sudo apt-get update && sudo apt-get install -y build-essential curl python3 python3-pip python3-venv

curl -sL https://deb.nodesource.com/setup_6.x | bash -
sudo apt-get install -y nodejs

# Install Python dependencies
pyvenv ~/tailsocket/venv
source ~/tailsocket/venv/bin/activate
pip install -r requirements.txt

# Set up working directory
cd ~/tailsocket
python setup.py develop
