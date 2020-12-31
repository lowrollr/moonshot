FROM golang:1.15.6-alpine3.12
RUN apk update && apk add --no-cache git
WORKDIR /go/src
COPY src .
RUN go get -d -v
RUN go build -v -o portfolio_manager
CMD ./portfolio_manager
