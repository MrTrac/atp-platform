# Contracts

`adapters/contracts` chua contract seed cho ATP M6.

M6 dung contracts de khoa naming giua core va adapter:

- `execution_adapter` cho execution path
- `handoff_adapter` cho handoff path
- `artifact_adapter` cho artifact shaping path

Contracts trong v0 chi la interface nhe:

- input la ATP-native dict
- output la dict da du de normalize tiep
- khong co framework abstraction hay registration engine
