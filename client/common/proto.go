package common

import (
	"encoding/binary"
	"fmt"
	"io"
	"math"
	"net"
	"strconv"
)

type Bet struct {
	Agency    int
	Name      string
	Surname   string
	DocNumber int
	BirthDate string
	Number    int
}

func NewBet(agency string, name string, surname string, docNumber string, birthDate string, betNumber string) (Bet, error) {
	agencyNumber, err := strconv.Atoi(agency)
	if err != nil {
		return Bet{}, fmt.Errorf("error parsing agency | %v", err)
	}

	document, err := strconv.Atoi(docNumber)
	if err != nil {
		return Bet{}, fmt.Errorf("error parsing document | %v", err)
	}

	number, err := strconv.Atoi(betNumber)
	if err != nil {
		return Bet{}, fmt.Errorf("error parsing number | %v", err)
	}

	return Bet{
		Agency:    agencyNumber,
		Name:      name,
		Surname:   surname,
		DocNumber: document,
		BirthDate: birthDate,
		Number:    number,
	}, nil
}

func SerializeBet(bet Bet) ([]byte, error) {
	message := fmt.Sprintf("%d,%s,%s,%d,%s,%d", bet.Agency, bet.Name, bet.Surname, bet.DocNumber, bet.BirthDate, bet.Number)
	if len(message) > math.MaxUint16 {
		return nil, fmt.Errorf("message too long")
	}

	buf := make([]byte, 2) // message size buffer
	binary.BigEndian.PutUint16(buf, uint16(len(message)))
	data := append(buf, []byte(message)...)
	return data, nil
}

func Sendall(conn net.Conn, data []byte) (int, error) {
	sent := 0
	for sent < len(data) {
		n, err := conn.Write(data[sent:])
		if err != nil {
			return sent, fmt.Errorf("failed to send message | %v", err)
		}
		sent += n
	}
	return sent, nil
}

func SendBet(conn net.Conn, bet Bet) (int, error) {
	data, err := SerializeBet(bet)
	if err != nil {
		return 0, fmt.Errorf("failed to serialize bet | %v", err)
	}

	return Sendall(conn, data)
}

func SendBatch(conn net.Conn, bets []Bet) (int, error) {
	bytes := make([]byte, 2)
	binary.BigEndian.PutUint16(bytes, uint16(len(bets)))

	for _, bet := range bets {
		betBytes, err := SerializeBet(bet)
		if err != nil {
			return 0, fmt.Errorf("failed to serialize bet | %v", err)
		}

		bytes = append(bytes, betBytes...)
	}
	return Sendall(conn, bytes)
}

func RecvAck(conn net.Conn) (string, error) {
	buf := make([]byte, 2)
	err := binary.Read(conn, binary.BigEndian, buf)
	if err != nil {
		return "", fmt.Errorf("error receiving message")
	}
	msg_size := binary.BigEndian.Uint16(buf)
	buf = make([]byte, msg_size)

	_, err = io.ReadFull(conn, buf)
	if err != nil {
		return "", fmt.Errorf("error receiving message")
	}

	return string(buf), nil
}
