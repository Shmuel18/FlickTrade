from datetime import datetime, timezone
import pytz

now = datetime.now(timezone.utc)
israel_tz = pytz.timezone("Asia/Jerusalem")
israel_time = now.astimezone(israel_tz)

print(f"Current UTC time: {now}")
print(f"Current Israel time: {israel_time}")
print(f"\nThe market 'Bitcoin above 84k on January 8' closes at:")
print("  12PM UTC on January 8, 2026")
print(f"\nCurrent date: January 7, 2026")
print(f"Hours until 12PM Jan 8 UTC: {(datetime(2026, 1, 8, 12, 0, 0, tzinfo=timezone.utc) - now).total_seconds() / 3600:.1f}h")
