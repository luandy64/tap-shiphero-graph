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

query_for_expected_data = """query {
  products {
    complexity
    request_id
    data(first: 20, sort: "created_at") {
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

first_query = """query {
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

second_query = """query {
  products {
    complexity
    request_id
    data(first: 10, sort: "created_at", after: "%s") {
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

endpoint = 'https://public-api.shiphero.com/graphql'

headers = {"Authorization" : "Bearer " + CONFIG['access_token']}

#-----------------------------------------------------------------------------#
# Spiking
#-----------------------------------------------------------------------------#

# We will make a request for our expected set of data containing 20
# records. Then we will ask again for the first 10, note the `endCursor`
# and ask for anothe r 10 with the `endCursor` in the request. Ideally
# these match

def go_to_edges(resp):
    return resp['data']['products']['data']['edges']

def call_api_with(query):
    result = requests.post(endpoint,
                           json={'query': query},
                           headers=headers)
    result.raise_for_status()

    return result.json()


def run_test():
    expected_data = call_api_with(query_for_expected_data)
    expected_data = go_to_edges(expected_data)
    
    part1 = call_api_with(first_query)

    # Get the `endCursor`
    cursor_to_start_from = part1['data']['products']['data']['pageInfo']['endCursor']

    part2 = call_api_with(second_query % (cursor_to_start_from))

    actual_data = go_to_edges(part1) + go_to_edges(part2)

    for i in range(20):
        assert expected_data[i] == actual_data[i]
