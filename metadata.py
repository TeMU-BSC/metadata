from typing import List, Union, Dict, Tuple
from pathlib import Path
import json


class GlobalInformation:
    def __init__(self, used_attributes: Union[Dict, None]):
        self.used_attributes = used_attributes

    def load_from_disk(self, path: Path):
        assert self.used_attributes is None
        with path.open('r') as f:
            self.used_attributes = json.loads(f.read())

    def write_to_disk(self, path: Path):
        assert self.used_attributes is not None
        with path.open('w') as f:
            f.write(json.dumps(self.used_attributes))

    def init_dict(self):
        assert self.used_attributes is None
        self.used_attributes = {}


class Component:
    def __init__(self, g: GlobalInformation):
        assert g.used_attributes is not None
        self.g = g

    def _stringify_attribute(self, attribute_name: str) -> Tuple[str, str, str]:
        class_name = self.__class__.__name__
        attribute_value = self. __getattribute__(attribute_name)
        return class_name, attribute_name, attribute_value

    def _add_global_attributes(self, attribute_names: List[str]):
        class_name = self.__class__.__name__
        for attribute_name in attribute_names:
            attribute_value = self.__getattribute__(attribute_name)
            if class_name not in self.g.used_attributes:
                self.g.used_attributes[class_name] = {}
            if attribute_name not in self.g.used_attributes[class_name]:
                self.g.used_attributes[class_name][attribute_name] = []
            if attribute_value not in self.g.used_attributes[class_name][attribute_name]:
                self.g.used_attributes[class_name][attribute_name].append(attribute_value)

    def get_global_values(self, attribute_name: str):
        class_name = self.__class__.__name__
        global_attribute_values = []
        if class_name in self.g.used_attributes and attribute_name in self.g.used_attributes[class_name]:
            global_attribute_values = self.g.used_attributes[class_name][attribute_name]
        return global_attribute_values

    def _check_fields(self):
        """
        Checks whether the attributes are correct (if possible), otherwise throws an exception
        :return:
        """
        raise NotImplementedError()


class Action(Component):
    def __init__(self, name: str, src: str, tgt: str, script: Union[Path, None], order: int, g: GlobalInformation):
        """
        Processing action applied to a given corpus version
        :param name: Name of the action (eg. 'tokenization'). It should be a name as standard as possible.
        :param src:
        :param tgt:
        :param script:
        :param order:
        """
        super().__init__(g)
        self.name = name
        self.src = src
        self.tgt = tgt
        self.script = script
        self.order = order
        self._check_fields()
        self._check_fields()
        self._add_global_attributes(['name', 'src', 'tgt', 'script', 'order'])

    def _check_fields(self):
        assert len(self.name) > 0
        assert self.name.lower() == self.name
        assert len(self.src) > 0
        assert self.src.lower() == self.src
        assert len(self.tgt) > 0
        assert self.tgt.lower() == self.tgt
        assert self.script is not None or self.order == 0
        assert (self.script.exists() and self.script.is_file() and not self.script.is_absolute()) or self.script is None
        assert self.order >= 0


class CorpusVersion(Component):
    def __init__(self, date: str, prev: str, path: Path, provider: str, lang: str, parallel: str, encoding: str,
                 format_: str, released: Union[str, None], actions: List[Action], g: GlobalInformation):
        super().__init__(g)
        self.date = date
        self.prev = prev
        self.path = path
        self.provider = provider
        self.lang = lang
        self.parallel = parallel
        self.encoding = encoding
        self.format = format_
        self.released = released
        self.actions = actions
        self._check_fields()
        self._add_global_attributes(['date', 'prev', 'path', 'provider', 'lang', 'parallel', 'encoding', 'format',
                                     'released', 'actions'])

    def _check_fields(self):
        assert self.path.exists() and self.path.is_file() and not self.path.is_absolute()


class Corpus(Component):
    def __init__(self, dirname: str, pretty_name: str, corpus_versions: List[CorpusVersion], g: GlobalInformation):
        super().__init__(g)
        self.dirname = dirname
        self.pretty_name = pretty_name
        self.corpus_versions = corpus_versions
        self._check_fields()
        self._add_global_attributes(['dirname', 'pretty_name', 'corpus_versions'])

    def _check_fields(self):
        assert len(self.dirname) > 0
        assert self.dirname.lower() == self.dirname
        assert len(self.pretty_name) > 0
        assert len(self.corpus_versions) > 0









