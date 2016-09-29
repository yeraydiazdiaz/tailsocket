echo "Tailsocket VM provision start..."

export LANG=en_GB.UTF-8
export LC_ALL=en_GB.UTF-8
export LC_CTYPE=en_GB.UTF-8
export LANGUAGE=en_GB.UTF-8
sudo locale-gen en_GB.UTF-8

sudo apt-get update && sudo apt-get install -y build-essential curl python3 python3-pip python3-venv python-dev make libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget llvm libncurses5-dev libncursesw5-dev xz-utils

curl -sL https://deb.nodesource.com/setup_6.x | sudo -E bash -
sudo apt-get install -y nodejs

cd ~/tailsocket
pyvenv ~/venv
source ~/venv/bin/activate
pip install -U pip wheel
pip install -r requirements.txt
python setup.py develop
