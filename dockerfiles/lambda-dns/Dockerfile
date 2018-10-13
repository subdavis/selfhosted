FROM ubuntu

ENV APIURL=""
ENV APIKEY=""
ENV HOSTNAME=""
ENV SECRET=""
ENV CRON_SCHEDULE=""

RUN cd /tmp
RUN apt update
RUN apt install -y git cron curl jq
RUN git clone https://github.com/awslabs/route53-dynamic-dns-with-lambda /tmp
COPY ./start.sh /tmp

CMD /tmp/start.sh
