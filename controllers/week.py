from fastapi import HTTPException, status
from datetime import time 

from sql import models
from models import schemas


def check_week_and_subject_ids(timetable_week_items: list[schemas.UpperWeek] | list[schemas.LowerWeek], weekly_timetable: list[schemas.WeekUpdate]):
    check_week_ids(timetable_week_items, weekly_timetable)
    check_subject_ids(timetable_week_items, weekly_timetable)


def check_week_ids(timetable_week_items: list[schemas.UpperWeek] | list[schemas.LowerWeek], weekly_timetable: list[schemas.WeekUpdate]):
    week_ids = {upper_day.id for upper_day in timetable_week_items}
    submitted_week_id_list = [upper_day.id for upper_day in weekly_timetable]
    submitted_week_ids = set(submitted_week_id_list)
    if len(submitted_week_id_list) != len(submitted_week_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="There are duplicate week ids"
        )
    if not week_ids.issuperset(submitted_week_ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unknown week id"
        )


def check_subject_ids(
    timetable_week_items: list[schemas.UpperWeek] | list[schemas.LowerWeek],
    weekly_timetable: list[schemas.WeekUpdate],
):
    submitted_week_id_list = [upper_day.id for upper_day in weekly_timetable]
    subject_ids = {subject.id for upper_day in timetable_week_items for subject in upper_day.subjects}
    submitted_subject_id_list = [subject.id for upper_day in weekly_timetable for subject in upper_day.subjects]
    submitted_subject_ids = set(submitted_subject_id_list)
    if len(submitted_subject_id_list) != len(submitted_subject_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="There are duplicate subject ids"
        )
    
    timetable_week_items.sort(key=lambda value: value.id)  # type: ignore
    submitted_week_id_list.sort()
    subject_ids = [{subject.id for subject in upper_day.subjects} for upper_day in timetable_week_items if upper_day.id in submitted_week_id_list]
    submitted_subject_ids = [{subject.id for subject in upper_day.subjects} for upper_day in weekly_timetable]
    for i in range(len(subject_ids)):
        if not subject_ids[i].issuperset(submitted_subject_ids[i]):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Unknown subject id"
            )


def check_day_in_timetable(
    week_name: schemas.WeekName,
    day_id: int,
    timetable: schemas.TimetableOut
) -> schemas.UpperWeek | schemas.LowerWeek:
    if week_name == schemas.WeekName.UPPER and timetable.upper_week_items:
        for day in timetable.upper_week_items:
            if day_id == day.id:
                return day
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Unknown day's id"
            )
    elif week_name == schemas.WeekName.LOWER and timetable.lower_week_items:
        for day in timetable.lower_week_items:
            if day_id == day.id:
                return day
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Unknown day's id"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The weekly timetable doesn't exists"
        )


def check_subject_id_in_timetable(
    week_name: schemas.WeekName,
    subject_id: int,
    timetable: schemas.TimetableOut
) -> schemas.UpperDaySubjects | schemas.LowerDaySubjects:
    if week_name == schemas.WeekName.UPPER and timetable.upper_week_items:
        for day in timetable.upper_week_items:
            for subject in day.subjects:
                if subject_id == subject.id:
                    return subject
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Unknown subject's id"
            )
    elif week_name == schemas.WeekName.LOWER and timetable.lower_week_items:
        for day in timetable.lower_week_items:
            for subject in day.subjects:
                if subject_id == subject.id:
                    return subject
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Unknown subject's id"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The weekly timetable doesn't exists"
        )


def check_days(days: list[schemas.Day]):
    days_sorted = set(days)
    if len(days_sorted) != len(days):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="There are duplicate days"
        )


def append_subject_time(
    daily_subject: schemas.DaySubjectsBase,
    start_time_list: list[time],
    end_time_list: list[time]
):
    if daily_subject.start_time in start_time_list or daily_subject.end_time in end_time_list:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This time is already occupied"
        )
    for i in range(len(start_time_list)):
        if daily_subject.start_time < start_time_list[i]:
            start_time_list.insert(i, daily_subject.start_time)
            end_time_list.insert(i, daily_subject.end_time)
            break
    else:
        start_time_list.append(daily_subject.start_time)
        end_time_list.append(daily_subject.end_time)


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