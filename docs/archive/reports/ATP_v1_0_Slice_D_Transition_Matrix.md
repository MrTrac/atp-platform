# ATP v1.0 Slice D Transition Matrix

## 1. Mục đích

Matrix này chuẩn hóa transition discipline của `ATP v1.0 Slice D` theo cách audit-friendly và usable cho implementation, review, consolidation, và freeze path.

Matrix này không phải workflow engine table. Đây là control matrix để xác định:

- decision type nào được dùng
- authority nào là bắt buộc
- preconditions nào phải đạt
- next state nào được phép hoặc bị cấm
- evidence nào là tối thiểu
- khi nào phải `hold`, `escalate`, hoặc `loop-back`

## 2. Transition matrix

| Source State | Decision Type | Required Authority | Preconditions | Allowed Next State | Forbidden Next State | Required Evidence | Hold Condition | Escalation Trigger | Failure Handling | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| `approved_continuity_ready` | `observational decision` | observational authority | state explicit, source refs complete | `approved_continuity_ready` retained as observed state | any binding transition state | source state ref, observation rationale | nếu observation chưa đủ trace context | nếu observation bị dùng để justify binding move | classify as non-binding observation only | observation không cho phép move |
| `approved_continuity_ready` | `advisory decision` | advisory authority | state valid, rationale explicit | `transition_candidate_ready` ở mức advisory only | any committed binding resulting state | source state ref, advisory rationale, proposed move | nếu advisory thiếu evidence cho recommendation | nếu advisory bị dùng thay binding authority | downgrade to advisory-only record | advisory được trace nhưng không tự mở permission |
| `approved_continuity_ready` | `conditional binding decision` | conditional binding authority | state valid, authority valid, evidence sufficient, no active block | `allowed_transition_ready` hoặc `conditional_transition_ready` | `blocked_transition`, `deferred_transition`, hoặc unrelated closed state nếu không có basis | state ref, authority ref, rationale, evidence set, requested move | nếu thiếu một phần evidence bổ sung nhỏ | nếu requested move vượt matrix hoặc đụng scope boundary | convert to hold hoặc block tùy mức thiếu hụt | đây là con đường chuẩn để move tiếp |
| `approved_continuity_ready` | `blocking decision` | blocking authority | state explicit, blocking basis explicit | `blocked_transition` | direct allowed move | blocking rationale, conflict evidence, authority ref | nếu block basis chưa đủ mạnh | nếu block ảnh hưởng governance line rộng | hold current state and open escalation | block có thể xảy ra dù source state nhìn hợp lệ |
| `held_continuity_pending` | `observational decision` | observational authority | state explicit | `held_continuity_pending` retained | any binding ready/closed move | source state ref, observation note | nếu state description còn mơ hồ | nếu pending state có inconsistent prior trace | preserve pending state | chỉ ghi nhận tình trạng, không quyết move |
| `held_continuity_pending` | `advisory decision` | advisory authority | pending state traceable, proposed clarification explicit | `conditional_transition_ready` ở mức advisory only hoặc `loop_back_required` | direct final allowed move | advisory rationale, unresolved conditions, proposed evidence | nếu clarification path chưa đủ rõ | nếu pending state kéo dài vượt acceptable control boundary | recommend loop-back or escalation | advisory ở đây thường dẫn tới clarify path |
| `held_continuity_pending` | `conditional binding decision` | conditional binding authority | pending cause understood, required missing evidence identified, supplemental basis available | `conditional_transition_ready`, `deferred_transition`, `loop_back_required` | direct `allowed_transition_ready` nếu unresolved condition còn active | state ref, authority ref, supplemental evidence, rationale | nếu supplemental evidence chưa hoàn tất | nếu pending condition không thể resolve ở current authority | defer or escalate | pending state hiếm khi đi thẳng sang allowed move |
| `held_continuity_pending` | `blocking decision` | blocking authority | active risk or invalidity detected | `blocked_transition` | direct allowed move | blocking basis, risk evidence, authority ref | nếu risk chưa đủ confirmed | nếu pending state liên quan governance conflict | hold then escalate | block bảo vệ khỏi move sớm |
| `deferred_continuity_deferred` | `observational decision` | observational authority | deferred state explicit | `deferred_continuity_deferred` retained | any binding move | state ref, defer reason recap | nếu defer reason không rõ | nếu deferred state lặp mà không có rationale refresh | keep deferred state and require trace cleanup | observation không tháo defer |
| `deferred_continuity_deferred` | `advisory decision` | advisory authority | deferred basis traceable, proposed revisit path explicit | `loop_back_required` hoặc `conditional_transition_ready` ở mức advisory | direct allowed move | defer rationale, revisit suggestion, source refs | nếu revisit path chưa đủ concrete | nếu defer kéo dài thành uncontrolled stall | escalate for re-qualification | advisory chỉ chuẩn bị revisit path |
| `deferred_continuity_deferred` | `conditional binding decision` | conditional binding authority | defer basis reviewed, current evidence refreshed, authority valid | `conditional_transition_ready`, `deferred_transition`, `loop_back_required` | direct allowed move khi refresh chưa đủ | refreshed evidence, authority ref, rationale, requested transition | nếu refresh evidence chưa đủ | nếu decision mâu thuẫn prior defer basis lớn | revert to defer or escalate | defer cần refresh discipline trước khi move |
| `deferred_continuity_deferred` | `blocking decision` | blocking authority | blocking basis explicit | `blocked_transition` | direct allowed move | blocking rationale, authority ref, conflict evidence | nếu blocking basis chưa ổn định | nếu block tạo governance conflict với prior binding path | hold and escalate | defer có thể chuyển sang block nếu phát hiện invalid basis |
| `rejected_continuity_closed` | `observational decision` | observational authority | closed state explicit | `rejected_continuity_closed` retained | any reopening move | source state ref, observation rationale | nếu closed basis chưa traceable đủ | nếu có dấu hiệu reopened semantics bị đưa vào sai scope | preserve closed state | closed state không tự reopen |
| `rejected_continuity_closed` | `advisory decision` | advisory authority | closed state explicit, rationale explicit | advisory note only; no transition | any reopened move | source refs, advisory note | nếu advisory cố đề xuất reopen không có basis | nếu có xung đột với closure discipline | reject advisory transition request | advisory trên closed state chỉ mang tính commentary |
| `rejected_continuity_closed` | `conditional binding decision` | conditional binding authority | only if explicit loop-back basis exists and matrix allows review return | `loop_back_required` only | direct ready state, direct allowed move | closure refs, explicit exception basis, authority ref, rationale | nếu exception basis chưa đủ | nếu reopen attempt không có strict basis | block and escalate | closed path chỉ loop-back trong exception path rất hẹp |
| `rejected_continuity_closed` | `blocking decision` | blocking authority | closure discipline active | `blocked_transition` retained | any reopen move without exception basis | closure evidence, blocking rationale, authority ref | nếu closure evidence còn thiếu | nếu exception claim được nêu nhưng không đủ grounds | maintain block and request escalation | đây là path mặc định của closed state |

## 3. Cách đọc matrix

- `Source State` luôn bắt nguồn từ Slice C continuity state.
- `Decision Type` phải dùng đúng decision classes của Slice D.
- `Required Authority` quyết định decision có thể tạo effect gì.
- `Allowed Next State` phải được hiểu như control result hoặc resulting move ở mức bounded, không phải workflow subsystem.
- `Forbidden Next State` dùng để chặn drift và chặn transition không có basis.
- `Hold Condition` và `Escalation Trigger` giúp ATP không lặng lẽ đi tiếp khi basis chưa đủ.

## 4. Matrix guardrails

Matrix này phải được dùng với các guardrails sau:

- advisory không được diễn giải thành binding
- observational không được phép tạo permission
- blocked transition không được “lách” bằng wording mềm hơn
- loop-back chỉ là control result, không phải recovery engine
- conditional transition không được finalize như allowed transition nếu preconditions chưa hoàn tất

## 5. Kết luận

Transition matrix này là operational discipline baseline của Slice D. Nó cung cấp khung đủ thực dụng để ATP kiểm soát:

- state nào được xem xét
- decision nào hợp lệ
- authority nào là bắt buộc
- transition nào được phép, có điều kiện, defer, block, hay loop-back

Mọi implementation hoặc review của Slice D phải bám matrix này thay vì suy diễn transition tùy ý.
