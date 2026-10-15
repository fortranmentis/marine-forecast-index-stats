<div align="center">

# Marine Forecast Index Stats

**From paired forecast spreadsheets to interpretable change statistics.**

생활해양예보지수 · 예보 변경 분석 · 통계 요약

![Python](https://img.shields.io/badge/Python-analysis%20scripts-3776AB?logo=python&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-tabular%20analysis-150458?logo=pandas&logoColor=white)
![Reports](https://img.shields.io/badge/Reports-XLSX%20%7C%20CSV%20%7C%20HTML-217346)
![Validation](https://img.shields.io/badge/Validation-partial%20%7C%20see%20notes-DAA520)

[English](#english) · [한국어](#한국어) · [Validation record](VALIDATION.md)

</div>

---

## English

[About](#about) · [Highlights](#highlights) · [Data contract](#data-contract) · [Usage](#usage) · [Validation](#validation) · [Notes](#notes)

### About

Python scripts for compiling statistics on Korean marine activity forecast indices. The workflow compares **service data (`mod`)** with **prediction data (`org`)**, summarizes index changes, examines differences in model variables and weather warnings, and produces tables for operational reporting.

The collection covers sea parting, tidal-flat activities, sea fishing, seasickness, surfing, swimming, and scuba diving. It supports review of how forecast products change between two datasets; it does not calculate forecast accuracy against observations.

### Highlights

| Capability | Analytical purpose |
| :--- | :--- |
| Forecast volume and index comparisons | Count input records and identify changed forecast indices by activity. |
| Model-variable diagnostics | Examine changes in wave height, water temperature, and activity-specific scores among changed-index records. |
| Warning diagnostics | Summarize warning codes and precipitation-related conditions using activity-specific filters. |
| Event-day summaries | Count days with typhoon, wind-wave, storm-surge, heavy-rain, and precipitation conditions, including overlaps. |
| Regional and vessel reporting | Produce regional, location, route, and vessel summaries where implemented. |
| Reporting exports | Write styled Excel/HTML detail tables and EUC-KR CSV summaries; some results are console-only. |

### Repository guide

| File or directory | Role |
| :--- | :--- |
| `0.특이사항_발생일및비중(수정).py` | Event-day counts, percentages, and overlapping conditions; console output. |
| `1.건수통계(수정).py` | Overall forecast/index-change counts; detailed sea-parting and tidal-flat exports. |
| `2.건수통계_모델(수정).py` | Model-variable comparisons for fishing, seasickness, surfing, swimming, and scuba diving. |
| `3.건수통계_특보(수정).py` | Warning-related comparisons and summaries for those five activities. |
| `bck/` | Eleven historical variants, including activity exclusions and older paths. |
| `VALIDATION.md` | Dated evidence, runtime failures, and validation boundaries. |
| `requirements.txt` | Candidate legacy dependency constraints; see compatibility notes. |
| Existing unnumbered scripts | Earlier repository material retained for provenance; outside the validation scope below. |

The four numbered root scripts are the current working-folder snapshot. The filenames and calculation logic are preserved. They remain standalone scripts rather than an installable package or a single command-line application.

### Data contract

Place input workbooks in the **working directory from which Python is launched**. The scripts read relative filenames and use the first worksheet through `pandas.read_excel`.

| Prefix | Activity | Expected pair |
| :---: | :--- | :--- |
| `sd` | Sea parting / 바다갈라짐 | `sdmod.xlsx`, `sdorg.xlsx` |
| `sf` | Sea fishing / 바다낚시 | `sfmod.xlsx`, `sforg.xlsx` |
| `sk` | Seasickness / 뱃멀미 | `skmod.xlsx`, `skorg.xlsx` |
| `sr` | Surfing / 서핑 | `srmod.xlsx`, `srorg.xlsx` |
| `tl` | Tidal-flat activities / 갯벌체험 | `tlmod.xlsx`, `tlorg.xlsx` |
| `sp` | Swimming / 해수욕 | `spmod.xlsx`, `sporg.xlsx` |
| `ss` | Scuba diving / 스킨스쿠버 | `ssmod.xlsx`, `ssorg.xlsx` |

**Schema expectations**

- Preserve Korean column names, including `생산일` and `예보지수`. Location identifiers differ by activity: `권역`/`지역`, `항로명`/`선박명`, `구분`/`지역`, or `권역`/`해수욕장`.
- Supply the activity-specific measures referenced by each script, such as `최대파고`, `평균수온`, `유의파고`, score fields, `해상특보`, `육상특보`, `특보`, and `강수량`. The columns above are examples, not a complete interchangeable schema.
- Pair matching is largely based on **DataFrame index and existing row order**. Equal row counts alone do not establish record identity. Align full record identifiers before running, including forecast time, species, or other dimensions where applicable.
- A date/location combination can describe several forecast records. Do not deduplicate records using only the reporting dimensions.
- `'-'` is a source placeholder handled differently across code branches; it is not a universal missing-value convention.

### Workflow and outputs

```text
Paired Excel inputs (mod / org)
              |
              +-- 0: event-day counts and overlaps --> console
              +-- 1: overall index-change counts --> console / selected reports
              +-- 2: model-variable diagnostics --> XLSX / CSV / HTML
              +-- 3: warning diagnostics --------> XLSX / CSV / HTML
```

Examples include `갈라짐_요약.csv`, `갯벌_지역_사유.xlsx`, `바다낚시2_요약_모델.csv`, and `뱃멀미3_선박_특보.xlsx`. Output availability depends on the input activity, selected records, and whether execution reaches the export step. Existing local reports are not evidence that this snapshot reproduces them successfully.

### Usage

> [!IMPORTANT]
> This publication preserves the existing analytical scripts. Syntax checks passed, but the four current scripts did **not** complete in the inspected Python 3.12 / pandas 3 environment. Review [VALIDATION.md](VALIDATION.md) before operational use.

The code uses legacy pandas interfaces, including `to_excel(..., encoding=...)`. A **candidate** environment is Python 3.10–3.11 with pandas 1.5.x and NumPy 1.x. The constraints supplied here have not been installed or validated as a working environment, and older pandas versions may retain the merge behavior seen in the source. They are a starting point for reproduction, not a compatibility guarantee.

```powershell
# In an environment already using Python 3.10 or 3.11:
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

# Put matching workbooks alongside the scripts, then run independently:
.\.venv\Scripts\python.exe "0.특이사항_발생일및비중(수정).py"
.\.venv\Scripts\python.exe "1.건수통계(수정).py"
.\.venv\Scripts\python.exe "2.건수통계_모델(수정).py"
.\.venv\Scripts\python.exe "3.건수통계_특보(수정).py"
```

Run in a separate working copy: exports use fixed filenames and may overwrite earlier outputs. Each script reads its own inputs; the numbering is a reading guide, not an implemented dependency chain. Historical variants in `bck/` require separate path and activity-scope review.

### Validation

Publication checks on **2026-10-15** distinguished source checks, input checks, and execution results:

| Check | Observed result | Boundary |
| :--- | :--- | :--- |
| Python syntax | All 15 local source files parsed successfully. | Two archive files emitted invalid-escape warnings; parsing does not establish runtime correctness. |
| Input inventory | Six workbook pairs were present; the swimming (`sp`) pair was absent. | Input workbooks are local and are not published with the code. |
| Pair structure | Each available pair had equal row counts and matching ordered values for selected date/location or route/vessel fields. | Full record identity, null handling, and business rules were not certified. |
| Isolated execution | All four current scripts were attempted on copied inputs; all exited with errors. | Duplicate-column merge behavior and a missing Jinja2 dependency prevented complete execution. |
| Output reconciliation | Not completed. | No claim of numerical accuracy, successful regeneration, or observational forecast skill. |

See [the detailed validation record](VALIDATION.md) for counts and exact failure summaries.

### Notes

- **Interpretation:** A changed index is a difference between two products. Model and warning categories follow code filters and may overlap; they do not establish independent causal attribution.
- **Denominators:** Event-day percentages use the script's merged-day population. Change reports use different denominators across summary levels, including selected changed records and total forecast records. Verify the relevant formula before combining percentages.
- **Join grain:** Some summaries join on a location name alone. Repeated names across regions can multiply rows; reconcile totals at the full grouping grain.
- **Missing activities:** Several scripts skip absent workbook pairs, while event-day processing follows a different path. Partial inputs must not be treated as complete seven-activity coverage.
- **Compatibility and encoding:** Scripts suppress warnings. CSV exports generally use EUC-KR, while HTML writes rely on the system's default text encoding. Modern pandas support requires further work.
- **Publication scope:** Python sources and documentation are included. Local input data, generated reports, and the HWPX summary document are excluded via `.gitignore`; the uploaded working-folder code is unchanged.
- **Reuse:** No license is introduced by this documentation update. Confirm applicable data and code permissions before redistribution.

---

## 한국어

### 소개 · About

생활해양예보지수의 **서비스 자료(`mod`)와 예측 자료(`org`)를 비교**하고, 예보 건수·지수 변경·모델 요소·기상특보·특이사항 발생일을 집계하는 Python 스크립트 모음입니다. 통계 요약집과 업무 검토용 표를 만드는 과정을 지원합니다.

대상은 바다갈라짐, 갯벌체험, 바다낚시, 뱃멀미, 서핑, 해수욕, 스킨스쿠버입니다. 두 자료 사이의 변경을 분석하는 코드이며, 관측값과 비교한 예보 정확도 검증 기능은 포함하지 않습니다.

### 주요 기능 · Highlights

| 기능 | 활용 목적 |
| :--- | :--- |
| 총 예보 건수와 지수 변경 집계 | 활동별 자료 규모와 서비스·예측 자료의 차이 파악 |
| 모델 요소 차이 분석 | 지수가 달라진 자료에서 파고·수온·활동별 점수의 차이 확인 |
| 특보 관련 분석 | 활동별 조건에 따라 특보 코드와 강수 관련 변경 내역 요약 |
| 특이사항 발생일 집계 | 태풍·풍랑·폭풍해일·호우·강수의 발생일 및 중복 발생 비중 산출 |
| 권역·지역·항로·선박별 요약 | 세부 단위의 통계 검토 지원 |
| 보고용 결과물 | Excel·HTML 상세표, EUC-KR CSV 요약표 및 콘솔 통계 출력 |

### 코드 구성

| 파일 | 역할 |
| :--- | :--- |
| `0.특이사항_발생일및비중(수정).py` | 특이사항 발생일·비중·중복 조건을 콘솔에 출력 |
| `1.건수통계(수정).py` | 전체 예보·지수 변경 건수와 바다갈라짐·갯벌 상세 결과 생성 |
| `2.건수통계_모델(수정).py` | 바다낚시·뱃멀미·서핑·해수욕·스킨스쿠버의 모델 요소 비교 |
| `3.건수통계_특보(수정).py` | 위 5개 활동의 특보 관련 비교·통계 생성 |
| `bck/` | 활동 제외 조건과 과거 경로가 포함된 이전 코드 11개 |
| `VALIDATION.md` | 이번 게시 시 확인한 검증 결과와 실행 제약 |
| `requirements.txt` | 재현을 시작하기 위한 기존 pandas 계열 의존성 후보 |

기존 레포의 번호 없는 Python 파일 5개는 이력을 위해 유지합니다. 이번 실행 검증 대상은 작업 폴더에서 추가한 번호 있는 주 실행 코드 4개이며, 기존 레포 파일의 동작까지 검증한 것은 아닙니다.

### 입력 자료와 실행 방법

영문 [Data contract](#data-contract)의 파일명 표에 따라 `sd`, `sf`, `sk`, `sr`, `tl`, `sp`, `ss`별 `mod.xlsx`·`org.xlsx` 쌍을 준비합니다. 입력 파일은 **Python을 실행하는 작업 디렉터리**에 두어야 합니다. 각 코드가 `pandas.read_excel`로 첫 번째 시트를 읽습니다.

- `생산일`, `예보지수` 및 활동별 식별자·모델 요소·점수·특보 열의 한글 이름을 유지합니다.
- 자료 비교는 주로 DataFrame 인덱스와 기존 행 순서에 의존합니다. 행 수만 맞추지 말고 예측일자·시간·어종 등 실제 레코드 구분 요소까지 확인합니다.
- 생산일과 지역이 같아도 시간·어종 등이 다른 별도 예보일 수 있습니다. 보고서의 집계 차원을 곧바로 중복 제거 키로 사용하지 않습니다.
- `'-'`의 처리 방식은 코드별로 다르므로 입력 전체의 결측값 규칙을 별도로 점검합니다.

> [!IMPORTANT]
> 이번 게시에서는 원래 계산 로직을 보존했습니다. 문법 검사는 통과했지만, 확인한 Python 3.12 / pandas 3 환경에서 주 실행 코드 4개는 모두 오류로 종료했습니다. 업무 적용 전 [검증 기록](VALIDATION.md)을 확인해야 합니다.

Python 3.10–3.11, pandas 1.5.x, NumPy 1.x 조합을 재현 환경 **후보**로 제시합니다. `requirements.txt`의 조합은 이번에 설치·실행 검증하지 않았으므로 정상 동작을 보장하지 않습니다. 영문 [Usage](#usage)의 PowerShell 명령으로 환경을 준비한 뒤 각 코드를 독립적으로 실행합니다.

코드가 고정된 파일명으로 결과를 저장하므로 별도 작업 복사본을 사용합니다. 번호 순서는 코드 이해를 위한 안내이며, 앞선 코드의 결과물을 다음 코드가 반드시 읽는 파이프라인 구조는 아닙니다. `bck/`는 경로와 활동 제외 조건을 확인한 후 사용합니다.

### 검증 · Validation

**2026-10-15 확인 결과**이며, 소스 검사와 자료 구조 확인, 실제 실행 결과를 구분했습니다.

| 검증 항목 | 확인 결과 | 해석 범위 |
| :--- | :--- | :--- |
| 문법 검사 | 추가 대상 Python 코드 15개 모두 파싱 성공 | 과거 코드 2개에서 이스케이프 경고 발생; 실행 성공을 의미하지 않음 |
| 입력 파일 | 6개 활동의 자료 쌍 존재, 해수욕(`sp`) 쌍 부재 | 입력 데이터는 레포에 게시하지 않음 |
| 자료 쌍 구조 | 존재하는 쌍의 행 수와 일부 날짜·공간 식별자 순서 일치 | 전체 식별자·결측 처리·업무 규칙의 검증은 아님 |
| 분리 환경 실행 | 복사한 입력으로 코드 4개 실행 시도, 모두 오류 종료 | 병합 시 중복 열 오류와 Jinja2 누락 확인 |
| 산출값 대사 | 미완료 | 통계 정확성·기존 산출물 재현·관측 대비 성능을 보증하지 않음 |

자료별 건수와 오류 내용은 [VALIDATION.md](VALIDATION.md)에 기록했습니다.

### 참고사항 · Notes

- **변경의 의미:** 지수 변경은 두 자료 간 차이입니다. 모델·특보 분류는 코드의 조건을 따른 결과이며, 서로 배타적이거나 독립된 인과관계라고 해석하지 않습니다.
- **비율의 분모:** 발생일 비율은 병합된 날짜 모집단을 사용합니다. 변경 통계는 선택된 변경 건수 또는 전체 예보 건수 등 집계 단계별 분모가 다르므로, 지표를 합치기 전에 계산식을 확인합니다.
- **병합 단위:** 일부 통계는 지역명만으로 병합합니다. 다른 권역에 같은 지역명이 있으면 행 수가 늘어날 수 있으므로 전체 식별자 수준에서 합계를 대사합니다.
- **활동 누락:** 입력이 없는 활동을 건너뛰는 코드와 특이사항 처리 경로는 다릅니다. 일부 자료만으로 7개 활동 전체를 분석했다고 해석하지 않습니다.
- **호환성과 인코딩:** 코드가 경고를 숨기며, 이전 pandas API를 사용합니다. CSV는 주로 EUC-KR, HTML은 시스템 기본 인코딩에 의존합니다.
- **게시 범위:** 코드와 문서를 게시하고, 입력 Excel·생성 결과·HWPX 요약집은 `.gitignore`로 제외합니다. 이번에 올린 기존 Python 코드의 계산 로직은 수정하지 않았습니다.
- **재사용:** 이번 문서화 작업에서 라이선스를 새로 지정하지 않았습니다. 자료와 코드의 재배포 권한을 확인한 뒤 사용합니다.

<div align="center">

[Back to English](#english) · [검증 기록](VALIDATION.md) · [맨 위로](#marine-forecast-index-stats)

</div>
