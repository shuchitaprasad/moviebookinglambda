# moviebookinglambda
This repository has code for Lambda attached to Movie booking AWS Lex bot

lambda_handler - The entry point in the Lambda

dispatch -verifies the intent names and dispatches control to the intent handler

book_movie_tickets - method which validates the slots, and also puts moviedetails_lookup map in session attributes, when the empty slot is movie name

validate_movie_tickets_input- the mothod which validates all the slots.

createmovielookupmap - the method which creates map where movie name is key and values is list of movie tinings with prices

elicit_slot -- ensures, Ellicit Slot stage is ensures.

close- ensures fullfillment state

movielist.py has hard coded JSON which should be replaced by api call.
