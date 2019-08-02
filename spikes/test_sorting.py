#!/usr/bin/env python3

#-----------------------------------------------------------------------------#
# Notes
#-----------------------------------------------------------------------------#

# Perhaps I only saw this because the queries I have been using are pretty
# simple, but sorting the result set does not add to the complexity of the
# request. I used the (unsorted) query from `test_client_libraries` and
# gave it the `sort` param here.

# To sort a result set:

# - On "Connection Fields", pass a parameter `sort: <fields>` where
# `fields` is the list of things you want to sort by

#   - What is a "Connection Field" though? The Shiphero docs don't say,
#     but maybe that's a term from the GraphQL Spec

#-----------------------------------------------------------------------------#
# Imports
#-----------------------------------------------------------------------------#
import json
import requests

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
query = """query {
  products {
    complexity
    request_id
    data(first: 10, sort: "created_at") {
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

# Can we make a request for the objects to come back sorted?
# - Default is ascending

def get_ascending():
    result = requests.post(endpoint,
                           json={'query': query},
                           headers=headers)
    result.raise_for_status()
    #result = result.json()

    return result

# What could processing look like?

def get_records():
    raw_results = get_ascending().json()

    # Descend into the results like wanted in the request
    records = raw_results['data']['products']['data']['edges']

    for record in records:
        # Note that each record here is wrapped in the 'node' object.
        # 'edges' was a nice enough spot to drill down to because its
        # value was a list we can iterate through.
        print(record)
