import json
import pytest
from langchain.document_loaders import JSONLoader

# Path to your JSON file
file_path = '../../../raw_data/arm_template/ARMTemplateForFactory.json'

def test_jsonloader():
    file_path = '../../../raw_data/arm_template/ARMTemplateForFactory.json'

    # Initialize JSONLoaders
    loader_parameters = JSONLoader(file_path, '.parameters', text_content=False)
    loader_variables = JSONLoader(file_path, '.variables', text_content=False)
    loader_resources = JSONLoader(file_path, '.resources[]', text_content=False)

    # Load data
    data_parameters = loader_parameters.load()
    data_variables = loader_variables.load()
    data_resources = loader_resources.load()

    # Assert that the page_content of the first Document in each list is not empty
    assert data_parameters[0].page_content != {}
    assert data_variables[0].page_content != {}
    assert data_resources[0].page_content != {}

    # Compare size of 'resources' in data_resources with the size in the original JSON file
    with open(file_path) as f:
        json_data = json.load(f)
        assert len(data_resources) == len(json_data["resources"])
