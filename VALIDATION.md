# Validation record / 검증 기록

**Review date: 2026-10-15 (Asia/Seoul)**

## Scope

This record concerns the working-folder snapshot added to this repository: four numbered root scripts and eleven Python variants in `bck/`. The five previously committed unnumbered scripts were retained and were not execution-tested in this review. Input workbooks and generated reports remain local.

The publication preserves the Python sources byte-for-byte. Documentation and candidate dependency constraints do not imply a code repair or a successful reproduction.

## Source checks

- All 15 source files were parsed with Python's `ast.parse` (Python 3.13.9).
- No syntax errors were raised.
- Two historical files, `bck/3.건수통계_특보_SP제외.py` and `bck/3.건수통계_특보_SP,SS제외.py`, emitted invalid-escape warnings for older Windows path text.
- Source review identified relative workbook reads, row/index-aligned comparisons, fixed output filenames, EUC-KR CSV exports, legacy `to_excel(..., encoding=...)`, suppressed warnings, and hardcoded paths in some archive variants.

## Local input inspection

Inspection used Python 3.12.14, pandas 3.0.1, NumPy 2.3.5, and openpyxl 3.1.5. Each existing pair was loaded from its first worksheet.

| Prefix | Service (`mod`) rows | Prediction (`org`) rows | Selected ordered identifiers aligned? |
| :---: | ---: | ---: | :---: |
| `sd` | 362 | 362 | Yes |
| `sf` | 7,560 | 7,560 | Yes |
| `sk` | 2,520 | 2,520 | Yes |
| `sr` | 520 | 520 | Yes |
| `tl` | 427 | 427 | Yes |
| `sp` | Absent | Absent | Not assessed |
| `ss` | 1,080 | 1,080 | Yes |

Compared fields were `생산일`/`권역`/`지역` for `sd`, `sf`, `tl`, and `ss`; `생산일`/`항로명`/`선박명` for `sk`; and `생산일`/`구분`/`지역` for `sr`.

These checks do not establish full record identity. Most date/location combinations repeat, consistent with the presence of finer forecast dimensions. Forecast date/time, species, code fields, and other applicable dimensions must be reviewed before adopting a unique-key or deduplication rule. No business-level duplicate-removal decision was made.

## Isolated execution

Each current script was run separately with copies of the available input workbooks. Existing local reports were not overwritten. The environment was the same Python 3.12.14 / pandas 3.0.1 environment described above; Jinja2 was unavailable.

| Script | Exit | First observed blocking failure |
| :--- | :---: | :--- |
| `0.특이사항_발생일및비중(수정).py` | 1 | `pandas.errors.MergeError`: repeated merges produced conflicting `해상특보_x`, `해상특보_y`, `육상특보_x`, and `육상특보_y` columns. |
| `1.건수통계(수정).py` | 1 | `AttributeError`: the `.style` accessor requires Jinja2. |
| `2.건수통계_모델(수정).py` | 1 | `AttributeError`: the `.style` accessor requires Jinja2. |
| `3.건수통계_특보(수정).py` | 1 | `AttributeError`: the `.style` accessor requires Jinja2. |

The attempts produced no new CSV, HTML, or report XLSX files before failure. These are the first observed failures, not an exhaustive defect list. Supplying Jinja2 alone does not demonstrate compatibility; later operations still require review. The candidate Python 3.10–3.11 / pandas 1.5.3 dependency set was not installed or tested.

## Validation still required

1. Establish and record a working dependency environment, then run every intended activity path.
2. Confirm complete input schemas, types, placeholders, missingness, and record identities.
3. Check date-level aggregation and merge cardinality, especially repeated location names and warning columns.
4. Reconcile all output totals and denominator definitions to independently calculated reference counts.
5. Test zero-change, absent-activity, missing-value, and overlapping-warning cases.
6. Compare regenerated outputs with an approved reference report; review encoding in Korean Excel and HTML consumers.

No statistical accuracy, complete report reproduction, observational forecast accuracy, or production readiness is certified by this review.

---

## 한국어

이번 검증 대상은 작업 폴더에서 추가한 주 실행 코드 4개와 `bck/`의 이전 코드 11개입니다. 기존 레포의 번호 없는 코드 5개는 보존했으며 실행 검증하지 않았습니다. Python 원본은 그대로 게시합니다.

**확인 결과:**

- Python 3.13.9에서 15개 파일의 AST 문법 검사에 성공했습니다. 과거 코드 2개에서 Windows 경로의 이스케이프 관련 경고가 발생했습니다.
- 로컬 입력은 6개 활동의 자료 쌍이 있었고, 해수욕(`sp`) 자료 쌍은 없었습니다. 활동별 행 수는 위 표와 같습니다.
- 존재하는 자료 쌍은 행 수와 일부 날짜·지역 또는 항로·선박 식별자의 순서가 일치했습니다. 예측일자·시간·어종 등 전체 식별자까지 확인한 결과는 아니므로, 고유키 검증으로 해석하지 않습니다.
- Python 3.12.14 / pandas 3.0.1 / NumPy 2.3.5 / openpyxl 3.1.5 환경에서 복사한 입력으로 주 실행 코드 4개를 각각 실행했습니다. 원래 결과물은 덮어쓰지 않았습니다.
- 특이사항 코드는 반복 병합에 따른 중복 열 오류로, 나머지 3개는 Jinja2 누락으로 종료했습니다. 오류 발생 전 새로운 CSV·HTML·보고용 XLSX는 생성되지 않았습니다.
- 기록한 오류는 각 실행에서 처음 확인한 중단 원인입니다. Jinja2 설치만으로 나머지 코드까지 정상 동작한다고 판단할 수 없습니다.
- `requirements.txt`의 Python 3.10–3.11 / pandas 1.5.3 조합은 재현을 위한 후보이며 이번에 설치·실행 검증하지 않았습니다.

**추가 확인:** 정상 실행 환경 확정, 전체 스키마·결측값·레코드 식별자 점검, 병합 전후 행 수와 집계 단위 확인, 분모 정의 및 독립 계산값 대사, 변경 없음·자료 누락·중복 특보 사례 검증, 승인된 기존 보고서와의 결과 대사가 필요합니다.

이번 기록은 문법 및 일부 입력 구조 확인과 실행 시도의 증거입니다. 통계 정확성, 보고서 전체 재현, 관측 대비 예보 성능 또는 운영 준비 완료를 보증하지 않습니다.
