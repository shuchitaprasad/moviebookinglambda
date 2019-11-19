
import json
import os
import logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def fetchMovieList():

    return  [
  {
    'name': 'Mangal Mission',
    'slotDetails': [
      {
        'slots': '9am',
        'price': '500'
      },
      {
        'slots': '1pm',
        'price': '700'
      }
    ]
  },
  {
    'name': 'WAR',
    'slotDetails': [
      {
        'slots': '10pm',
        'price': '400'
      },
      {
        'slots': '12pm',
        'price': '600'
      }
    ]
  }
]



