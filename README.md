## this is my own bombsquad 1.7.62 modded server script
contact whit me in my discord server:
https://discord.gg/v35wYXKsFq

## setup and launching 

Install `software-properties-common`
```
sudo apt install software-properties-common -y
```
Add python Deadsnakes PPA
```
sudo add-apt-repository ppa:deadsnakes/ppa
```
Install Python 3.13
```
sudo apt install python3.13 python3.13-dev python3.13-venv python3-pip -y
```
Update installed and existing packages
```
sudo apt update && sudo apt upgrade
```
Create a tmux session.
```
tmux new -s 43210
```
Download server files.
```
git clone https://github.com/anasdhaoidi/ATD-MODDED-SERVER
```
## Making the server files executable.
```
chmod 777 atd_server
chmod 777 dist/atd_headless
chmod 777 dist/atd_headless_aarch64
```
Starting the server
```
./atd_server
```
### Adding yourself as owner
- Open `dist/ba_root/mods/playersData/roles.json` in your prefered editor.
- Add your Pb-id in owner id list.
- Restart your server
