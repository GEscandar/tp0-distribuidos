package common

import (
	"net"
	"os"
	"os/signal"
	"strings"
	"syscall"
	"time"

	"github.com/op/go-logging"
)

var log = logging.MustGetLogger("log")

// ClientConfig Configuration used by the client
type ClientConfig struct {
	ID            string
	ServerAddress string
	LoopAmount    int
	LoopPeriod    time.Duration
	MaxBatchSize  int
}

// Client Entity that encapsulates how
type Client struct {
	config ClientConfig
	conn   net.Conn
	closed bool
}

// NewClient Initializes a new client receiving the configuration
// as a parameter
func NewClient(config ClientConfig) *Client {
	client := &Client{
		config: config,
		closed: false,
	}
	s := make(chan os.Signal, 1)
	signal.Notify(s, syscall.SIGTERM, syscall.SIGINT)
	go func() {
		<-s
		log.Info("action: signal_received | result: in_progress")
		if client.conn != nil {
			_ = client.conn.Close()
		}
		client.closed = true
	}()
	return client
}

// CreateClientSocket Initializes client socket. In case of
// failure, error is printed in stdout/stderr and exit 1
// is returned
func (c *Client) createClientSocket() error {
	conn, err := net.Dial("tcp", c.config.ServerAddress)
	if err != nil {
		log.Criticalf(
			"action: connect | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
	}
	c.conn = conn
	return err
}

// StartClientLoop Send messages to the client until some time threshold is met
func (c *Client) StartClientLoop(bet Bet) {
	// There is an autoincremental msgID to identify every message sent
	// Messages if the message amount threshold has not been surpassed
	loader, err := NewBetsLoader(c.config.ID)
	if err != nil {
		log.Errorf("action: create_bets_loader | result: fail | error: %v", err)
		loader.Close()
		return
	}
	for msgID := 1; msgID <= c.config.LoopAmount && !c.closed; msgID++ {
		// Create the connection the server in every loop iteration. Send an
		err := c.createClientSocket()
		if err != nil {
			return
		}

		chunk, err := loader.NextChunk(c.config.MaxBatchSize)
		log.Infof("Sending chunk: %v", chunk)
		if err != nil {
			log.Errorf("action: load_bets | result: fail | error: %v", err)
			return
		}

		if len(chunk) == 0 {
			log.Infof("action: load_bets | result: success | client_id: %v", c.config.ID)
			break
		}
		_, err = SendBatch(c.conn, chunk)
		if err != nil {
			log.Errorf("action: send_message | result: fail | client_id: %v | error: %v",
				c.config.ID,
				err,
			)
			return
		}

		msg, err := RecvAck(c.conn)
		c.conn.Close()

		if err != nil {
			log.Errorf("action: receive_message | result: fail | client_id: %v | error: %v",
				c.config.ID,
				err,
			)
			return
		}

		arr := strings.Split(msg, ",")
		doc, num := arr[0], arr[1]
		log.Infof("action: apuesta_enviada | result: success | dni: %s | numero: %s",
			doc,
			num,
		)
	}
	log.Infof("action: loop_finished | result: success | client_id: %v", c.config.ID)
}
