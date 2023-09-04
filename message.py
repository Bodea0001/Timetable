from config import USER_TIMETABLES_LIMIT


APPLICATION_TO_USER_TIMETABLE = """Зачем подавать заявку на добавление к 
расписанию, которое к которому уже добавлен?🤔"""

DUPLICATE_APPLICATION = """Вы уже подавали заявку на добавление 
к данному расписанию!😅"""

APPLICATION_NOT_FOUND = """Такой заявки не существует!😣 Возможно ее удалили"""

APPLICATION_HAS_BEEN_CREATED = """Заявка на добавление к расписанию отправлена👍"""

APPLICATION_HAS_BEEN_ACCEPTED = """Пользователь добавлен к расписанию👍"""

APPLICATION_HAS_BEEN_REJECTED = """Заявка была отклонена👍"""

APPLICATION_HAS_BEEN_DELETED = """Заявка удалена👍"""

DELETING_TIMETABLE = """Расписание удалено👍"""

LEAVING_TIMETABLE = """Вы покинули расписание👍"""

TIMETABLE_NOT_FOUND = """Такого расписания не существует!😣"""

TIMETABLE_LIMIT_HAS_BEEN_REACHED = f"""Пользователь достиг лимита расписаний!😱 
Нельзя иметь больше {USER_TIMETABLES_LIMIT} расписаний!"""

DUPLICATE_OF_TIMETABLE_NAME = """У Вас уже есть расписание с таким названием!😰"""

DUPLICATE_TIMETABLE = """Уже существует расписание с такими данными!😰"""

USER_NOT_FOUND = """Такого пользователя не существует!😰"""

USER_DOESNT_HAVE_TIMETABLE = """У Вас нет такого расписания!😣"""

USER_DOESNT_HAVE_ENOUGH_RIGHTS = """У Вас недостаточно прав в этом расписании!😰"""

USERS_CANT_CREATE_TASKS_FOR_OTHER = """Только староста может создавать задачи 
для других поьлзователей в расписании!😰"""

USER_IS_NOT_TASK_CREATOR = """Вы не являетесь создателем задачи!😰"""

NOT_ALL_USERS_ARE_ATTACHED_TO_TIMETALBE = """Не все пользователи прикреплены к 
расписанию!😰"""

INCORRECT_EMAIL = """Некорректная почта!😰"""

ELDER_CANT_LEAVE = "Староста не может покинуть расписание!😣"

UNIVERSITY_NOT_FOUND = """Такого университета нет в нашей базе!😣"""

EDUCATION_LEVEL_NOT_FOUND = """Такого уровня образования не существует!😣"""

SPEC_NAME_WIHTOUT_EDUC_LEVEL = """Если Вы написали наименование специальности, 
то нужно также выбрать уровень образования!😰"""

SPECIALIZATION_NOT_FOUND = """Такой специальности нет в нашей базе!😣"""

INVALID_COURSE = """Курс указан неверно!😰"""

INVALID_NAMING = """Некорректное наименование!😰"""

ARGUMENTS_NOT_PASSED = """Не передано ни одного аргумента!😰"""

SEARCH_YIELDED_NO_RESULTS = """Поиск не дал результатов!😟"""

TASK_NOT_FOUND = """Такой задачи не нашлось!😣"""

TASKS_NOT_FOUND = """Задач не нашлось!😣"""

TASK_DELETED = """Задача удалена👍"""

TASK_IS_NOT_ATTACHED_TO_TIMETABLE = """Данная задача не прикрепрелена к данному 
расписанию!😰"""

TASK_IS_NOT_ATTACHED_TO_USER = """Вы не прикреплены к данной задаче!😰"""

INVALID_ID = """Неправильный ID!😓"""

WEEKLY_TIMETABLE_ALREADY_EXISTS = """Расписание на неделю уже существует!😰"""

WEEK_NOT_FOUND = """Недельного расписания не нашлось!😣"""

DUPLICATE_DAYS = """Есть повторяющиеся дни!😓"""

DUPLICATE_SUBJECTS = """Есть повторяющиеся предметы!😓"""

DAY_ALREADY_EXISTS = """Уже существует расписание на этот день!😣"""

WEEKLY_TIMETABLE_HAS_BEEN_DELETED = """Недельное расписание удалено👍"""

DAILY_TIMETABLE_HAS_BEEN_DELETED = """Дневное расписание удалено👍"""

SUBJECT_NOT_FOUND_IN_TIMETABLE = """Данного предмета не нашлось в расписании"""

SUBJECT_HAS_BEEN_DELETED = """Предмет в расписании удалён👍"""

UNKNOWN_REFRESH_TOKEN = """Такой токен не найден!😰"""

UNKNOWN_USER_WHITE_IP = """Пользователь не заходил под таким ip!😓"""

LOGOUT = """Выход выполнен👍"""

UPDATING_DAY_IDS_NOT_EXISTS = """Присутствуют id дней, которые не принадлежат 
данному распиcанию!😰"""

UPDATING_SUBJECT_IDS_NOT_EXISTS = """Присутствуют id предметов, которые не 
принадлежат данному распиcанию!😰"""

INCORRECT_TIME = """Некорректное время!😓"""

NO_TIME_ENTERED = """Время не введено!😓"""

PASSWORDS_MATCH = """Ваш пароль совпадает паролем для изменения!😓"""

PASS_CHANGE_REQUEST_CREATED = """Запрос на изменение пароля создан👍"""

PASS_CHANGE_REQUEST_APPROVED = """Запрос на изменение пароля одобрен👍"""

PASS_CHANGE_REQUEST_NOT_FOUND = """Запрос на изменение проля не найден!😣"""
