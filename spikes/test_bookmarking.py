#!/usr/bin/env python3

#-----------------------------------------------------------------------------#
# Notes
#-----------------------------------------------------------------------------#

# I can't get this to work

#-----------------------------------------------------------------------------#
# Imports
#-----------------------------------------------------------------------------#
import json
import requests
import singer

#-----------------------------------------------------------------------------#
# Setup
#-----------------------------------------------------------------------------#

# Load in the a JSON object holding things like the refresh token
CONFIG = {}

with open('/tmp/gql_token') as input_file:
    CONFIG.update(json.load(input_file))


#-----------------------------------------------------------------------------#
# Constants
#-----------------------------------------------------------------------------#

# This query was tested in Insomnia first.

query1 = """query {
  products {
    complexity
    request_id
    data(first: 10, sort: "created_at") {
      pageInfo {
        hasNextPage
        startCursor
        endCursor
      }
      edges {
        node {
          id
          sku
          name
          warehouse_products {
            id
            warehouse_id
            on_hand
          }
          created_at
        }
      }
    }
  }
}"""

query2 = """query """

endpoint = 'https://public-api.shiphero.com/graphql'

headers = {"Authorization" : "Bearer " + CONFIG['access_token']}

#-----------------------------------------------------------------------------#
# Spiking
#-----------------------------------------------------------------------------#

# We will make a request for our expected set of data. Then examine the
# data, pick record somewhere in the middle of the set, grab the
# `created_at`, and make a new query to get records after that
# `created_at`. And we want the filtered set to match the expected set
# from some index on

# expected data:
# +---+---+---+---+---+
# | 0 | 1 | 2 | 3 | 4 |
# +---+---+---+---+---+
#           ^
#           | matches from here on
#           v
#         +---+---+---+
#         | 0 | 1 | 2 |
#         +---+---+---+
#           ^ fltered data:

def go_to_edges(resp):
    return resp['data']['products']['data']['edges']

def call_api_with(query):
    result = requests.post(endpoint,
                           json={'query': query},
                           headers=headers)
    result.raise_for_status()

    return result.json()


def run_test():
    expected_data = call_api_with(query1)
    filtered_data = call_api_with(query2)

    expected_data = go_to_edges(expected_data)
    filtered_data = go_to_edges(filtered_data)

    bookmark = datetime.now() # change me

    # This offset is for the expected data
    offset = 0 # change me

    # Did the filter actually work?
    for record in go_to_edges(filtered_data):
        record_created_at = singer.utils.strptime_to_utc(record['node']['created_at'])
        assert bookmark <= record_created_at

    # Does the filtered set sequence match the expected set?
    for i in range(len(filtered_data)):
        assert filtered_data[i] == expected_data[offset + i]

    return (expected_data, filtered_data)
