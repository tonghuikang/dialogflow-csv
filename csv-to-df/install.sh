# assumes Ubuntu 16.04, 10GB space, allow http and https

export LC_ALL="en_US.UTF-8"
export LC_CTYPE="en_US.UTF-8"
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install git zip python3 python3-pip python3-tk -y
pip3 install jupyter ipykernel pandas
