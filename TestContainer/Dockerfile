FROM alpine

RUN apk add --update \
    bash \
    shadow \
    sudo \
    coreutils \
    nano \
    netcat-openbsd \
    curl 

COPY ttyd_linux.x86_64 /bin/ttyd

RUN chmod 755 /bin/ttyd

RUN useradd -m -u 1100 -s /bin/bash bob
RUN echo 'bob ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

ENV HOME /home/bob
WORKDIR /home/bob
RUN chown -R bob /home/bob

COPY shellart.txt /etc/shellart
COPY bashrc /home/bob/.bashrc

EXPOSE 7681
ENTRYPOINT ["ttyd", "-m", "2", "-u", "1100", "-O"]

CMD ["/bin/bash"] 
