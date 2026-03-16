# ATP Development Ruleset

- **Mục đích:** Bộ quy tắc vận hành development của ATP, dùng như gate/checklist bắt buộc xuyên suốt mọi phase.
- **Phạm vi:** Doctrine application, roadmap inheritance, version opening, slice execution, consolidation, freeze, close-out, README alignment, approval gates.
- **Trạng thái:** Active.
- **Loại:** Mandatory.

## 1. Mục đích và trục vận hành

### Rule 1.1
Mọi ATP development activity phải được đánh giá theo trục vận hành:

`requested user ⇄ ATP ⇄ products`

### Rule 1.2
ATP development chỉ được coi là hợp lệ khi thay đổi đang được đề xuất làm mạnh hơn ít nhất một phần của trục trên:

- quality của requested intent/context/review flow
- orchestration/control/governance capability của ATP
- product-facing execution/capability mediation của ATP

### Rule 1.3
ATP must not mở rộng internal mechanisms chỉ vì implementation convenience, local elegance, hay feature pressure, nếu thay đổi đó không có operating purpose rõ trên trục `requested user ⇄ ATP ⇄ products`.

## 2. Architecture rules

### Rule 2.1 Stable core
Stable core của ATP phải được giữ nguyên trừ khi có human-approved architectural decision rõ ràng.

Stable core bao gồm tối thiểu:

- repo/workspace boundary
- control-plane shape
- artifact lifecycle discipline
- human-gated flow
- source-of-truth order

### Rule 2.2 Modular boundaries
Mọi capability growth phải đi qua modular boundaries rõ ràng. Cross-boundary behavior phải được giải thích bằng contract hoặc documented seam, không được ẩn trong implicit coupling.

### Rule 2.3 Extension seams
Chỉ được mở extension seam tại những ranh giới có operating purpose rõ, ví dụ:

- adapters
- runtime materialization zones
- handoff / exchange contracts
- current-task contracts
- inspect surfaces

Không được tạo seam mới nếu chỉ để chứa future ideas chưa có planning basis.

### Rule 2.4 Composable capabilities
Capability mới phải là composable capability hoặc refinement của capability hiện có. Không được thêm feature rời rạc nếu không thể giải thích nó gắn vào capability bundle nào.

### Rule 2.5 Architecture-first
Architecture doctrine là north star. Roadmap, planning, implementation, và release must not override architecture vì implementation convenience.

### Rule 2.6 Market-aware but governance-controlled
ATP có thể học từ better modern patterns ngoài thị trường, nhưng chỉ được hấp thụ khi:

- pattern có lợi ích rõ cho trục `requested user ⇄ ATP ⇄ products`
- pattern không phá stable core
- pattern đi qua review, planning, verification, consolidation, freeze, close-out, và roadmap continuity

ATP must not sao chép literal product narratives, hype framing, hay generic no-code/platform language không khớp ATP architecture.

## 3. Roadmap rules

### Rule 3.1 Roadmap is mandatory
Roadmap là governance artifact bắt buộc. Mọi version của ATP phải có:

- product-roadmap context
- major-roadmap context
- version roadmap hoặc planning baseline tương ứng

### Rule 3.2 Roadmap layering
ATP roadmap phải giữ rõ ba tầng:

- product roadmap = strategic capability horizons
- major roadmap = major-family capability horizon
- version roadmap = execution horizon cho major family hiện tại

### Rule 3.3 Doctrine/history separation
Roadmap docs phải tách rõ:

- architecture doctrine
- roadmap direction
- version execution planning
- frozen historical facts

Frozen history chỉ được dùng như inheritance evidence, không được trở thành narrative chính của roadmap.

### Rule 3.4 Roadmap inheritance
Mỗi version roadmap mới phải kế thừa từ:

- previous frozen version
- previous consolidation baseline
- previous freeze close-out nếu đã tồn tại
- current major roadmap
- current product roadmap

### Rule 3.5 Major/minor transition
Minor version chỉ được mở khi phạm vi vẫn nằm trong current major capability horizon.

Major transition chỉ được coi là hợp lệ khi có evidence rằng:

- current major family đã đạt coherent maturity boundary
- next step đòi hỏi capability horizon mới
- next step không còn là refinement tự nhiên của current major

### Rule 3.6 Freeze continuity
Sau mỗi frozen version:

- freeze close-out document là bắt buộc
- roadmap continuity phải được cập nhật để version tiếp theo có inheritance chain rõ ràng

## 4. Version opening rules

### Rule 4.1 Preconditions
Trước khi mở một version mới, các artifact sau phải tồn tại hoặc đã được review:

- previous frozen version close-out
- previous integration review
- previous consolidation decision
- current product roadmap
- current major roadmap
- current architecture overview

### Rule 4.2 Planning baseline required
Implementation must not start nếu planning baseline của version chưa được chấp nhận.

### Rule 4.3 Planning baseline contents
Planning baseline của một version phải nêu rõ tối thiểu:

- version goal
- inherited direction
- capability gap
- must-have / good-to-have / deferred
- slice structure
- freeze criteria
- integration criteria

### Rule 4.4 Scope test
Trước khi mở version, phải kiểm tra và ghi rõ:

- phạm vi này còn thuộc current major hay không
- nó cải thiện đoạn nào của `requested user ⇄ ATP ⇄ products`
- nó không kéo ATP sang subsystem growth không có operating purpose

## 5. Slice execution rules

### Rule 5.1 Narrow slice rule
Mỗi slice phải narrow, testable, verifiable, và traceable tới version roadmap.

### Rule 5.2 Slice branch pre-implementation gate
Trước khi bắt đầu pass đầu tiên của bất kỳ slice mới nào, bắt buộc phải:

- tạo branch của slice mới
- switch vào đúng branch của slice mới
- verify current repo, current branch, và worktree đang đúng với slice đó
- chỉ sau đó mới được bắt đầu docs baseline, implementation, hoặc bounded execution pass của slice mới

Không được viết docs/baseline/implementation của slice mới khi vẫn đang đứng ở nhánh cũ.

Nếu phát hiện slice work đã bắt đầu trên sai branch, phải:

- dừng pass hiện tại
- sửa lineage / branch context trước
- verify lại repo / branch / worktree
- chỉ tiếp tục sau khi branch gate đã pass

Rule này là global pre-implementation gate cho mọi slice mới.

Trong ATP workflow hiện tại, cách hiện thực hóa ưu tiên cho gate này là:

```bash
gsgr start-slice <new-branch> <base-branch>
```

Nếu không dùng `start-slice`, flow tối thiểu phải là:

```bash
gsgr create-branch <new-branch> <base-branch>
gsgr publish-branch <new-branch>
gsgr status <new-branch>
```

Flow trên tồn tại để chốt đủ bốn bước bắt buộc:

- create branch
- switch vào branch mới
- verify đúng repo / branch / worktree
- rồi mới bắt đầu slice work

### Rule 5.3 In-scope / out-of-scope rule
Mỗi slice execution task phải ghi rõ:

- objective
- in-scope
- out-of-scope
- acceptance criteria

Không được ẩn extra work ngoài slice trong cùng change set.

### Rule 5.4 No hidden extra-slice work
Nếu một thay đổi vượt khỏi slice hiện tại, thay đổi đó phải:

- bị loại khỏi change set, hoặc
- được nêu explicit như strictly necessary fix với lý do rõ ràng

### Rule 5.5 Verification required
Mỗi slice phải có test hoặc verification evidence phù hợp với loại thay đổi:

- code/runtime changes -> tests hoặc explicit verification run
- docs/governance changes -> review pass + consistency check

### Rule 5.6 README alignment
Whenever anything changes at any level, README system ở level đó phải được review ngay.

Nếu README bị ảnh hưởng, nó phải được cập nhật trong cùng task/change set trừ khi human explicitly cho phép defer.

Nếu README không cần cập nhật, điều đó phải được nói rõ trong final report.

### Rule 5.7 Boundary rule during execution
Slice execution must not làm mờ boundary giữa:

- source repo và runtime workspace
- doctrine và history
- roadmap direction và implementation detail

## 6. Consolidation and freeze rules

### Rule 6.1 Integration review required
Trước khi freeze một version, phải có integration review đánh giá coherence của toàn bộ slices trong version đó.

### Rule 6.2 Consolidation decision required
Trước khi freeze, phải có consolidation decision document nêu rõ một trong ba trạng thái:

- ready to freeze/integrate
- freezeable với minor deferred cleanup
- not ready do blocker cụ thể

### Rule 6.3 Freeze criteria required
Không được freeze version nếu freeze criteria của version roadmap chưa được kiểm tra và kết luận rõ.

### Rule 6.4 Freeze close-out required
Sau khi version được freeze/tag:

- formal freeze close-out document phải được tạo
- close-out phải nêu rõ scope included, scope not included, verification/consolidation state, governance closure, follow-on direction

### Rule 6.5 Historical integrity
Close-out và consolidation docs phải dùng recoverable repo evidence. Không được invent unsupported historical claims.

## 7. Approval / high-risk action rules

### Rule 7.1 Human approval required
Các hành động sau require explicit user approval:

- merge vào `main`
- push lên `main`
- release tag / freeze tag
- destructive git operations
- rewrite hoặc replace historical/frozen artifacts

### Rule 7.2 Working-branch autonomy
Trên working branch hiện tại, các hoạt động sau có thể proceed tự động nếu nằm đúng task scope:

- chỉnh docs/code/tests trong phạm vi task
- chạy tests/verification cục bộ
- tạo branch-local planning/consolidation artifacts
- small consistency fixes strictly necessary cho task

### Rule 7.3 Escalation
Nếu thay đổi có thể:

- làm lệch architecture baseline
- vượt current slice/version scope
- thay đổi boundary semantics
- tạo ambiguity với frozen history

thì phải stop và nêu conflict thay vì tự mở scope.

## 8. Definition of Done rules

### Rule 8.1 Slice DoD
Một slice chỉ được coi là done khi:

- objective đã hoàn thành
- acceptance criteria đã được đáp ứng
- tests/verification phù hợp đã có
- README alignment ở location đã đổi đã được xử lý
- không còn hidden extra-slice work trong change set

### Rule 8.2 Version DoD
Một version chỉ được coi là done khi:

- planning baseline đã tồn tại và đã được thực hiện xong
- các slices required đã hoàn tất
- integration review đã có
- consolidation decision đã có
- freeze criteria đã pass

### Rule 8.3 Freeze DoD
Một frozen version chỉ được coi là fully closed khi:

- version đã integrate/tag theo governance hiện hành
- freeze close-out đã tồn tại
- roadmap continuity cho version sau không bị đứt

## 9. Exceptions and deviations

### Rule 9.1 Exception recording
Mọi deviation khỏi ruleset này phải được ghi rõ trong task output hoặc decision artifact với:

- rule bị lệch
- lý do
- phạm vi ảnh hưởng
- vì sao deviation là tạm thời hay cần promote thành rule change

### Rule 9.2 Temporary exceptions
Temporary exception must have exit condition rõ. Không được để exception mở vô thời hạn.

### Rule 9.3 Refinement of the ruleset
Ruleset này có thể được refine ở future version, nhưng refinement must not:

- phá historical continuity
- hạ thấp freeze discipline
- làm roadmap trở lại optional writing
- làm yếu README alignment rule
- làm ATP drift khỏi trục `requested user ⇄ ATP ⇄ products`

## 10. Minimum gate checklist

### Before opening a version

- previous freeze close-out reviewed
- previous consolidation reviewed
- current roadmap docs reviewed
- planning baseline accepted

### Before implementing a slice

- slice branch đã được tạo cho slice mới
- đã switch vào đúng slice branch
- repo / branch / worktree đã được verify lại
- slice objective rõ
- in-scope / out-of-scope rõ
- acceptance criteria rõ
- affected README locations identified

### Before calling a slice done

- verification completed
- README alignment completed or explicit not-needed statement prepared
- no hidden extra-slice work

### Before freezing a version

- integration review completed
- consolidation decision completed
- freeze criteria checked

### After freezing a version

- freeze close-out created
- roadmap continuity preserved
