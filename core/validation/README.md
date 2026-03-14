# Validation

`core/validation` chứa implementation M7 cho validation summary và minimal review input.

Validation hiện hành có nghĩa:

- kiểm tra execution result có đủ field tối thiểu
- đánh dấu `passed`, `failed`, hoặc `incomplete`
- tạo summary nhẹ để phục vụ review decision

Không thuộc scope:

- semantic validation sau execution
- human review UI
- approval workflow
