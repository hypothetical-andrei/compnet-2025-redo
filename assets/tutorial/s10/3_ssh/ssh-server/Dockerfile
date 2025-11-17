FROM ubuntu:22.04

RUN apt-get update && apt-get install -y openssh-server && \
    mkdir /var/run/sshd

# Create user
RUN useradd -m labuser && echo "labuser:labpass" | chpasswd

# Enable password login
RUN sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config
RUN sed -i 's/PasswordAuthentication no/#PasswordAuthentication no/' /etc/ssh/sshd_config

CMD ["/usr/sbin/sshd", "-D"]