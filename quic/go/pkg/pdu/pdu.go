package pdu

import (
	"encoding/json"
	"fmt"
)

const (
	// PDU types
	TYPE_DATA = 0
	TYPE_ACK  = 1

	MAX_PDU_SIZE = 1024
)

type PDU struct {
	Mtype uint8  `json:"mtype"`
	Len   uint32 `json:"len"`
	Data  []byte `json:"data"`
}

func MakePduBuffer() []byte {
	return make([]byte, MAX_PDU_SIZE)
}

func NewPDU(mtype uint8, data []byte) *PDU {
	return &PDU{
		Mtype: mtype,
		Len:   uint32(len(data)),
		Data:  data,
	}
}

func (pdu *PDU) GetTypeAsString() string {
	switch pdu.Mtype {
	case TYPE_DATA:
		return "***DATA"
	case TYPE_ACK:
		return "****ACK"
	default:
		return "UNKNOWN"
	}
}

func (pdu *PDU) ToJsonString() string {
	jsonData, err := json.MarshalIndent(pdu, "", "    ")
	if err != nil {
		fmt.Println("Error marshaling JSON:", err)
		return "{}"
	}

	return string(jsonData)
}

func PduFromBytes(raw []byte) (*PDU, error) {
	pdu := &PDU{}
	json.Unmarshal(raw, pdu)
	return pdu, nil
}

func PduToBytes(pdu *PDU) ([]byte, error) {
	return json.Marshal(pdu)
}
