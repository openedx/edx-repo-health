"""
GraphQL Queries for Github API v4
"""

FETCH_BUILD_CHECK_RUNS = """
query fetch_repository_languages($repository_id: ID!) {
  node(id: $repository_id) {
    ... on Repository {
      defaultBranchRef {
        target {
          ... on Commit {
            history(first: 1) {
              edges {
                node {
                  message
                  checkSuites(first: 10) {
                    edges {
                      node {
                        checkRuns(first: 10) {
                          edges {
                            node {
                              name
                              startedAt
                              completedAt
                            }
                          }
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
"""
