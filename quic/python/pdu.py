
import json

MSG_TYPE_DATA = 0x00
MSG_TYPE_ACK = 0x01

class PDU:
    def __init__(self, message_type: int, message: str):
        self.mtype = message_type
        self.msg = message
        self.len = len(self.msg)
        
    def to_json(self):
        return json.dumps(self.__dict__)    
    
    @staticmethod
    def from_json(json_str):
        return PDU(**json.loads(json_str))
    
    def to_bytes(self):
        return json.dumps(self.__dict__).encode('utf-8')
    
    @staticmethod
    def from_bytes(json_bytes):
        return PDU(**json.loads(json_bytes.decode('utf-8')))    