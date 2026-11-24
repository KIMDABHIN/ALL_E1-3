
import json


def create_cross(size):
    return [
        [
            1 if i == size // 2 or j == size // 2 else 0
            for j in range(size)
        ]
        for i in range(size)
    ]


def create_x(size):
    return [
        [
            1 if i == j or i + j == size - 1 else 0
            for j in range(size)
        ]
        for i in range(size)
    ]


data = {
    "filters": {},
    "patterns": {}
}


for size in [5, 13, 25]:
    cross = create_cross(size)
    x = create_x(size)

    data["filters"][f"size_{size}"] = {
        "cross": cross,
        "x": x
    }

    data["patterns"][f"size_{size}_1"] = {
        "input": cross,
        "expected": "+"
    }

    data["patterns"][f"size_{size}_2"] = {
        "input": x,
        "expected": "x"
    }


with open("data.json", "w", encoding="utf-8") as file:
    json.dump(data, file, ensure_ascii=False, indent=2)


print("데이터 생성 완료!")
print("생성된 크기: 5x5, 13x13, 25x25")
print("전체 패턴 수:", len(data["patterns"]))
