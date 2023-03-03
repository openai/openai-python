## Contributor’s Guide
openai is a community that lives on its volunteers. You can contribute in many ways, code, documentation, tests, features, bug fixes, etc.


## Steps required for code patch
1. Fork the repository on GitHub.
2. Run tests, refer section for installing test dependencies.
	1. cd ```openai-python ```
	2. run ```pytest```
3. If tests do not run sucessfully, please investigate further. If you’re unable to resolve, raise a issue.
4. Write tests that demonstrate your bug or feature. Ensure that they fail.
5. Make your change.
6. Run the entire test suite again, confirming that all tests pass including the ones you just added.
7. Send a GitHub Pull Request to the repository’s main branch. 


## Install test dependencies
1. pytest
2. pytest-mock