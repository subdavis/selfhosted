FROM alpine

RUN apk add rsync
ENTRYPOINT ["rsync"]
CMD ["-ra", "--update", "/source", "/dest"]
