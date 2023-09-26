# berlayar.ai
Hire your own team of generative agents for marketing and software development, all you gotta do is prompt. Find your niche and build an audience, turn an idea into a feature for iteration – anytime, anywhere in the world.

## Meet Your Round-the-Clock Team

* Arthur: a tireless librarian and researcher who will build up knowledge and market intelligence for easy retrieval
* Bertrand: go from prompt-to-publish
* Kay: prompt-to-feature
* Ching Shih: router and orchestrator


## Instalation

### Update env file from azure key vault

- clone the project branch refactor_env_to_config
- set your python path `export PYTHONPATH="${PYTHONPATH}:/path/to/berlayar"`
- `pip install pytest`
- run the test to make sure everything works fine and all necessary plug in has been installed
- `python -m pytest tests/integration/functional_config.py`
- `python update_env.py`
- env file with current value from azure key vault will be generated 😊
