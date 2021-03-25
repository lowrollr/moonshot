FROM golang:1.16.1-buster as builder

ENV GO111MODULE auto
ENV GOPATH /go
ENV PATH $GOPATH/bin:/usr/local/go/bin:$PATH

WORKDIR /go/src
COPY src .
RUN go get "gorm.io/gorm"
RUN go get -d -v
RUN chmod +x wait-for-it.sh

RUN CGO_ENABLED=0 go build -gcflags "all=-N -l" -o ./portfolio_manager .

FROM alpine:edge
WORKDIR /
COPY --from=builder /go/src/portfolio_manager .
COPY --from=builder /go/src/wait-for-it.sh .
RUN apk update && apk add bash

CMD ./wait-for-it.sh beverly_hills:7979 -t 0 -- ./portfolio_manager