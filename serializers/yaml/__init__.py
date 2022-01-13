from serializers.serializer import Serializer
import yaml


class YamlSerializer(Serializer):
    def serialize(self, dict: dict, **kwargs) -> str:
        return yaml.dump(dict, sort_keys=False)

    def deserialize(self, str: str, **kwargs) -> dict:
        dict = yaml.safe_load(str)
        dict.update(kwargs)
        return dict
