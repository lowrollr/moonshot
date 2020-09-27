FROM golang:rc-alpine
RUN apk update && apk add --no-cache git
WORKDIR /code
COPY src .
RUN go get -d -v
RUN go build -v
CMD ./code
