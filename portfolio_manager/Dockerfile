FROM golang

ENV GO111MODULE auto
ENV GOPATH /go
ENV PATH $GOPATH/bin:/usr/local/go/bin:$PATH
# RUN apk update && apk add --no-cache git
WORKDIR /go/src
COPY src .
RUN go get -d -v
RUN go build -v -o portfolio_manager
RUN chmod +x wait-for-it.sh
RUN CGO_ENABLED=0 go build -gcflags "all=-N -l" -o ./portfolio_manager .
CMD ./wait-for-it.sh beverly_hills:7979 -t 0 -- ./portfolio_manager

# RUN go get -d -v
# RUN go get github.com/derekparker/delve/cmd/dlv
# CMD ["dlv", "debug", "--listen=:4000", "--headless=true", "--api-version=2", "--log", "."]