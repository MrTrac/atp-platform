# Runbook ATP v0

ATP v0 hiện đã khép kín baseline đến M8 theo repo-local flow.

## Flow vận hành v0

1. tiếp nhận request file
2. normalize request
3. classify request
4. resolve product
5. package context
6. prepare và select route
7. thực thi local command nếu route hỗ trợ
8. capture artifact, validation, và review
9. chạy approval gate summary
10. tạo handoff output và finalization summary
11. quyết định `close-run` hoặc `continue-run`
12. xem final summary trên CLI

## Đặc điểm vận hành hiện tại

- Approval Gate là manual-first, rule-based summary
- Finalization là dict-based summary, không có external side effect
- Handoff hiện là ATP-side summary/handoff structures
- chưa ghi production runtime outputs đầy đủ vào `SOURCE_DEV/workspace`

## Mục tiêu của runbook này

Runbook này dùng để mô tả:
- ATP v0 đang vận hành ở mức nào
- cái gì đã được triển khai thật
- cái gì vẫn còn deferred
- operator nên kỳ vọng gì khi chạy ATP v0
