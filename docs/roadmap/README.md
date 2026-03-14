# Roadmap ATP

- **Mục đích:** Lớp roadmap active cho ATP; điều phối continuity giữa product direction, major family, version planning, consolidation, freeze, và close-out.
- **Phạm vi:** Product roadmap, major roadmap, version roadmap, và inheritance rules.
- **Trạng thái:** Active.

## Roadmap layering

ATP dùng roadmap 3 tầng:

- **Product roadmap** — mô tả long-range evolution model của ATP
- **Major roadmap** — mô tả capability horizon của một major family như `v0`, `v1`, `v2`
- **Version roadmap** — mô tả goal, scope, slices, freeze criteria, và integration criteria của một version cụ thể

## Quy tắc inheritance

Mỗi version roadmap mới phải kế thừa từ:

- previous frozen version
- consolidation baseline của version trước đó
- freeze close-out của version trước đó khi đã tồn tại
- major roadmap và product roadmap đang active

## Quy tắc governance

Roadmap không phải optional writing. Trong ATP:

- mỗi version phải có planning baseline
- implementation không nên đi trước planning baseline acceptance
- freeze không nên diễn ra nếu chưa có consolidation decision
- sau mỗi version đã freeze, formal freeze close-out là bắt buộc
- roadmap continuity là một phần của release/documentation governance

## Tài liệu trong miền

- `ATP_Product_Roadmap.md` — product-level direction và doctrine continuity
- `majors/` — roadmap cho từng major family
- `versions/` — roadmap cho từng version cụ thể
