from datetime import datetime, timedelta


def build_reservation_datetimes(
    reservation_date: str, reservation_time: str, duration_hours: float
) -> tuple[datetime, datetime]:
    """
    Combines a date string, a time string, and a duration into start and end datetime objects.

    Args:
        reservation_date (str): Date in ISO format, e.g. "2025-06-26".
        reservation_time (str): Time in 24h format, e.g. "19:30".
        duration_hours (float): Duration in hours.

    Returns:
        tuple[datetime, datetime]: A tuple containing (start_datetime, end_datetime).

    Raises:
        ValueError: If the input date or time strings are not in the correct ISO format.
    """
    # Parse the combined ISO datetime string
    try:
        start_dt = datetime.fromisoformat(f"{reservation_date}T{reservation_time}")
    except ValueError as e:
        raise ValueError(
            f"Invalid date or time format: {reservation_date}T{reservation_time}"
        ) from e

    # Compute the end datetime by adding a timedelta
    end_dt = start_dt + timedelta(hours=duration_hours)

    return start_dt, end_dt
