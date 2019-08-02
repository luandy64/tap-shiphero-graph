#!/usr/bin/env python3

#-----------------------------------------------------------------------------#
# Notes
#-----------------------------------------------------------------------------#

# I found 3 GraphQL client libraries to play with:
#   - gql
#   - graphqlclient
#   - sgqlc

# The first two install fine, but sgqlc needs `python >=3.6`
#   - Using pyenv to set up a 3.6 virtualenv was easy enough

# Option 4 is to just POST to the API with `requests`

# It seems like you should never lose the refresh token or else you have
# to hit the original auth endpoint again and get a new one.

# The way I was running these was:
# ```
# python -i test1.py
# ```

# This drops you in a repl and these functions are already defined so you
# can call them and inspect the results

#-----------------------------------------------------------------------------#
# Imports
#-----------------------------------------------------------------------------#
import json
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
import graphqlclient
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

# In the Shiphero docs, they describe this idea of a quota. And you are
# given a certain number of credits that refresh after some time. The
# `analyze : true` param does not run the query, but calculates the cost
# of the query.

# I'm using it here so I don't expend too many credits in testing
query = """query {
    products(analyze : true) {
        complexity
        request_id
        data(first: 10) {
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
                }
            }
        }
    }
}"""

# Our expected response looks something like this. I mainly care about the
# complexity being the same
# {
#   "data": {
#     "products": {
#       "complexity": 11,
#       "request_id": "5d3f0cd984697db73bc5cb8e",
#       "data": {
#         "edges": []
#       }
#     }
#   }
# }

endpoint = 'https://public-api.shiphero.com/graphql'

headers = {"Authorization" : "Bearer " + CONFIG['access_token']}

#-----------------------------------------------------------------------------#
# Spiking
#-----------------------------------------------------------------------------#

# Test 1 A: Using the gql library to make the query
# This one does not work

# Traceback (most recent call last):
#   File "<stdin>", line 1, in <module>
#   File "spikes/test1.py", line 110, in test_gql
#     return client.execute(query)
#   File "/opt/code/tap-shiphero-gql/env/lib/python3.5/site-packages/gql/client.py", line 48, in execute
#     self.validate(document)
#   File "/opt/code/tap-shiphero-gql/env/lib/python3.5/site-packages/gql/client.py", line 42, in validate
#     validation_errors = validate(self.schema, document)
#   File "/opt/code/tap-shiphero-gql/env/lib/python3.5/site-packages/graphql/validation/validation.py", line 29, in validate
#     return visit_using_rules(schema, type_info, ast, rules)
#   File "/opt/code/tap-shiphero-gql/env/lib/python3.5/site-packages/graphql/validation/validation.py", line 36, in visit_using_rules
#     visit(ast, TypeInfoVisitor(type_info, ParallelVisitor(visitors)))
#   File "/opt/code/tap-shiphero-gql/env/lib/python3.5/site-packages/graphql/language/visitor.py", line 119, in visit
#     assert isinstance(node, ast.Node), "Invalid AST Node: " + repr(node)
# AssertionError: Invalid AST Node: 'query {\n    products(analyze : true) {\n        complexity\n        request_id\n        data(first: 10) {\n            edges {\n                node {\n                    id\n
#                     sku\n                    name\n                    warehouse_products {\n                        id\n                        warehouse_id\n                        on_hand\n                    
# }\n                }\n            }\n        }\n    }\n}'


def test_gql():

    # Initial Questions

    # How does this get the api token?
    # - pass it into the `RequestsHTTPTransport` constructor as a kwarg
    #   because that gets passed to requests.post()

    a_so_called_transport = RequestsHTTPTransport(url=endpoint,
                                                  use_json=True,
                                                  headers=headers)

    client = Client(transport=a_so_called_transport,
                    fetch_schema_from_transport=True)
    return client.execute(query)


# Test 1 B: Using the graphqlclient to make a query
def test_graphqlclient():

    # Initial Questions

    # How does this get the api token?
    # - Use the client's `inject_token()`

    client = graphqlclient.GraphQLClient(endpoint)

    # inject_token, by default, wants a value to complete the header for
    # "Authorization", so we have to give it the "Bearer <token>" part
    client.inject_token("Bearer " + CONFIG['access_token'])

    return client.execute(query)

# Test 1 C: Using the sgqlc library to make a query
def test_sgqlc():
    # I didn't get around to this since I had to use 3.6
    pass

# Test 1 D: Using requests to make a query
def test_requests():

    result = requests.post(endpoint,
                           json={'query': query},
                           headers=headers)
    result.raise_for_status()
    #result = result.json()

    return result

