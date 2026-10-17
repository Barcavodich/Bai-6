from datetime import datetime, timedelta
from borrowing import BorrowingSlip
from exceptions import BorrowingException
from models import (
    AirConditionerRemote,
    DeviceStatus,
    Lecturer,
    Microphone,
    ProjectorRemote,
    TeachingAssistant,
)


def main():
  print("=== CHƯƠNG TRÌNH QUẢN LÝ THIẾT BỊ HỌC TẬP ===")

  # Luồng thành công
  try:
    gv = Lecturer("GV001", "Nguyễn Văn A")
    pj = ProjectorRemote("P01", "Máy chiếu Sony", 2024, 500000)
    mic = Microphone("M01", "Micro Shure", 2025, 1200000)

    slip = BorrowingSlip("SLIP01", gv, "P301", datetime.now())
    slip.add_device(pj, 5)
    slip.add_device(mic, 2)
    print("[OK] Thêm thiết bị vào phiếu thành công.")

    fee1 = slip.return_device("P01", datetime.now() + timedelta(days=3))
    print(f"Phí phạt P01: {fee1:,.0f} VNĐ")

    fee2 = slip.return_device("M01", datetime.now() + timedelta(days=4))
    print(f"Phí phạt M01: {fee2:,.0f} VNĐ")
    print(f"Tổng phí phạt: {slip.calculate_total_late_fee():,.0f} VNĐ\n")
  except Exception as e:
    print("Lỗi luồng thành công:", e)

  # Kiểm thử các ngoại lệ
  print("=== KIỂM THỬ CÁC TÌNH HUỐNG NGOẠI LỆ ===")
  tests = [
      (
          "Mượn điều hòa đang bảo trì",
          lambda: BorrowingSlip(
              "S2", Lecturer("GV2", "B"), "P102", datetime.now()
          ).add_device(
              AirConditionerRemote(
                  "A2", "Hỏng", 2022, 500, DeviceStatus.UNDER_MAINTENANCE
              ),
              2,
          ),
      ),
      (
          "Trợ giảng mượn vượt quá 2 thiết bị",
          lambda: (
              lambda s=BorrowingSlip(
                  "S3", TeachingAssistant("TA1", "C"), "P201", datetime.now()
              ): [
                  s.add_device(
                      ProjectorRemote(f"P{i}", f"P{i}", 2024, 100), 1
                  )
                  for i in range(3)
              ]
          )(),
      ),
      (
          "Thêm trùng thiết bị vào phiếu",
          lambda: (
              s := BorrowingSlip(
                  "S4", Lecturer("GV3", "D"), "P302", datetime.now()
              ),
              m := Microphone("M99", "Mic", 2025, 1000),
              s.add_device(m, 1),
              s.add_device(m, 1),
          ),
      ),
      (
          "Mượn Micro quá ngày cho phép",
          lambda: BorrowingSlip(
              "S5", Lecturer("GV4", "E"), "P303", datetime.now()
          ).add_device(Microphone("M88", "Mic VIP", 2025, 1000), 5),
      ),
      (
          "Trả thiết bị không có trong phiếu",
          lambda: BorrowingSlip(
              "S6", Lecturer("GV5", "F"), "P304", datetime.now()
          ).return_device("NOT_EXIST", datetime.now()),
      ),
      (
          "Trả thiết bị hai lần",
          lambda: (
              s := BorrowingSlip(
                  "S7", Lecturer("GV6", "G"), "P305", datetime.now()
              ),
              dev := ProjectorRemote("PT", "Test", 2024, 1000),
              s.add_device(dev, 2),
              s.return_device("PT", datetime.now()),
              s.return_device("PT", datetime.now()),
          ),
      ),
      (
          "Ngày trả trước ngày mượn",
          lambda: (
              s := BorrowingSlip(
                  "S8", Lecturer("GV7", "H"), "P306", datetime.now()
              ),
              dev := ProjectorRemote("PT2", "Test2", 2024, 1000),
              s.add_device(dev, 2),
              s.return_device("PT2", datetime.now() - timedelta(days=5)),
          ),
      ),
  ]

  for name, action in tests:
    print(f"- {name}: ", end="")
    try:
      action()
      print("THẤT BẠI (Lẽ ra phải bắn ngoại lệ)")
    except (BorrowingException, ValueError) as ex:
      print(f"THÀNH CÔNG -> Bắt lỗi: {ex}")
    except Exception as ex:
      print(f"Lỗi khác: {ex}")


if __name__ == "__main__":
  main()