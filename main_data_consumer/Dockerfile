FROM golang

ENV GOPATH /go
ENV PATH $GOPATH/bin:/usr/local/go/bin:$PATH

# RUN apk update && apk add --no-cache git
EXPOSE 4000
WORKDIR /go/src
COPY src .
RUN go get -d -v
# RUN go get github.com/derekparker/delve/cmd/dlv

# RUN apt update
# RUN apt install net-tools
RUN chmod +x wait-for-it.sh

# RUN pwd
# RUN ls
# RUN go build -v -o 

# FROM alpine:3.11 as final
# # COPY --from=builder /portfolio_manager ./
# # COPY --from=builder /go/bin/dlv ./
# # ENTRYPOINT ["./main_data_consumer"]

# #Copy whatever files you need from intermediate 
# COPY --from=intermediate /main_data_consumer ./


# #Add delve to current build
# COPY --from=intermediate /go/bin/dlv /
#Allow delve to run ./app in headless debug mode
# CMD ["/dlv", "--listen=:1234", "--headless=true", "--api-version=2", "exec", "./app"]

RUN CGO_ENABLED=0 go build -gcflags "all=-N -l" -o ./main_data_consumer .
CMD ./wait-for-it.sh crypto_db:5432 -t 0 -- ./main_data_consumer

# CMD ["dlv", "debug", "--listen=:4040", "--headless=true", "--api-version=2", "--log", "."]