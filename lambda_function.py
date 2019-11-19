"""
This sample demonstrates an implementation of the Lex Code Hook Interface
in order to serve a sample bot which manages booking of movie tickets.

"""
import math
import dateutil.parser
import datetime
import time
import os
import logging
import json
import movielist

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

""" --- Helpers to build responses which match the structure of the necessary dialog actions --- """


def get_slots(intent_request):
    return intent_request['currentIntent']['slots']


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message
        }
    }


def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }

    return response


def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }


""" --- Helper Functions --- """


def parse_int(n):
    try:
        return int(n)
    except ValueError:
        return float('nan')


def build_validation_result(is_valid, violated_slot, content, message_content, sessionAttributes):
    if message_content is None:
        return {
            "isValid": is_valid,
            "violatedSlot": violated_slot,
        }

    return {
        'isValid': is_valid,
        'violatedSlot': violated_slot,
        'message': {'contentType': content, 'content': message_content},
        'sessionAttributes': sessionAttributes
    }


def isvalid_date(date):
    try:
        dateutil.parser.parse(date)
        return True
    except ValueError:
        return False


# Create a map with movie name as key and slots with prices as  values
def createmovielookupmap(movienamesList):
    logger.debug("Creating Category Map {}".format(movienamesList))
    moviesLookup = {}

    for moviename in movienamesList:
        synonyms = moviename['name']
        moviesLookup[synonyms] = moviename['slotDetails']

    logger.debug("Created Category Map:: {}".format(moviesLookup))
    return moviesLookup


def validate_movie_tickets_input(intent_request):
    sessionAttributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}
    # fetch all the slot values
    bookingDate = get_slots(intent_request)["bookingDate"]
    movieName = get_slots(intent_request)["movieName"]
    bookingSlot = get_slots(intent_request)["bookingSlot"]
    numbrOfTickets = get_slots(intent_request)['numbrOfTickets']
    customername = get_slots(intent_request)['customerName']

    # validation for booking date not null
    if bookingDate is None:
        "-- if the user has not selected any movie --"
        return build_validation_result(False, 'bookingDate', 'PlainText', 'Please specify the date of booking', None)

    else:
        # validation for invalid booking date
        if not isvalid_date(bookingDate):
            return build_validation_result(False, 'bookingDate', 'PlainText',
                                           'I did not understand that, what date would you like to book the tickets '
                                           'for?', None)
        elif datetime.datetime.strptime(bookingDate, '%Y-%m-%d').date() < datetime.date.today():
            return build_validation_result(False, 'bookingDate', 'PlainText', 'Booking date cannot be of the past',
                                           None)
    "-- fetch movie name by api call/ being fetch from ahrd coded JSON --"
    if movieName is None:
        moviedetailslist = movielist.fetchMovieList();

        movie_lookup = createmovielookupmap(moviedetailslist)
        movienamesonly = []
        for moviedetails in moviedetailslist:
            movienamesonly.append(moviedetails['name'])

        return build_validation_result(False, 'movieName', 'PlainText',
                                       'Please choose from the given movies ' + ','.join(movienamesonly),
                                       json.dumps(movie_lookup))

        # return build_validation_result(False, 'movieName', 'CustomPayload', json.dumps(moviedetailslist),
        # json.dumps(movie_lookup))

    if bookingSlot is None:
        "-- if the user has  selected  movie, it should be present in the list of movies which the  user was shown to--"
        if sessionAttributes.get('moviedetails_lookup', None) is None:
            return build_validation_result(False, 'movieName', 'PlainText',
                                           'Please enter movie name from the list only',
                                           None)
        # fetch the slot details based on movie selected
        else:

            time_slots = []
            # convert the session attribute string to dictionary/map
            moviedetails_lookup = eval(sessionAttributes['moviedetails_lookup'])

            logger.debug("SELECTED MOVIE :: {}".format(moviedetails_lookup.get(movieName)))

            """---find the booking slot as per the movie selected----"""
            for slot in moviedetails_lookup.get(movieName):
                time_slots.append(slot['slots'])
            return build_validation_result(False, 'bookingSlot', 'PlainText',
                                           'Please select from  the available slots for the movie ' + ','.join(
                                               time_slots),
                                           None)

    else:
        if len(bookingSlot) != 5:
            # Not a valid time; use a prompt defined on the build-time model.
            return build_validation_result(False, 'bookingSlot', 'PlainText', 'Not a valid time', None)

        hour, minute = bookingSlot.split(':')
        hour = parse_int(hour)
        minute = parse_int(minute)
        if math.isnan(hour) or math.isnan(minute):
            # Not a valid time; use a prompt defined on the build-time model.
            return build_validation_result(False, 'bookingSlot', 'PlainText', 'Not a valid time', None)

    if customername is None:
        return build_validation_result(False, 'customerName', 'PlainText', 'Please specify the name against which the '
                                                                           'booking needs to be done', None)

    if numbrOfTickets is None:
        return build_validation_result(False, 'numbrOfTickets', 'PlainText', 'Please specify the number of tickets '
                                                                             'required', None)

    return build_validation_result(True, None, None, None, None)


""" --- Functions that control the bot's behavior --- """


def book_movie_tickets(intent_request):
    """
    Performs dialog management and fulfillment for booking movie  tickets.
    Beyond fulfillment, the implementation of this intent demonstrates the use of the elicitSlot dialog action
    in slot validation and re-prompting.
    """
    sessionAttributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}
    bookingDate = get_slots(intent_request)["bookingDate"]
    movieName = get_slots(intent_request)["movieName"]
    bookingSlot = get_slots(intent_request)["bookingSlot"]
    numbrOfTickets = get_slots(intent_request)['numbrOfTickets']
    customername = get_slots(intent_request)['customerName']
    source = intent_request['invocationSource']

    if source == 'DialogCodeHook':
        # Perform basic validation on the supplied input slots.
        # Use the elicitSlot dialog action to re-prompt for the first violation detected.
        slots = get_slots(intent_request)

        validation_result = validate_movie_tickets_input(intent_request)
        if not validation_result['isValid']:
            if validation_result.get('sessionAttributes', None) is None:
                slots[validation_result['violatedSlot']] = None
                return elicit_slot(intent_request['sessionAttributes'],
                                   intent_request['currentIntent']['name'],
                                   slots,
                                   validation_result['violatedSlot'],
                                   validation_result['message'])
            # nothing in session attributes
            else:
                slots[validation_result['violatedSlot']] = None
                if validation_result['violatedSlot'] == 'movieName':
                    sessionAttributes['moviedetails_lookup'] = validation_result['sessionAttributes'];

                return elicit_slot(sessionAttributes,
                                   intent_request['currentIntent']['name'],
                                   slots,
                                   validation_result['violatedSlot'],
                                   validation_result['message'])

    return close(intent_request['sessionAttributes'],
                 'Fulfilled',
                 {'contentType': 'PlainText',
                  'content': 'Thanks, your {} ticket for {} has been booked for date {} and slot {} against name {}'.format(
                      numbrOfTickets, movieName, bookingDate, bookingSlot, customername)})


""" --- Intents --- """


def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    logger.debug(
        'dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))

    intent_name = intent_request['currentIntent']['name']

    # If the intent is the one which you created, Dispatch to your bot's intent handlers
    if intent_name == 'BookMovieTickets':
        return book_movie_tickets(intent_request)

    raise Exception('Intent with name ' + intent_name + ' not supported')


""" --- Main handler --- """


def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """
    # By default, treat the user request as coming from the America/New_York time zone.
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    logger.debug('event.bot.name={}'.format(event['bot']['name']))

    return dispatch(event)
