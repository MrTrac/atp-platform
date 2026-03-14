# Version Roadmaps

- **Mục đích:** Orientation file cho các version-roadmap documents của ATP.
- **Phạm vi:** Goal, scope, slices, freeze criteria, integration criteria, và inheritance discipline theo từng version.
- **Trạng thái:** Active.

## Version roadmap dùng để làm gì

Mỗi version roadmap phải mô tả tối thiểu:

- roadmap position của version đó trong current major family
- version goal
- inheritance từ previous frozen version
- capability gap mà version đó cần address
- điều version đó cần unlock cho major family
- execution horizon mà version đó đang đảm nhiệm
- version đó cải thiện trục `requested user ⇄ ATP ⇄ products` như thế nào
- must-have direction
- good-to-have direction nếu còn capacity
- deferred areas
- slice structure
- freeze criteria
- integration criteria

## Quy tắc inheritance

Mỗi version roadmap mới phải bắt đầu từ:

- previous frozen version close-out
- previous consolidation baseline
- major roadmap đang active
- product roadmap đang active

Không nên đi vào implementation nếu chưa có planning baseline được chấp nhận.

## Quy tắc release continuity

- version roadmap -> planning reports -> slice implementation -> consolidation -> freeze -> close-out
- không bỏ qua consolidation decision
- không bỏ qua freeze close-out
- roadmap continuity là bắt buộc, không phải optional documentation
