"""Handle configuration file related stuff."""

from json import loads, JSONDecodeError
import logging as loggr
from typing import Optional
from pathlib import Path
from jsonschema import Draft6Validator, SchemaError, ValidationError, validate


log = loggr.getLogger('cogsworth')


def open_file(filepath: str) -> Optional[str]:
    """Open file and read content.

    :param filepath: ``str`` path to file.
    :returns: ``str`` or ``None``.
    """
    file = Path(filepath)

    if not file.exists() or not file.is_file():
        log.error(f'Could not open file "{file}"'
                  + ', file does not exist.')
        return None

    with file.open('r') as fh:
        content = fh.read()
        return content

    return None


def open_json(filepath: str) -> Optional[dict]:
    """Open file and parse as JSON.

    :param filepath: ``str`` path to file.
    :returns: ``str`` or ``None``.
    """
    content = open_file(filepath)

    try:
        return loads(content)  # if valid json, return it
    except JSONDecodeError as err:
        log.warning(f'Invalid json for "{filepath}": {err}')
        return None


def validate_json(json: dict, schema: dict) -> bool:
    """Validate json against schema.

    :param json: ``dict`` json to be verified.
    :param schema: ``dict`` json schema draft 6.
    :returns: ``bool`` json valid to schema.
    """
    try:
        Draft6Validator.check_schema(schema)
    except SchemaError as err:
        log.debug(f'Schema does not conform to json schema draft 6: {err}')
        return False

    try:
        validate(instance=json, schema=schema)
    except ValidationError as err:
        log.debug(f'JSON does not conform to schema: {err}')
        return False

    return True


def load_config(config_path: str, schema_path: str) -> Optional[dict]:
    """Load configuration file, schema file and validate configuration.

    :param config_path: ``dict`` path to config file.
    :param schema_path: ``dict`` path to schema file.
    :returns: ``bool`` json valid to schema.
    """
    if (config := open_json(config_path)) is None:
        raise ValidationError(
            f'Could not load configuration file "{config_path}".')

    if (schema := open_json(schema_path)) is None:
        raise ValidationError(f'Could not open schema file "{schema_path}".')

    if not validate_json(config, schema):
        raise ValidationError(f'Configuration does not conform to schema.')

    return config
