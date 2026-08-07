FROM golang:1.21-alpine AS builder
WORKDIR /build
COPY . .
RUN go mod download
RUN CGO_ENABLED=0 go build -o anishtayin-agent ./main.go

FROM alpine:latest
WORKDIR /opt/agent
COPY --from=builder /build/anishtayin-agent .
ENTRYPOINT ["./anishtayin-agent"]
