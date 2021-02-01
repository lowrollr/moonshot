FROM golang

ENV GOPATH /go
ENV PATH $GOPATH/bin:/usr/local/go/bin:$PATH

# RUN apk update && apk add --no-cache git
WORKDIR /go/src
COPY src .
RUN go get -d -v
RUN go build -v -o portfolio_manager
CMD ./portfolio_manager

# RUN go get -d -v
# RUN go get github.com/derekparker/delve/cmd/dlv
# CMD ["dlv", "debug", "--listen=:4000", "--headless=true", "--api-version=2", "--log", "."]