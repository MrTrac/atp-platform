"""Constants of AOKP `synthesis/suggestion-engine.ts` and `synthesis/citation-grounding.ts` — GENERATED, do not edit.

Source: AOKP commit 51b1139b120de69969f4e87f760b62dfca3bf15a, read out of the TypeScript by tests/fixtures/synthesis_v2/make_golden.ts and written here by gen_python_data.py.
"""

from __future__ import annotations

# topic -> follow-up suggestions (Vietnamese text as in AOKP)
TOPIC_SUGGESTIONS: dict[str, list[dict[str, str]]] = {
    "radar": [
        {
            "question": "Radar này sử dụng giao thức ASTERIX category nào?",
            "rationale": "Hiểu rõ data format truyền nhận"
        },
        {
            "question": "Khi radar mất kết nối, hệ thống fallback như thế nào?",
            "rationale": "Đảm bảo an toàn vận hành"
        },
        {
            "question": "Radar này kết nối với những subsystem nào khác?",
            "rationale": "Hiểu dependency graph"
        }
    ],
    "fdp": [
        {
            "question": "FDP nhận dữ liệu surveillance từ nguồn nào?",
            "rationale": "Hiểu data flow vào FDP"
        },
        {
            "question": "FDP xử lý track correlation như thế nào?",
            "rationale": "Hiểu core processing logic"
        }
    ],
    "safety_net": [
        {
            "question": "Các tham số FAT cụ thể của safety net này là gì?",
            "rationale": "Chi tiết cấu hình vận hành"
        },
        {
            "question": "Safety net này hoạt động ở chế độ nào (warning/alarm)?",
            "rationale": "Hiểu mức độ can thiệp"
        }
    ],
    "network": [
        {
            "question": "VLAN scheme cho kết nối này được phân chia như thế nào?",
            "rationale": "Hiểu network segmentation"
        },
        {
            "question": "Redundancy plan cho đường truyền này là gì?",
            "rationale": "Đánh giá fault tolerance"
        }
    ],
    "firewall": [
        {
            "question": "Firewall này hoạt động ở chế độ air-gap hay online?",
            "rationale": "Hiểu security posture"
        },
        {
            "question": "Quy trình cập nhật signature cho firewall offline?",
            "rationale": "Bảo trì an ninh mạng"
        }
    ],
    "rack": [
        {
            "question": "Rack này chứa những thiết bị gì?",
            "rationale": "Hiểu physical layout"
        },
        {
            "question": "Nguồn điện (power feed) cho rack này từ đâu?",
            "rationale": "Hiểu power topology"
        }
    ],
    "twr": [
        {
            "question": "TWR site này kết nối WAN qua thiết bị nào?",
            "rationale": "Hiểu remote connectivity"
        },
        {
            "question": "Các dịch vụ ATM nào được cung cấp tại TWR site này?",
            "rationale": "Hiểu service scope"
        }
    ]
}

# (topic, JavaScript regex SOURCE, JavaScript flags) in AOKP's order; compiled with JS semantics by suggestion_engine.py
TOPIC_PATTERN_SOURCES: list[tuple[str, str, str]] = [
    ("radar", "\\b(radar|smrdr|psr|ssr|mlat|ads-?b)\\b", "i"),
    ("fdp", "\\b(fdp|flight\\s*data|xử\\s*lý\\s*chuyến\\s*bay)\\b", "i"),
    ("safety_net", "\\b(safety\\s*net|stca|msaw|apw|apm|ntz|clam)\\b", "i"),
    ("network", "\\b(network|mạng|vlan|wan|ethernet|ip|kết\\s*nối)\\b", "i"),
    ("firewall", "\\b(firewall|fortinet|fg-70f|fortimanager|cyber)\\b", "i"),
    ("rack", "\\b(rack|rs[a-z]*\\d+|rp[a-z]*\\d+|tủ)\\b", "i"),
    ("twr", "\\b(twr|tower|đài\\s*kiểm\\s*soát|remote\\s*site)\\b", "i"),
]

GENERIC_SUGGESTIONS: list[dict[str, str]] = [
    {
        "question": "Hệ thống này có dependency nào cần lưu ý?",
        "rationale": "Hiểu mối liên hệ trong hệ thống"
    },
    {
        "question": "Có thay đổi nào gần đây ảnh hưởng đến vấn đề này?",
        "rationale": "Nắm bắt tình trạng mới nhất"
    }
]

# NOTE: these are NFC strings, but the grounding tokenizer decomposes text (NFKD) before comparing, so the Vietnamese ones never match a token. AOKP behaves the same; kept as is.
STOPWORDS: frozenset[str] = frozenset([
    "a",
    "an",
    "the",
    "and",
    "or",
    "of",
    "to",
    "in",
    "on",
    "for",
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "being",
    "this",
    "that",
    "these",
    "those",
    "it",
    "its",
    "as",
    "at",
    "by",
    "with",
    "từ",
    "của",
    "và",
    "hoặc",
    "là",
    "có",
    "các",
    "một",
    "những",
    "trong",
    "ngoài",
    "cho"
])

GROUNDED_AT: float = 0.18
WEAK_AT: float = 0.08
