# ATP Development Stages

- **Mục đích:** Orientation file cho stage-based development roadmap của ATP.
- **Phạm vi:** Các capability/maturity stages của ATP theo logic dài hạn, tách biệt với version roadmap.
- **Trạng thái:** Active.

## Stage roadmap dùng để làm gì

Stage roadmap mô tả ATP theo từng development stage:

- ATP có hình hài gì ở stage đó
- ATP trả lời nhu cầu thực tế nào ở stage đó
- ATP làm được gì và chưa làm được gì ở stage đó
- điều kiện nào đủ để sang stage tiếp theo

Stage roadmap không thay thế:

- architecture doctrine
- major roadmap
- version roadmap
- freeze close-out

Nó là lớp practical maturity map nằm giữa product roadmap dài hạn và version roadmap ngắn hạn.

## Quan hệ với các roadmap layer khác

- `../ATP_Product_Roadmap.md` — strategic capability horizons dài hạn
- `../majors/` — major-family roadmap
- `../versions/` — version roadmap theo từng release step
- `ATP_Development_Stage_Roadmap.md` — stage-based map mô tả ATP trông như thế nào ở từng maturity stage
- `ATP_Practical_Milestone_Map.md` — lineage map vận hành cho continuity từ `v0.1` tới current milestone

## Quan hệ với governance

- `../../governance/framework/ATP_Version_Lineage_and_Documentation_Continuity_Rule.md` — rule bắt buộc cho lineage và documentation continuity

Stage docs không thay rule này. Khi cần theo dõi milestone continuity cụ thể, dùng practical milestone map.

## Quy tắc sử dụng

- dùng stage roadmap để kiểm tra ATP đang ở đâu trong capability progression
- dùng version roadmap để quyết định version hiện tại cần unlock gì
- không dùng stage roadmap như release notes hay implementation backlog
