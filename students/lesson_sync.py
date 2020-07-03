from datetime import datetime, timedelta
import logging

from students.models import Lesson
from marengue import calendarpython

log = logging.getLogger('SyncMarengueCal')
log.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter(
    '%(asctime)s [%(levelname)s]: %(message)s'))
log.addHandler(console_handler)
file_handler = logging.FileHandler('sync_marengue.log')
file_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s'))
log.addHandler(file_handler)


googleCal = calendarpython.MarengueCal()


def get_or_none(model, *args, **kwargs):
    try:
        return model.objects.get(*args, **kwargs)
    except model.DoesNotExist:
        return None


def date_from_iso(event):
    return datetime.fromisoformat(event['updated'].replace('Z', '+00:00'))


def add_lesson_from_event(event):
    lesson = Lesson(student_id=1)

    log.debug(f"Add lesson from event: {event.get('start')}, with descr {event.get('description')}")

    if event['start'].get('dateTime') and event['end'].get('dateTime'):
        start_lesson = datetime.fromisoformat(event['start']['dateTime'])
        end_lesson = datetime.fromisoformat(event['end']['dateTime'])
        lesson.date = start_lesson
        lesson.lesson_long = int((end_lesson-start_lesson).seconds/60)
    else:
        lesson.lesson_long = 0

    lesson.googlecal_event_id = event['id']
    lesson.googlecal_updated = date_from_iso(event)
    lesson.googlecal_description = event.get('description')
    lesson.googlecal_summary = event.get('summary')
    lesson.googlecal_status = event['status']
    lesson.save()

    log.debug(f'lesson saved: {lesson.id}')


def update_lesson_from_event(lesson, event):
    log.debug(f'update lesson {lesson} from event {event}')

    if event['status'] == 'cancelled':
        lesson.googlecal_status = event['status']
        lesson.status = 4
        lesson.save()
        return

    if event['start'].get('dateTime') and event['end'].get('dateTime'):
        start_lesson = datetime.fromisoformat(event['start']['dateTime'])
        end_lesson = datetime.fromisoformat(event['end']['dateTime'])
        lesson.date = start_lesson
        lesson.lesson_long = int((end_lesson-start_lesson).seconds/60)
    else:
        lesson.lesson_long = 0

    lesson.googlecal_updated = date_from_iso(event)
    lesson.googlecal_description = event.get('description')
    lesson.googlecal_summary = event.get('summary')

    if 'OK' in event['description']:
        lesson.status = 1

    lesson.save()


def sync_new_lessons():
    new_lessons = Lesson.objects.filter(googlecal_event_id=None)

    log.debug(f'start syncing new lesson: {new_lessons}')

    for lesson in new_lessons:
        response = googleCal.add_event_to_marengue(**lesson.gcal_format)
        log.debug(f'added new event: {response["id"]} {response["description"]}')
        lesson.googlecal_event_id = response['id']
        lesson.googlecal_updated = date_from_iso(response)
        lesson.googlecal_description = response.get('description')
        lesson.googlecal_summary = response.get('summary')
        lesson.googlecal_status = response['status']
        lesson.save()
        log.debug(f'lesson {lesson.id} updated after add event')


def sync_updated_events(changed_events):
    if changed_events:
        log.debug('sync_updated_events started...')
        for event in changed_events:
            log.debug(f'find lesson for event {event["id"]}')
            lesson = get_or_none(Lesson, googlecal_event_id=event['id'])
            if lesson is None:
                if event['status'] == 'cancelled':
                    continue
                log.debug(f'no such lesson, try add new lesson')
                add_lesson_from_event(event)
            else:
                event_update = date_from_iso(event)
                log.debug(f'event {event["description"]} have date {event_update}')
                log.debug(f'lesson with same id {lesson.id} have date {lesson.googlecal_updated}')
                if event_update - lesson.googlecal_updated < timedelta(seconds=2):
                    log.debug(f'event is too old, skip')
                    continue
                update_lesson_from_event(lesson, event)
                log.debug(f'lesson {lesson.id} has been updated')


def sync_updated_lesson(sync_time_updated):
    log.debug(f'synd_updated_lesson started.. finding lesson updated after {sync_time_updated}')
    updated_lesson = Lesson.objects.filter(googlecal_updated__gt=sync_time_updated)
    if updated_lesson:
        for lesson in updated_lesson:
            event = googleCal.get_event_from_marengue(lesson.googlecal_event_id)
            event_update = date_from_iso(event)

            log.debug(f'lesson {lesson.id} have date {lesson.googlecal_event_id}')
            log.debug(f'event for this lesson {event["description"]} gave date {event_update}')

            if lesson.googlecal_updated - event_update < timedelta(seconds=2):
                log.debug(f'lesson is too old, skip')
                continue

            log.debug(f'try update event {evend["id"]}')
            response = googleCal.update_event_to_marengue(
                event_id=lesson.googlecal_event_id, **lesson.gcal_format)

            lesson.googlecal_updated = date_from_iso(response)
            lesson.googlecal_description = response.get('description')
            lesson.googlecal_summary = response.get('summary')
            lesson.googlecal_status = response['status']
            lesson.save()
            log.debug(f'lesson {lesson.id} updated after update event ')


def sync_event_and_lesson_through_token():
    log.debug('### syncing start')
    response = googleCal.marengue_token_events_list()
    changed_events = response['items']
    sync_time_updated = date_from_iso(response)
    sync_new_lessons()
    sync_updated_events(changed_events)
    sync_updated_lesson(sync_time_updated)
    log.debug('### syncing end')
