package common

import (
	"encoding/binary"
	"fmt"
	"math"
	"net"
)

type Bet struct {
	Agency    int
	Name      string
	Surname   string
	DocNumber int
	BirthDate string
	Number    int
}

func SendBet(conn net.Conn, bet Bet) (int, error) {
	message := fmt.Sprintf("%d,%s,%s,%d,%s,%d", bet.Agency, bet.Name, bet.Surname, bet.DocNumber, bet.BirthDate, bet.Number)
	if len(message) > math.MaxUint16 {
		return 0, fmt.Errorf("message too long")
	}

	sent := 0
	buf := make([]byte, 2) // message size buffer
	binary.BigEndian.PutUint16(buf, uint16(len(message)))
	data := append(buf, []byte(message)...)
	for sent < len(data) {
		n, err := conn.Write(data[sent:])
		if err != nil {
			return 0, fmt.Errorf("failed to send message")
		}
		sent += n
	}
	return sent, nil
}
