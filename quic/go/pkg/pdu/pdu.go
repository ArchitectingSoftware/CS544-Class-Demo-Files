package pdu

import "errors"

const (
	// PDU types
	TYPE_DATA = 0
	TYPE_ACK  = 1
)

type PDU struct {
	mtype uint8
	len   uint32
	data  []byte
}

func NewPDU(mtype uint8, data string) *PDU {
	return &PDU{
		mtype: mtype,
		len:   uint32(len(data)),
		data:  []byte(data),
	}
}

func (pdu *PDU) GetType() uint8 {
	return pdu.mtype
}

func (pdu *PDU) SetType(mtype uint8) {
	pdu.mtype = mtype
}

func (pdu *PDU) SetData(msg string) {
	pdu.data = []byte(msg)
	pdu.len = uint32(len(pdu.data))
}

func (pdu *PDU) GetTypeAsString() string {
	switch pdu.mtype {
	case TYPE_DATA:
		return "***DATA"
	case TYPE_ACK:
		return "****ACK"
	default:
		return "UNKNOWN"
	}
}

func (pdu *PDU) GetLen() uint32 {
	return pdu.len
}

func (pdu *PDU) GetData() string {
	return string(pdu.data)
}

func PduFromBytes(raw []byte) (*PDU, error) {
	if len(raw) < 5 {
		return nil, errors.New("PDU too short")
	}
	pdu := &PDU{
		mtype: raw[0],
		len:   uint32(raw[1])<<24 | uint32(raw[2])<<16 | uint32(raw[3])<<8 | uint32(raw[4]),
		data:  raw[5:],
	}
	if len(pdu.data) != int(pdu.len) {
		return nil, errors.New("PDU length mismatch")
	}
	return pdu, nil
}

func PduToBytes(pdu *PDU) []byte {
	raw := make([]byte, 5+pdu.len)
	raw[0] = pdu.mtype
	raw[1] = byte(pdu.len >> 24)
	raw[2] = byte(pdu.len >> 16)
	raw[3] = byte(pdu.len >> 8)
	raw[4] = byte(pdu.len)
	copy(raw[5:], pdu.data)
	return raw
}
