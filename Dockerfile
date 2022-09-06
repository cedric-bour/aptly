FROM ubuntu:20.04

RUN echo "deb [trusted=yes] http://repo.aptly.info/ squeeze main" > /etc/apt/sources.list.d/aptly.list

RUN apt update -y && apt install -y gpg aptly xz-utils nginx screen rng-tools python3 python3-yaml && rm -rf /var/cache/apt/*

COPY default /etc/nginx/site-enabled/default

RUN groupadd -g 1010 aptly
RUN mkdir /srv/aptly
RUN useradd -u 1010 -g 1010 aptly -s /bin/bash -d /srv/aptly
RUN chown aptly:aptly -R /srv/aptly/

RUN service rng-tools start

RUN apt update -y && apt install -y sudo wget curl net-tools gnupg python3-pip && rm -rf /var/cache/apt/*

RUN pip3 install pytz

USER aptly

COPY gpg2_generate_batch_file.txt /srv/aptly/gpg2_generate_batch_file.txt

RUN gpg --batch --gen-key /srv/aptly/gpg2_generate_batch_file.txt

WORKDIR /srv/aptly

VOLUME [ "/srv/aptly" ]

EXPOSE 8080

ENTRYPOINT [ "./mirror.py" ]
