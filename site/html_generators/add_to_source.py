import json
import pprint
import yaml
import click
import io
from typing import List, Any
from datetime import date
from .constants import LIST_SOURCES
from .generate_list import Source

from pydantic.error_wrappers import ValidationError as PydanticValidationError

from prompt_toolkit import prompt
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit.document import Document

list_template = (
    '''{
  "cc": false,
  "database": [
    {
      "mal": "MAL ID HERE"
    }
  ],
  "date": "'''
    + str(date.today())
    + """",
  "duration": 3,
  "episodes": 1,
  "extra_info": null,
  "name": "TITLE HERE",
  "streaming": [
    {
      "youtube": "d1lmCdabZws"
    }
  ],
  "tags": [
    "Anthology",
    "Arthouse",
    "Commercial",
    "Film",
    "Music Video",
    "Series"
  ]
}"""
)


class SourceValidator(Validator):
    def validate(self, document: Document) -> None:
        text = document.text
        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            raise ValidationError(message=str(e))
        try:
            Source.parse_obj(data)
        except PydanticValidationError as pe:
            raise ValidationError(message=str(pe))


def prompt_source() -> Source:
    text = prompt(
        "New Source:\n",
        default=list_template,
        validator=SourceValidator(),
        multiline=True,
    )
    source_obj = Source.parse_obj(json.loads(text))

    pprint.pprint(source_obj)
    return source_obj


def add_source_to_file() -> None:
    with open(LIST_SOURCES) as yaml_src:
        sources_raw: List[Any] = yaml.load(yaml_src, Loader=yaml.FullLoader)

    obj = prompt_source()
    click.echo(f"Source item count: {len(sources_raw)}")
    index = -1
    while index < 0:
        itxt: int = click.prompt("Insert at index: ", type=int)
        if itxt > 0 and itxt < len(sources_raw):
            index = itxt

    sources_raw.insert(index, obj.dict())

    dataf = io.StringIO()
    yaml.dump(sources_raw, dataf)
    with open(LIST_SOURCES, "w") as yaml_dump:
        yaml_dump.write(dataf.getvalue())
