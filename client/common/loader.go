package common

import (
	"encoding/csv"
	"fmt"
	"io"
	"os"
)

type BetsLoader struct {
	agency string
	file   *os.File
	reader *csv.Reader
}

func NewBetsLoader(agency string) (*BetsLoader, error) {
	path := fmt.Sprintf("/.data/agency-%s.csv", agency)

	file, err := os.Open(path)
	if err != nil {
		return nil, fmt.Errorf("failed to open file %s | %v", path, err)
	}

	reader := csv.NewReader(file)
	reader.FieldsPerRecord = 0

	return &BetsLoader{
		agency: agency,
		file:   file,
		reader: reader,
	}, nil

}

func (b *BetsLoader) NextChunk(size int) ([]Bet, error) {
	var bets []Bet

	for i := 0; i < size; i++ {
		line, err := b.reader.Read()
		if err != nil {
			if err == io.EOF {
				break
			}
			return nil, fmt.Errorf("failed to read from file | %v", err)
		}

		bet, err := NewBet(
			b.agency,
			line[0],
			line[1],
			line[2],
			line[3],
			line[4],
		)
		if err != nil {
			return nil, fmt.Errorf("failed to create bet | %v", err)
		}

		bets = append(bets, bet)
	}

	return bets, nil
}

func (b *BetsLoader) Close() {
	_ = b.file.Close()
}
