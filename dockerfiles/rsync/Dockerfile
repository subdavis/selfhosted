FROM alpine

RUN apk add rsync
ENTRYPOINT ["rsync"]
CMD ["-r", "/source", "/dest"]
