# Historical variants / 이전 코드

Eleven Python scripts from the working folder are preserved here without changing their contents. These files document earlier activity-selection and reporting implementations; use the four numbered root scripts as the current snapshot.

- `SP제외`: swimming excluded.
- `SP,SS제외`: swimming and scuba diving excluded.
- `SP,SS,TL제외`: swimming, scuba diving, and tidal-flat activities excluded.
- Variants may contain hardcoded Windows paths and older pandas calls. Review the actual code before running; a filename describes the intended scope, not a verified execution guarantee.
- All eleven files passed syntax parsing during publication, with invalid-escape warnings in two files. They were not execution-tested. See [the validation record](../VALIDATION.md).
- Run historical scripts in a separate working copy because they can use the same output filenames as current scripts.

---

작업 폴더에 있던 이전 Python 코드 11개를 내용 변경 없이 보존합니다. 주 실행 기준은 루트의 번호 있는 코드 4개입니다.

- `SP제외`: 해수욕 제외 변형입니다.
- `SP,SS제외`: 해수욕·스킨스쿠버 제외 변형입니다.
- `SP,SS,TL제외`: 해수욕·스킨스쿠버·갯벌 제외 변형입니다.
- 일부 코드는 이전 Windows 절대경로와 pandas API를 사용합니다. 파일명은 의도된 범위를 나타내며, 실제 적용 범위와 경로는 소스에서 확인해야 합니다.
- 11개 모두 문법 파싱은 성공했으나 2개에서 이스케이프 경고가 발생했습니다. 실행 검증은 하지 않았습니다. 자세한 범위는 [검증 기록](../VALIDATION.md)을 참고하세요.
- 현재 코드와 결과 파일명이 겹칠 수 있으므로 별도 작업 복사본에서 사용합니다.
