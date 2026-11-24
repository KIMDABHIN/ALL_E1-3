
import json
import time
import math

EPSILON = 1e-9
REPEAT_COUNT = 10


# 라벨을 표준 이름으로 변경
def normalize_label(label):
    if not isinstance(label, str):
        return "UNKNOWN"

    label = label.strip().lower()

    if label in ["+", "cross"]:
        return "Cross"
    elif label == "x":
        return "X"

    return "UNKNOWN"


# 행렬 크기와 숫자 확인
def validate_matrix(matrix, size, name):
    if not isinstance(matrix, list) or len(matrix) != size:
        raise ValueError(f"{name}: 행 개수가 맞지 않습니다.")

    for row in matrix:
        if not isinstance(row, list) or len(row) != size:
            raise ValueError(f"{name}: 열 개수가 맞지 않습니다.")

        for value in row:
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(value)
            ):
                raise ValueError(f"{name}: 올바른 숫자가 아닙니다.")


# MAC 연산
def mac_operation(pattern, filter_data):
    score = 0

    for i in range(len(pattern)):
        for j in range(len(pattern[i])):
            score += pattern[i][j] * filter_data[i][j]

    return score


# 점수 비교
def classify_pattern(score_a, score_b):
    if abs(score_a - score_b) < EPSILON:
        return "UNDECIDED"
    elif score_a > score_b:
        return "A"
    else:
        return "B"


# 두 점수를 Cross/X로 판정
def classify_labels(cross_score, x_score):
    result = classify_pattern(cross_score, x_score)

    if result == "A":
        return "Cross"
    elif result == "B":
        return "X"

    return "UNDECIDED"


# 사용자 입력
def input_matrix(name):
    matrix = []

    print(f"\n[{name} 입력]")

    for i in range(3):
        while True:
            try:
                row = input(
                    f"{i + 1}번째 행 (숫자 3개 입력): "
                ).split()

                if len(row) != 3:
                    print(
                        "입력 형식 오류: "
                        "각 줄에 3개의 숫자를 입력하세요."
                    )
                    continue

                values = [float(value) for value in row]

                if not all(math.isfinite(value) for value in values):
                    print("유한한 숫자만 입력할 수 있습니다.")
                    continue

                matrix.append(values)
                break

            except ValueError:
                print("숫자만 입력하세요.")

    return matrix


# 행렬 출력
def print_matrix(name, matrix):
    print(f"\n{name}")

    for row in matrix:
        print(" ".join(f"{value:g}" for value in row))


# 평균 연산 시간 측정
def measure_mac_time(pattern, filter_data):
    total_time = 0

    for _ in range(REPEAT_COUNT):
        start = time.perf_counter()
        mac_operation(pattern, filter_data)
        end = time.perf_counter()

        total_time += end - start

    return total_time / REPEAT_COUNT * 1000


# 사용자 입력 모드
def user_input_mode():
    print("\n========== 사용자 입력 모드 ==========")

    filter_a = input_matrix("필터 A")
    filter_b = input_matrix("필터 B")
    pattern = input_matrix("판별할 패턴")

    print_matrix("필터 A 확인", filter_a)
    print_matrix("필터 B 확인", filter_b)
    print_matrix("입력 패턴 확인", pattern)

    score_a = mac_operation(pattern, filter_a)
    score_b = mac_operation(pattern, filter_b)

    result = classify_pattern(score_a, score_b)

    time_a = measure_mac_time(pattern, filter_a)
    time_b = measure_mac_time(pattern, filter_b)

    print("\n========== 판정 결과 ==========")
    print(f"필터 A 점수: {score_a}")
    print(f"필터 B 점수: {score_b}")
    print(f"최종 판정: {result}")

    print("\n========== 3×3 성능 분석 ==========")
    print(f"반복 횟수: {REPEAT_COUNT}회")
    print(f"연산 횟수: 9회")
    print(f"필터 A 평균 시간: {time_a:.6f} ms")
    print(f"필터 B 평균 시간: {time_b:.6f} ms")


# JSON 데이터 불러오기
def load_json_data():
    try:
        with open("data.json", "r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, dict):
            raise ValueError("JSON 최상위 구조가 올바르지 않습니다.")

        if not isinstance(data.get("filters"), dict):
            raise ValueError("filters 데이터가 없거나 잘못되었습니다.")

        if not isinstance(data.get("patterns"), dict):
            raise ValueError("patterns 데이터가 없거나 잘못되었습니다.")

        print("\nJSON 데이터 로드 성공!")
        return data

    except FileNotFoundError:
        print("오류: data.json 파일을 찾을 수 없습니다.")
    except json.JSONDecodeError:
        print("오류: JSON 파일의 형식이 올바르지 않습니다.")
    except ValueError as error:
        print(f"오류: {error}")

    return None


# 필터 키 정규화
def get_standard_filters(filters):
    standard_filters = {}

    for key, matrix in filters.items():
        label = normalize_label(key)

        if label == "UNKNOWN":
            continue

        if label in standard_filters:
            raise ValueError(f"중복된 필터 라벨: {label}")

        standard_filters[label] = matrix

    return standard_filters


# JSON 패턴 분석
def analyze_json_data(data):
    total = 0
    passed = 0
    failed = 0
    failed_cases = []

    print("\n========== JSON 패턴 분석 ==========")

    for key, info in data["patterns"].items():
        total += 1

        print(f"\n[{key}]")

        try:
            parts = key.split("_")

            if len(parts) != 3 or parts[0] != "size":
                raise ValueError("패턴 이름 형식이 올바르지 않습니다.")

            size = int(parts[1])

            if size <= 0:
                raise ValueError("패턴 크기가 올바르지 않습니다.")

            if not isinstance(info, dict):
                raise ValueError("패턴 데이터 구조가 올바르지 않습니다.")

            pattern = info["input"]
            expected = normalize_label(info["expected"])

            if expected == "UNKNOWN":
                raise ValueError("정답 라벨 오류")

            filter_key = f"size_{size}"

            if filter_key not in data["filters"]:
                raise ValueError(f"{filter_key} 필터가 없습니다.")

            filters = data["filters"][filter_key]

            if not isinstance(filters, dict):
                raise ValueError("필터 데이터 구조가 올바르지 않습니다.")

            standard_filters = get_standard_filters(filters)

            if "Cross" not in standard_filters:
                raise ValueError("Cross 필터가 없습니다.")

            if "X" not in standard_filters:
                raise ValueError("X 필터가 없습니다.")

            cross_filter = standard_filters["Cross"]
            x_filter = standard_filters["X"]

            validate_matrix(pattern, size, "입력 패턴")
            validate_matrix(cross_filter, size, "Cross 필터")
            validate_matrix(x_filter, size, "X 필터")

            cross_score = mac_operation(pattern, cross_filter)
            x_score = mac_operation(pattern, x_filter)

            result = classify_labels(cross_score, x_score)

            status = "PASS" if result == expected else "FAIL"

            print(f"Cross 점수: {cross_score}")
            print(f"X 점수: {x_score}")
            print(f"판정 결과: {result}")
            print(f"기대 결과: {expected}")
            print(f"테스트 결과: {status}")

            if status == "PASS":
                passed += 1
            else:
                failed += 1
                failed_cases.append(
                    (key, "판정 결과와 정답이 일치하지 않습니다.")
                )

        except (KeyError, ValueError, TypeError, IndexError) as error:
            failed += 1
            failed_cases.append((key, str(error)))

            print("테스트 결과: FAIL")
            print(f"실패 사유: {error}")

    print("\n========== 전체 테스트 결과 ==========")
    print(f"전체 테스트: {total}개")
    print(f"통과: {passed}개")
    print(f"실패: {failed}개")

    if failed_cases:
        print("\n[실패 케이스 목록]")

        for case, reason in failed_cases:
            print(f"- {case}: {reason}")
    else:
        print("\n모든 테스트를 통과했습니다!")

    return failed_cases


# 크기별 성능 분석용 패턴 생성
def create_cross(size):
    return [
        [
            1 if i == size // 2 or j == size // 2 else 0
            for j in range(size)
        ]
        for i in range(size)
    ]


# 3×3, 5×5, 13×13, 25×25 성능 비교
def compare_size_performance(data=None):
    print("\n========== 크기별 성능 비교 ==========")
    print(f"{'크기':<12}{'평균 시간(ms)':<20}{'연산 횟수(N²)'}")

    for size in [3, 5, 13, 25]:
        try:
            if size == 3:
                pattern = create_cross(size)
                filter_data = create_cross(size)

            else:
                if data is None:
                    continue

                filters = data["filters"][f"size_{size}"]
                standard_filters = get_standard_filters(filters)

                pattern = create_cross(size)
                filter_data = standard_filters["Cross"]

                validate_matrix(pattern, size, "성능 측정 패턴")
                validate_matrix(filter_data, size, "성능 측정 필터")

            avg_time = measure_mac_time(pattern, filter_data)
            operation_count = size ** 2

            print(
                f"{size}×{size:<10}"
                f"{avg_time:<20.6f}"
                f"{operation_count}"
            )

        except (KeyError, ValueError, TypeError) as error:
            print(f"{size}×{size}: 측정 실패 - {error}")


# JSON 분석 모드
def json_analysis_mode():
    print("\n========== JSON 분석 모드 ==========")

    data = load_json_data()

    if data is None:
        return

    analyze_json_data(data)
    compare_size_performance(data)


# 프로그램 시작
def main():
    print("==============================")
    print("      Mini NPU Simulator")
    print("==============================")

    print("\n실행할 모드를 선택하세요.")
    print("1. 사용자 입력 (3×3)")
    print("2. JSON 데이터 분석")

    while True:
        choice = input("\n번호 입력: ").strip()

        if choice == "1":
            user_input_mode()
            break

        elif choice == "2":
            json_analysis_mode()
            break

        else:
            print("1 또는 2를 입력하세요.")


if __name__ == "__main__":
    main()
