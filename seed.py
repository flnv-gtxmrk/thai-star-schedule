"""
Seed script — Add sample data for testing
"""
from datetime import date, timedelta
from app import app
from models import db, User, Schedule


def seed():
    with app.app_context():
        # Create tables
        db.create_all()

        # Check if data exists
        if User.query.count() > 0:
            print("Data already exists. Skipping seed.")
            return

        # Create demo users
        users = []
        demo_users = [
            ("alice", "alice@example.com", "password123"),
            ("bob", "bob@example.com", "password123"),
            ("charlie", "charlie@example.com", "password123"),
        ]

        for username, email, password in demo_users:
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            users.append(user)

        db.session.commit()
        print(f"Created {len(users)} demo users")

        # Sample schedule data
        today = date.today()
        schedules = [
            # Solo
            {
                "star_name": "Baifern Pimchanok",
                "star_name_en": "Baifern Pimchanok",
                "star_name_th": "ใบเฟิร์น พิมพ์ชนก",
                "event_name": "Fan Meeting in Bangkok",
                "event_name_en": "Fan Meeting in Bangkok",
                "event_name_th": "แฟนมีตติ้งที่กรุงเทพ",
                "event_date": today + timedelta(days=5),
                "event_time": "19:00",
                "event_location": "Siam Paragon, Bangkok",
                "event_location_en": "Siam Paragon, Bangkok",
                "event_location_th": "สยามพารากอน กรุงเทพ",
                "group_type": "solo",
            },
            {
                "star_name": "Bright Vachirawit",
                "star_name_en": "Bright Vachirawit",
                "star_name_th": "ไบร์ท วชิรวิชญ์",
                "event_name": "Concert: Bright Night",
                "event_name_en": "Concert: Bright Night",
                "event_name_th": "คอนเสิร์ต: ไบร์ทไนท์",
                "event_date": today + timedelta(days=8),
                "event_time": "20:00",
                "event_location": "Impact Arena, Bangkok",
                "event_location_en": "Impact Arena, Bangkok",
                "event_location_th": "อิมแพ็ค อารีน่า กรุงเทพ",
                "group_type": "solo",
            },
            # Duo
            {
                "star_name": "Freen & Becky",
                "star_name_en": "Freen & Becky",
                "star_name_th": "ฟรีน & เบคกี้",
                "event_name": "Double Fan Meeting",
                "event_name_en": "Double Fan Meeting",
                "event_name_th": "แฟนมีตติ้งคู่",
                "event_date": today + timedelta(days=10),
                "event_time": "18:00",
                "event_location": "Union Hall, Bangkok",
                "event_location_en": "Union Hall, Bangkok",
                "event_location_th": "ยูเนี่ยนฮอลล์ กรุงเทพ",
                "group_type": "duo",
            },
            {
                "star_name": "Billkin & PP Krit",
                "star_name_en": "Billkin & PP Krit",
                "star_name_th": "บิวกิ้น & พีพี กฤษฏ์",
                "event_name": "Joint Concert Tour",
                "event_name_en": "Joint Concert Tour",
                "event_name_th": "คอนเสิร์ตทัวร์ร่วม",
                "event_date": today + timedelta(days=18),
                "event_time": "20:00",
                "event_location": "Rajamangala Stadium, Bangkok",
                "event_location_en": "Rajamangala Stadium, Bangkok",
                "event_location_th": "ราชมังคลากีฬาสถาน กรุงเทพ",
                "group_type": "duo",
            },
            # Group
            {
                "star_name": "GMMTV Starlympic 2026",
                "star_name_en": "GMMTV Starlympic 2026",
                "star_name_th": "GMMTV สตาร์ลิมปิก 2026",
                "event_name": "Annual Sports Day",
                "event_name_en": "Annual Sports Day",
                "event_name_th": "วันกีฬาประจำปี",
                "event_date": today + timedelta(days=22),
                "event_time": "13:00",
                "event_location": "Thammasat Stadium, Bangkok",
                "event_location_en": "Thammasat Stadium, Bangkok",
                "event_location_th": "สนามธรรมศาสตร์ กรุงเทพ",
                "group_type": "group",
            },
        ]

        # Create schedules
        for i, data in enumerate(schedules):
            schedule = Schedule(
                creator_id=users[i % len(users)].id,
                **data
            )
            db.session.add(schedule)

        db.session.commit()
        print(f"Created {len(schedules)} sample schedules")
        print("\nDemo accounts:")
        for username, _, password in demo_users:
            print(f"  - {username} / {password}")


if __name__ == "__main__":
    seed()
