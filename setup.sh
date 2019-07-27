export LC_ALL="en_US.UTF-8"
export LC_CTYPE="en_US.UTF-8"
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install git zip python3 python3-pip python3-tk -y
pip3 install jupyter ipykernel pandas
git clone https://github.com/tonghuikang/dialogflow-csv
pip3 install -r dialogflow-csv/requirements.txt
chmod +x ./dialogflow-csv/start.sh
chmod +x ./dialogflow-csv/clr.sh
touch ./dialogflow-csv/df-to-csv/token.pickle
touch ./dialogflow-csv/df-to-csv/credentials.json
