# Alloy & Interface Database

머신러닝 원자간 포텐셜(MLIP)로 계산한 금속 표면·계면·합금 첨가 원소 물성을 모아 검색·비교·시각화하는 공개 조회용 데이터베이스입니다. 구조 생성 → MLIP 계산 → 원본 검증 → DB 수록은 내부 자동화 도구로 수행하고, 이 저장소에는 검증된 결과만 공개합니다.

MLIP-based database of metal surfaces, interfaces and alloying-element energetics. Read-only public view; structure generation, calculation and validation run in an internal pipeline.

- 사이트: https://hexagonrose.github.io/interface-platform-db/
- 2026-11-18 기준 고정본: [`v2026.11.18`](https://github.com/hexagonrose/interface-platform-db/tree/v2026.11.18) (`catalog.json` SHA-256 `d8603adfc76383a25a35084e733451b60c2b73f7cad4327840cc68f273e836a5`)
- 계산 모델: SevenNet-Omni, MPA modal

## Interface PES 업로드

기존 Builder 계면의 동일 정합 셀에서 계산한 **고정 간격 a/b 지도 한 장**을 [02_interface_pes](02_interface_pes)에 JSON 하나로 추가합니다. `53_interface_gap_grid/00_scan.py`의 검증된 출력을 그대로 올릴 수 있습니다. 기준 지도 예시는 [Cu(110)/Ni(110)](02_interface_pes/builder-cu110-ni110-c1_dz+0.00.json)입니다.

- `id`는 기존 계면 구조 ID, `source_sha256`과 `checkpoint_sha256`은 계산 원구조와 모델의 해시입니다. 첫 형식은 SevenNet-Omni(MPA), 강체 이동, 정합된 원구조에 대한 추가 twist·tilt 0°입니다.
- `gap_A`와 `dz_A`는 최외곽 층 사이의 절대 간격과 기준 구조 대비 변화량(Å)입니다. `axes`는 0과 1을 포함한 균일 분율 격자이며 두 배열 `energies_eV`, `gamma_J_m2`의 인덱스 순서는 [b][a]입니다. `area_A2`와 `origin_control_eV`도 함께 기록합니다.
- Pages 빌드는 구조·모델·간격·원점·양축 주기 경계 및 총에너지에서 재산출한 절대 γ를 검사합니다. 통과한 간격은 홈페이지 슬라이더에 자동 등록됩니다. 원래 격자 크기를 유지하고 서로 다른 간격 사이 에너지는 보간하지 않습니다.
- 전체 공개 catalog.json의 `interface_pes`에서 구조별 파일과 수록 간격을 조회할 수 있습니다. 새 방위나 모델을 추가하려면 그 계산에 해당하는 셀과 에너지 참조가 필요합니다.

## Surface 계산 결과 업로드

검증을 마친 홑원소 결정상마다 [01_surface](01_surface)에 `원소_mp-ID.json` 파일 하나를 올립니다. 예를 들어 Mg 갱신은 [Mg_mp-153.json](01_surface/Mg_mp-153.json)을 교체합니다. 새 결정상에는 고유한 `record.id`를 사용하고 `record.material_id`를 바깥의 `material_id`와 맞춥니다. 같은 원소의 다른 상은 별도 파일로 올립니다.

파일의 `record`에는 면별 에너지(J/m²), 슬랩 원자구조, 계산 출처와 Wulff 형상을 담습니다. `nano`에는 검증을 통과한 면별 비교값, `failures`에는 보류 모델과 실패한 면의 사유를 담습니다. 계산 수렴과 모델 기준상 검토는 업로드 전에 수행합니다.

`main`에 반영하면 GitHub Actions가 식별자·필수 값·슬랩 구조를 검사하고 모바일·데스크톱에서 각 결정상의 화면을 엽니다. 검사를 통과하면 Pages에 배포합니다. 실패 사유는 저장소의 Actions에서 확인할 수 있으며 직전 성공 배포가 계속 제공됩니다.

최신 전체 데이터는 [공개 catalog.json](https://hexagonrose.github.io/interface-platform-db/catalog.json)에서 받습니다. 저장소 루트의 `catalog.json`은 기존 자료를 합치는 기준 스냅숏입니다. 홑원소 Surface는 `01_surface`의 결과가 우선합니다.

## 연구 계획 대응

2025년(2단계 1차년도) 보고서의 차년도 계획 "합금 원소 및 이질상 구성 원소 분석용 자동화 플랫폼 구축"에 대응하는 결과물입니다.

| 계획 내용 | 현재 구현 |
|---|---|
| 원소 제약 없이 MLIP로 물성 데이터베이스 구축 | Omni-MPA 기준 표면·계면·벌크 용질 DB 106건(2026-11-18 고정본 68건) |
| Cu-Ni-Si 합금의 이질상/기지 계면 | Cu/Ni, Cu/Ni₂Si, Cu/G-phase, Al/Zn 계면 42건, 초기 이동별 계면 지도, Cu/Ni 강체 미끄럼 경로, Cu×Ni 면 조합 격자 매칭 후보 |
| Al-Zn 등 첨가 원소 선정 | Cu·Al·Zn 모재의 용질 형성에너지 57건(Cu·Al 모재 12원소 자동 계산 포함), Cu/G-phase 계면 Al 편석 시범 |
| 물질 선정·구조 생성 등 데이터 생산 자동화 | 치환 구조 생성 → MLIP 완화 → 원본 검증 → DB 수록 자동화(벌크 신규 3건), 계면 만들기 후보 → MLIP 완화 → DB 등록(12건) |
| 후보군의 양자계산 검증 | 후속 계획(현재 DFT 검증 미수행) |

## 데이터 생산 흐름

```mermaid
flowchart LR
  A[물질·첨가 원소 선택] --> B[구조 생성<br/>치환·슬랩·계면]
  B --> C[SevenNet-Omni MPA<br/>구조 완화·에너지]
  C --> D[원본 검증<br/>에너지·힘·조성·셀·해시]
  D -->|통과| E[DB 수록<br/>catalog.json]
  D -->|불일치·미수렴| X[제외]
  E --> F[공개 조회<br/>검색·비교·시각화·다운로드]
```

공개 사이트에는 계산 제출 기능이 없습니다. 내부 경로, HPC 접속 정보, 실행 로그는 공개하지 않습니다.

## 수록 현황

DB 등록 106건 (보고서 기준 고정본 `v2026.11.18`은 68건: 계면 30건, 벌크 33건):

| 분야 | 건수 | 내용 |
|---|---:|---|
| 표면·Wulff | 7 | Cu 6, Ni 3, Ni₂Si 8, Al 6, Zn 6, Si 3, α-Mn 2 방향 (총 34개 결정면 표면에너지와 Wulff 형상) |
| G-phase surface | 1 | Mn₆Ni₁₆Si₇ (100)/(110)/(111) 화학양론 슬랩의 양면 평균 γ̄와 3면족 근사 Wulff. 두 두께에서 26개 슬랩을 완화했습니다. |
| 계면 | 42 | Cu/Ni 24, Cu/Ni₂Si 13, Cu/G-phase 1, Al/Zn 4 (접합일 또는 계면에너지). 이 중 12건은 계면 만들기 후보 표본 |
| 벌크 첨가 원소 | 57 | Cu·Al·Zn 모재 각 10종(기존 계산) + 자동 계산: Cu 모재 Al·Zn·Mg 3건(11/13), Cu·Al 모재 각 12원소 24건(11/20) |

68건과 별도로 제공하는 자료:

- Interface 요약의 2차원 강체 미끄럼 지도 13개. Cu/G-phase 1개, Cu/Ni·Cu/Ni₂Si·Al/Zn 결정면 조합 각 4개. 지도마다 두 면내 방향으로 21 × 21개 위치에서 SevenNet-Omni(MPA) 단일점 에너지를 계산했습니다.
- Cu/G-phase는 주기 셀의 두 계면에 대한 평균 계면에너지 γ를 표시합니다. 나머지 12개는 슬랩 간 수직 거리를 고정하고, 격자 최저점과의 에너지 차이를 접합 면적으로 나눈 Δγ(J/m²)를 표시합니다. 오른쪽 카드의 γ는 같은 면내 격자 조건에서 계산한 두 표면에너지의 합에서 선택 위치의 접합일을 뺀 값입니다. 결정면별 그래프는 각 21 × 21 PES의 최저 계면에너지 γ를 오름차순으로 표시합니다. 기준 구조의 접합일은 상세 데이터에서 확인할 수 있습니다.
- Cu 6방향 × Ni 3방향 격자 매칭 후보 18개(미완화, 에너지 미계산)
- Cu/G-phase Al 편석 시범: Cu 6층·12층 × 6자리, 치환 12구조와 무첨가 2구조

## 사이트 기능

- 표면: 물질별 결정면 표면에너지 순위, Wulff 형상, 완화된 슬랩 구조
- 계면: 물질쌍·계산 세트별 구조와 에너지, 초기 이동 위치별 지도, 2차원 미끄럼 지도와 원자 구조, 기존 1차원 경로 재생, 면 조합 후보, Al 편석 자리 비교
- 벌크 첨가 원소: 모재와 계산 세트를 선택하면 용질별 형성에너지가 낮은 순으로 표시됩니다. 원소 카드를 선택해 해당 구조를 확인할 수 있습니다.
- Segregation(Interface → Cu/G-phase, Cu/Ni₂Si): Al·Si·Sc·Zn·Mg·Ni·Ti의 interface 자리별 segregation energy(Cu 내부 자리 기준)와 Cu host bulk formation energy를 한 표에서 비교, 칸을 누르면 완화 구조. 대표 6자리·한 두께 탐색 계산
- Omni·Nano 비교: surface energy 막대·표, interface 비교 막대, initial shift 지도, Al segregation 표에 같은 구조의 SevenNet-Nano(pretrained 5.5) single-point 값을 Omni 값과 함께 표시. 기준은 Omni이며 DFT 정확도가 아님
- 계면 만들기(`builder.html`): 표면 DB의 완화 슬랩 두 개를 골라 격자 매칭한 계면 초기 구조를 브라우저에서 생성. Cu/Ni·Cu/Ni₂Si·Al/Zn 102개 면 조합, 후보 321개. 층간 간격·면내 이동 조절과 EXTXYZ 다운로드. 에너지는 계산하지 않으며, 같은 면 조합의 DB 계산이 있으면 함께 표시
- 모든 결과의 구조(EXTXYZ)·값(JSON/CSV) 다운로드, 직접 링크, 라이트/다크 모드

## 해석 범위

- 형성에너지, 접합일, 계면에너지, 자유표면에너지, 편석에너지는 서로 다른 물리량입니다. 같은 계산 세트 안에서만 비교합니다.
- 값은 SevenNet-Omni(MPA) 계산값이며 DFT 정확도 검증은 후속 과제입니다. 계산 세트 안의 순위는 실험적 합금 추천이 아닙니다.
- 자유표면 Wulff 형상은 기지 내 석출물 형상과 다릅니다.
- 초기 이동별 계면 지도는 고정 셀에서 원자를 자유 완화한 결과로, 구속된 미끄럼 장벽 지도가 아닙니다. 강체 미끄럼 경로는 원자 완화 없는 단일점 계산입니다.
- 격자 매칭 후보는 지정한 탐색 한도 안의 대표 후보이며 계면에너지는 계산하지 않았습니다.
- 계면 만들기의 구조는 자유표면으로 완화된 DB 슬랩을 붙인 미완화 초기 구조입니다. 후보 순서는 에너지 순위가 아닙니다.
- 편석 시범은 대표 자리·두 두께의 결과입니다. 전체 자리, 두께·희석 한계 수렴, DFT 정확도는 검증하지 않았습니다.

## 파일

- `index.html`: 사이트(데이터 포함 단일 파일)
- `builder.html`: 계면 만들기(표면 슬랩·격자 매칭 후보 포함 단일 파일)
- `catalog.json`: 전체 DB. `records`(에너지 자료 106건과 구조 전용 1건), `sliding`, `matching`, `segregation`, `model_policy`, `scope`

## 갱신 이력

- 2026-11-20: Cu/G-phase·Cu/Ni₂Si solute segregation screening 84계산 추가
- 2026-11-20: 헤더 Solute 탭, solute 자동 계산 한 표, 구조 보기 원자 영역 맞춤, surface supercell 표시, G-phase surface 구조(구조만) 추가
- 2026-11-20: 결과 그래프에 Omni·Nano 값을 함께 표시(별도 모델 비교 페이지는 삭제). 전문 용어 영어 표기. 태그 `v2026.11.20.3`
- 2026-11-23: α-Mn의 {100}·{110} 두 면족으로 제한 Wulff 형상을 생성했다. (111) 슬랩의 비등가 양면 평균은 상세 데이터와 Slab에서 별도로 제공한다.
- 2026-11-23: 다이아몬드 Si의 (100), (110), (111) 대칭 절단 표면을 완화해 수록. Wulff 형상은 이 세 면족으로 구성하며 면내 초격자 재구성은 탐색 범위 밖이다. Si·Ni·Cu·Al·Zn의 상세 데이터에서 문헌 DFT-PBE와 출처를 제공한다.
- 2026-11-20: 자동 계산으로 Cu·Al 모재에 Al·Zn·Mg·Ni·Si·Mn·Co·Cr·Fe·Ti·Zr·Sc(모재 원소 제외) 용질 형성에너지 24건 추가(DB 104건). 11/13 Cu 모재 Al·Zn·Mg 값 재현(차 <0.0001 eV). 태그 `v2026.11.20`
- 2026-11-18: 계면 만들기 후보 12개(Cu/Ni·Cu/Ni₂Si·Al/Zn 각 4)를 MLIP로 완화해 접합일 등록(DB 80건)
- 2026-11-18: 계면 만들기 페이지 추가
- 2026-11-18: 구조 표시 개선(셀 경계에서 원자 열이 갈라져 보이던 문제 해소, 편석 화면 표·구조 2단 배치)
- 2026-11-18: Cu/G-phase Al 편석 시범 공개, 보고서 기준 고정본 `v2026.11.18` 태그
- 2026-11-13: 사이트 공개. Omni-MPA 기준으로 DB 정리, Al·Zn 표면 확장, 계면 지도·강체 미끄럼·격자 매칭 후보, 벌크 첨가 원소 히트맵 추가

DB는 검증된 계산을 추가하며 계속 갱신합니다. 보고서 인용 시에는 고정본 태그를 사용하십시오.
