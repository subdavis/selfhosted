FROM alpine

ENV APIURL=""
ENV APIKEY=""
ENV HOSTNAME=""
ENV SECRET=""

# Needed by the shell script
RUN apk add git jq curl bash
RUN git clone https://github.com/awslabs/route53-dynamic-dns-with-lambda /awslabs
# Explicitly support known working commit a1cb6efd1de04c0f19d07113b3efe9381f084541
# this should also prevent a takeover of that github repo by some bad actor
# given sha1 integrity holds :)
RUN cd /awslabs && git checkout a1cb6efd1de04c0f19d07113b3efe9381f084541
CMD /awslabs/route53-ddns-client.sh --hostname "${HOSTNAME}" --api-key "${APIKEY}" --secret "${SECRET}" --url "${APIURL}"
