from fastapi import HTTPException, status
from datetime import time 

from sql import models
from models import schemas


def check_days(days: list[schemas.Day]):
    days_sorted = set(days)
    if len(days_sorted) != len(days):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="There are repeating days"
        )


def check_time(start_time: list[time], end_time:list[time]):
    if len(start_time) != len(end_time):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No time entered"
        )
    for i in range(len(start_time) - 1):
        if start_time[i+1] < end_time[i] or start_time[i] > end_time[i]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect time"
            )
    if start_time[-1] > end_time[-1]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect time"
        )


def validate_upper_week_items(upper_week_items: list[models.UpperWeek]) -> list[schemas.UpperWeek]:
    valid_upper_week_items = []
    for upper_day_items in upper_week_items:
        valid_upper_day_subjects = []
        for upper_day_subject in upper_day_items.subjects:  # type: ignore
            valid_upper_day_subject = validate_upper_day_subject(upper_day_subject)
            valid_upper_day_subjects.append(valid_upper_day_subject)
        valid_upper_day_items = validate_upper_week(upper_day_items, valid_upper_day_subjects)
        valid_upper_week_items.append(valid_upper_day_items)
    return valid_upper_week_items


def validate_upper_day_subject(upper_day_subject: models.UpperDaySubjects) -> schemas.UpperDaySubjects:
    return schemas.UpperDaySubjects(
        id = upper_day_subject.id,  # type: ignore
        id_upper_week = upper_day_subject.id_upper_week,  # type: ignore
        subject=upper_day_subject.subject,  # type: ignore
        start_time=upper_day_subject.start_time,  # type: ignore
        end_time=upper_day_subject.end_time,  # type: ignore
    )


def validate_upper_week(
    upper_day_items: models.UpperWeek,
    upper_day_subjects: list[schemas.UpperDaySubjects],
    ) -> schemas.UpperWeek:
    return schemas.UpperWeek(
        id=upper_day_items.id,  # type: ignore
        id_timetable=upper_day_items.id_timetable,  # type: ignore
        day=upper_day_items.day,  # type: ignore
        subjects=upper_day_subjects
        )


def validate_lower_week_items(lower_week_items: list[models.LowerWeek]) -> list[schemas.LowerWeek]:
    valid_lower_week_items = []
    for lower_day_items in lower_week_items:
        valid_lower_day_subjects = []
        for lower_day_subject in lower_day_items.subjects:  # type: ignore
            valid_lower_day_subject = validate_lower_day_subject(lower_day_subject)
            valid_lower_day_subjects.append(valid_lower_day_subject)
        valid_lower_day_items = validate_lower_week(lower_day_items, valid_lower_day_subjects)
        valid_lower_week_items.append(valid_lower_day_items)
    return valid_lower_week_items


def validate_lower_day_subject(lower_day_subject: models.LowerDaySubjects) -> schemas.LowerDaySubjects:
    return schemas.LowerDaySubjects(
        id = lower_day_subject.id,  # type: ignore
        id_lower_week = lower_day_subject.id_lower_week,  # type: ignore
        subject=lower_day_subject.subject,  # type: ignore
        start_time=lower_day_subject.start_time,  # type: ignore
        end_time=lower_day_subject.end_time,  # type: ignore
    )


def validate_lower_week(
    lower_day_items: models.LowerWeek,
    lower_day_subjects: list[schemas.LowerDaySubjects],
    ) -> schemas.LowerWeek:
    return schemas.LowerWeek(
        id=lower_day_items.id,  # type: ignore
        id_timetable=lower_day_items.id_timetable,  # type: ignore
        day=lower_day_items.day,  # type: ignore
        subjects=lower_day_subjects
        )