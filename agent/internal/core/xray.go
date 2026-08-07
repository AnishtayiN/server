package core

import (
	"context"
	"fmt"
	"log"
	"time"

	"github.com/xtls/xray-core/app/proxyman/command"
	"github.com/xtls/xray-core/common/protocol"
	"github.com/xtls/xray-core/common/serial"
	"github.com/xtls/xray-core/proxy/vless"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
)

type XrayManager struct {
	conn *grpc.ClientConn
}

func NewXrayManager(apiAddr string) (*XrayManager, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	conn, err := grpc.DialContext(ctx, apiAddr,
		grpc.WithTransportCredentials(insecure.NewCredentials()),
		grpc.WithBlock())
	if err != nil {
		return nil, fmt.Errorf("gRPC connect failed: %w", err)
	}

	log.Printf("Connected to Xray API at %s", apiAddr)
	return &XrayManager{conn: conn}, nil
}

func (m *XrayManager) AddUser(ctx context.Context, inboundTag, email, uuid string) error {
	client := command.NewHandlerServiceClient(m.conn)
	
	user := &protocol.User{
		Level: 0,
		Email: email,
		Account: serial.ToTypedMessage(&vless.Account{
			Id:   uuid,
			Flow: "xtls-rprx-vision",
		}),
	}

	req := &command.AddUserRequest{
		InboundTag: inboundTag,
		User:       user,
	}

	_, err := client.AddUser(ctx, req)
	if err != nil {
		return fmt.Errorf("xray AddUser RPC failed: %w", err)
	}
	
	log.Printf("User injected: %s -> %s", email, inboundTag)
	return nil
}

func (m *XrayManager) RemoveUser(ctx context.Context, inboundTag, email string) error {
	client := command.NewHandlerServiceClient(m.conn)
	req := &command.RemoveUserRequest{
		InboundTag: inboundTag,
		Email:      email,
	}
	_, err := client.RemoveUser(ctx, req)
	return err
}

func (m *XrayManager) Close() {
	if m.conn != nil {
		m.conn.Close()
	}
}
