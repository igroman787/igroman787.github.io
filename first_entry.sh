# доустановить пакеты
apt update && apt dist-upgrade -y
apt install htop ncdu nload git iptables iptables-persistent net-tools -y

# Настроить консоль
echo "PS1='\[\033[01;32m\]\u\[\033[01;34m\]-\[\033[01;31m\]\h\[\033[00;34m\]{\[\033[01;34m\]\w\[\033[00;34m\]}\[\033[01;32m\]:\[\033[00m\]'" > ~/.bashrc
