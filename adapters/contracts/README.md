# Contracts

`adapters/contracts` chứa contract seeds cho ATP M6.

Contracts dùng để khóa naming giữa core và adapter:

- `execution_adapter` cho execution path
- `handoff_adapter` cho handoff path
- `artifact_adapter` cho artifact shaping path

Contracts trong v0 chỉ là interface nhẹ:

- input la ATP-native dict
- output la dict da du de normalize tiep
- không có framework abstraction hay registration engine
